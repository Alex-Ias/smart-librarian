from src.vector_store.utils import (
    create_or_get_collection,
    get_openai_client,
    generate_embedding,
)


def retrieve_books(query: str, n_results: int = 3) -> list[dict]:
    client = get_openai_client()
    collection = create_or_get_collection()

    query_embedding = generate_embedding(client, query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    books = []

    for metadata in results["metadatas"][0]:
        books.append({
            "title": metadata["title"],
            "author": metadata["author"],
            "genre": metadata["genre"],
            "year": metadata["year"],
        })

    return books


if __name__ == "__main__":
    user_query = "I want a book about love and war, preferably set in the 20th century."

    books = retrieve_books(user_query, n_results=3)

    print("\nTop results:\n")

    for i, book in enumerate(books, start=1):
        print(f"{i}. {book['title']} by {book['author']}")