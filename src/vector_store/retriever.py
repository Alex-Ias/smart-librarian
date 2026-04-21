from src.vector_store.utils import (
    create_or_get_collection,
    get_openai_client,
    generate_embedding,
)
from src.vector_store.vector_store import load_books


def normalize_for_match(value: str) -> str:
    return " ".join(str(value).split()).strip().casefold()


def format_field(value, default: str = "Unknown") -> str:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)

    if value is None:
        return default

    text = str(value).strip()
    return text or default


def build_book_lookup() -> dict[str, dict]:
    return {
        normalize_for_match(book.get("title", "")): book
        for book in load_books()
        if book.get("title")
    }


def retrieve_books(query: str, n_results: int = 3) -> list[dict]:
    client = get_openai_client()
    collection = create_or_get_collection()
    book_lookup = build_book_lookup()

    query_embedding = generate_embedding(client, query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["metadatas"],
    )

    books = []
    metadata_rows = results.get("metadatas") or []

    if not metadata_rows:
        return books

    for metadata in metadata_rows[0]:
        metadata = metadata or {}
        fallback_book = book_lookup.get(
            normalize_for_match(metadata.get("title", "")),
            {},
        )

        books.append({
            "title": format_field(metadata.get("title") or fallback_book.get("title")),
            "author": format_field(metadata.get("author") or fallback_book.get("author")),
            "genre": format_field(metadata.get("genre") or fallback_book.get("genre")),
            "year": format_field(metadata.get("year") or fallback_book.get("year")),
            "themes": format_field(metadata.get("themes") or fallback_book.get("themes"), default=""),
            "short_summary": format_field(
                metadata.get("short_summary") or fallback_book.get("short_summary"),
                default="",
            ),
        })

    return books
