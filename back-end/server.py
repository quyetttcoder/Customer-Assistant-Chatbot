from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage, AIMessageChunk
from langgraph.types import Command
from uuid import uuid4
import traceback

from graph import chatbot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

async def run_graph(ws: WebSocket, graph_input, config) -> bool:
    "Run graph and return. True if pending interrupt"
    streamed = False
    async for mode, data in chatbot.astream(
        graph_input, config=config, stream_mode=["messages", "updates"]
    ):
        print("STREAM:", mode, type(data[0]).__name__ if mode == "messages" else list(data.keys()))
        if mode == "messages":
            chunk, meta = data
            print(f"Chunk: {chunk}\nMeta: {meta}")
            if (
                meta.get("langgraph_node") == "chat_node"
                and isinstance(chunk, AIMessageChunk)
                and chunk.content
            ):
                streamed = True
                await ws.send_json({"type": "token", "content": chunk.content})

        elif mode == "updates":
            if "__interrupt__" in data:
                intr = data["__interrupt__"][0]
                print("Interrupt:", intr)
                await ws.send_json({"type": "interrupt", "payload": intr.value})
                return True

            node_out = data.get("chat_node")
            print(f"Node out: {node_out}")
            if node_out:
                msg = node_out["messages"][-1]
                print(f"Node out msg: {msg}")
                if not streamed and msg.content and not msg.tool_calls:
                    await ws.send_json({"type": "token", "content": msg.content})
                streamed = False
    await ws.send_json({"type": "done"})
    return False

@app.websocket("/ws")
async def chat_ws(ws: WebSocket):
    await ws.accept()
    thread_id = str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    waiting_interrupt = False

    try:
        while True:
            msg = await ws.receive_json()
            print("RECV:", msg)
            if msg["type"] == "user_message":
                if waiting_interrupt:
                    await ws.send_json({"type": "error", "message": "Please confirm the previous request!"})
                    continue
                graph_input = {"messages": [HumanMessage(content=msg["content"])]}
            elif msg["type"] == "resume":
                if not waiting_interrupt:
                    continue
                graph_input = (Command(resume={"approved": msg["approved"]}))
            else:
                continue
            try:
                waiting_interrupt = await run_graph(ws, graph_input, config)
            except Exception as e:
                traceback.print_exc()
                waiting_interrupt = False
                await ws.send_json({"type": "error", "message": str(e)})
    except WebSocketDisconnect:
        pass
    finally:
        chatbot.checkpointer.delete_thread(thread_id)