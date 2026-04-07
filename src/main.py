#!/usr/bin/env python3

from src.vector_store.retriever import retrieve_books

DEFAULT_QUERY = "I want a book about love and war, preferably set in the 20th century."
DEFAULT_RESULTS = 3


def main() -> None:
    books = retrieve_books(DEFAULT_QUERY, n_results=DEFAULT_RESULTS)

    print("\nTop results:\n")

    for i, book in enumerate(books, start=1):
        print(f"{i}. {book['title']} by {book['author']}")


if __name__ == "__main__":
    main()
