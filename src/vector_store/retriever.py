from src.vector_store.utils import  (
    create_or_get_collection,
    get_openai_client,
    generate_embedding,
  
)

def search_books(query: str, n_results: int = 3):
    client = get_openai_client()
    collection = create_or_get_collection()

    query_embedding = generate_embedding(client, query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results


if __name__ == "__main__":
    user_query = "I want a book about freedom and control."

    results = search_books(user_query, n_results=3)

    print("\nTop results:\n")

    for i, metadata in enumerate(results["metadatas"][0], start=1):
        print(f"{i}. {metadata['title']} by {metadata['author']}")