import os
from pathlib import Path

import chromadb
from openai import OpenAI

from src.vector_store.vector_store import load_books


CHROMA_DB_PATH = Path(__file__).parent.parent / "chrom_db"
COLLECTION_NAME = "books_collection"
EMBEDDING_MODEL = "text-embedding-3-small"


def build_book_text(book: dict) -> str:
    title = book["title"]
    short_summary = book["short_summary"]
    themes = ", ".join(book["themes"])
    genre = ", ".join(book["genre"])

    return (
        f"Title: {title}\n"
        f"Short Summary: {short_summary}\n"
        f"Themes: {themes}\n"
        f"Genre: {genre}"
    )


def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")
    return OpenAI(api_key=api_key)


def generate_embedding(client: OpenAI, text: str) -> list[float]:
    response = client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


def create_or_get_collection():
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    collection = chroma_client.get_or_create_collection(name=COLLECTION_NAME)
    return collection


def index_books():
    books = load_books()
    client = get_openai_client()
    collection = create_or_get_collection()

    existing_items = collection.get()
    existing_ids = existing_items.get("ids", [])

    if len(existing_ids) > 0:
        print(f"Collection already has {len(existing_ids)} items. Deleting them first.")
        collection.delete(ids=existing_ids)

    ids = []
    documents = []
    metadatas = []
    embeddings = []

    for book in books:
        book_text = build_book_text(book)
        embedding = generate_embedding(client, book_text)

        ids.append(book["id"])
        documents.append(book_text)
        metadatas.append({
            "title": book["title"],
            "author": book["author"],
            "year": str(book["year"]),
            "genre": ", ".join(book["genre"]),
        })
        embeddings.append(embedding)

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings
    )

    print(f"Indexed {len(books)} books into ChromaDB collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    index_books()