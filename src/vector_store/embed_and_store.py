from src.vector_store.vector_store import load_books
from src.vector_store.utils import (
    get_openai_client,
    create_or_get_collection,
    generate_embedding,
    COLLECTION_NAME,
)

# PT RUN:
# python -m src.vector_store.embed_and_store


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


def index_books() -> None:
    books = load_books()
    client = get_openai_client()
    collection = create_or_get_collection()

    ids = []
    documents = []
    metadatas = []
    embeddings = []

    for book in books:
        book_text = build_book_text(book)
        embedding = generate_embedding(client, book_text)

        ids.append(book["id"])
        documents.append(book_text)
        metadatas.append(
            {
                "title": book["title"],
                "author": book["author"],
                "year": str(book["year"]),
                "genre": ", ".join(book["genre"]),
                "themes": ", ".join(book["themes"]),
                "short_summary": book["short_summary"],
            }
        )
        embeddings.append(embedding)

    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"Indexed {len(books)} books into ChromaDB collection '{COLLECTION_NAME}'.")


def ensure_indexed() -> None:
    collection = create_or_get_collection()

    existing_items = collection.get()
    existing_ids = existing_items.get("ids", [])

    if existing_ids:
        print(
            f"Collection '{COLLECTION_NAME}' already initialized with {len(existing_ids)} items."
        )
        return

    print(f"Collection '{COLLECTION_NAME}' is empty. Indexing books...")
    index_books()


if __name__ == "__main__":
    ensure_indexed()
