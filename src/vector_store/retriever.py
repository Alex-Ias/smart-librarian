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
