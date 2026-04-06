import os
from pathlib import Path
from typing import List

import chromadb
from openai import OpenAI

CHROMA_DB_PATH = Path(__file__).parent.parent / "chrom_db"
COLLECTION_NAME = "books_collection"
EMBEDDING_MODEL = "text-embedding-3-small"


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")
    return OpenAI(api_key=api_key)


def generate_embedding(client: OpenAI, text: str) -> List[float]:
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


def create_or_get_collection():
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    return collection