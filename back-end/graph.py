import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Optional
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI

from query_db import get_data
from retrieve_kb import retrieve_docs


load_dotenv()
openai_api_key = os.environ.get("OPENAI_API_KEY")

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_accepted_escalation: Optional[bool]


llm = ChatOpenAI(
    api_key=openai_api_key,
    model="gpt-4.1-mini",
    streaming=True
)

@tool
def escalation(message: str):
    """Transfer to a human agent when the user explicitly requests it,
    when they repeatedly complain about ineffective answers, or after three
    unauthorized data access attempts.
    `message`: a short, empathetic statement in the user's language that
    acknowledges the situation and asks the user to confirm the transfer to a human agent."""
    decision = interrupt({
        "type": "approval",
        "message": message,
        "options": ["yes", "no"],
    })

    if decision["approved"] == "yes":
        return "User approved the transfer. Tell them they are being connected to a human agent."
    return "User declined the transfer. Apologize briefly and keep supporting them."


tools = [get_data, retrieve_docs, escalation]
llm_with_tools = llm.bind_tools(tools, parallel_tool_calls=False)

tool_node = ToolNode(tools)

async def chat_node(state: ChatState):
    instruction_prompt = """You are an expert Customer Support AI Assistant. Your goal is to provide accurate, helpful, and efficient support to customers.

### Tone and Style
- **Professional & Friendly:** Maintain a polite, empathetic, and welcoming tone while upholding high standards of professionalism.
- **Clear & Concise:** Get straight to the point. Avoid unnecessary verbosity, filler words, or overly long explanations. Give precise answers immediately.

### Available Tools
You have access to the following tools to gather data and policy information needed for your responses:
1. **`get_data`**: Use this tool to analyze and query structured data from the customer database (e.g., account details, order status, transaction history).
2. **`retrieve_docs`**: Use this tool to query relevant official policy documents, terms, and guidelines (e.g., refund policies, shipping rules, warranty terms).
3. **`escalation`**: Use when the customer explicitly asks for a human, or keeps complaining that your answers don't help. Write the `message` argument as a short empathetic sentence asking if they want to be transferred.

### Operating Guidelines
1. **Fact-Check via Tools:** Always rely on data retrieved from `get_data` and `retrieve_docs` to ensure accuracy. Do not guess or make up information.
2. **Step-by-Step Execution:** 
   - Identify what customer information or policy details are missing.
   - Call the appropriate tool(s) to fetch the necessary data.
   - Synthesize the findings into a short, clear, and direct response for the customer.
3. **No Technical Jargon:** Never expose internal tool names, database schemas, or system mechanics to the customer. Translate technical findings into customer-friendly language.    
"""

    system_prompt = SystemMessage(content=instruction_prompt)
    messages = [
        system_prompt,
        *state["messages"]
    ]
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")
chatbot = graph.compile(checkpointer=InMemorySaver())