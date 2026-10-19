import asyncio, json, websockets

async def main():
    async with websockets.connect("ws://localhost:8000/ws/test1") as ws:
        await ws.send(json.dumps({"type": "user_message", "content": "I want to talk with staff"}))
        while True:
            ev = json.loads(await ws.recv())
            print(ev)
            if ev["type"] == "interrupt":
                await ws.send(json.dumps({"type": "resume", "approved": "yes"}))
            if ev["type"] in ("done", "error"):
                break

asyncio.run(main())