# %% Import libraries
import os
from dotenv import load_dotenv
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter,MarkdownHeaderTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct
from openai import OpenAI
from uuid import uuid4

# %% Load enviroment keys
load_dotenv(override=True)
qdrant_url = os.environ.get("QDRANT_URL")
qdrant_api_key = os.environ.get("QDRANT_API_KEY")
openai_api_key = os.environ.get("OPENAI_API_KEY")

# %% Load files
policies_path = Path("policies")

headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2")
]

markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on,
    strip_headers=False
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
    # separators=["\n\n", "\n", ".", " "]
)

all_docs = []

for file in policies_path.glob("*.md"):
    file_content = file.read_text(encoding="utf-8")
    md_header_splits = markdown_splitter.split_text(file_content)
    splits = text_splitter.split_documents(md_header_splits)
    all_docs.extend(splits)


# %% Create vector db
collection_name = "Chatbot_Support_Customer"

qdrant_client = QdrantClient(
    url=qdrant_url,
    api_key=qdrant_api_key
)

# qdrant_client.create_collection(
#     collection_name=collection_name,
#     vectors_config={"dense": VectorParams(size=1536, distance=Distance.COSINE)}
# )

# %% Embedding documents and create payload
client_openai = OpenAI(api_key=openai_api_key)
MODEL_NAME = "text-embedding-3-small"

texts = [doc.page_content for doc in all_docs]
payloads = [
    {"page_content": doc.page_content, **doc.metadata} for doc in all_docs
]

def get_embeddings(texts, model=MODEL_NAME):
    response = client_openai.embeddings.create(
        input=texts,
        model=model
    )
    return [item.embedding for item in response.data]

vectors = get_embeddings(texts)

# %% Insert to DB
points = []

for idx, (vector,payload) in enumerate(zip(vectors, payloads)):
    points.append(
        PointStruct(
            id=str(uuid4()),
            vector={"dense":vector},
            payload=payload
        )
    )

batch_size = 100
total_points = len(points)

for i in range(0, total_points, batch_size):
  batch_points = points[i : i + batch_size]

  qdrant_client.upsert(
      collection_name=collection_name,
      wait=True,
      points=batch_points,
      timeout=60,
  )
# %%
