# %% Import all necessary libraries
import os
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from langchain_core.tools import tool

# %% Load environment keys
load_dotenv(override=True)

openai_api_key = os.environ.get("OPENAI_API_KEY")
qdrant_url = os.environ.get("QDRANT_URL")
qdrant_key = os.environ.get("QDRANT_API_KEY")

# %% Define retriver
collection_name = "Chatbot_Support_Customer"
embedding_model = "text-embedding-3-small"
qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_key)
openai_client = OpenAI(api_key=openai_api_key)

@tool
def retrieve_docs(query: str):
    """
    Retrieve relevant e-commerce policy documents and information based on the user's query. 
    Use this tool when you need to find details about payment policies, privacy policies, 
    return and refund policies, shipping policies.
    """
    response = qdrant_client.query_points(
        collection_name=collection_name,
        query= openai_client.embeddings.create(
            input=[query],
            model=embedding_model
        ).data[0].embedding,
        using="dense",
        limit=7
    )
    retrieved_docs = "\n\n".join([p.payload["page_content"] for p in response.points])

    return retrieved_docs

