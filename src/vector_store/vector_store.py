import json
from pathlib import Path


def load_books():
    base_path = Path(__file__).parent.parent
    file_path = base_path / "books" / "books.json"

    with open(file_path, "r", encoding="utf-8") as f:
        books = json.load(f)

    return books


if __name__ == "__main__":
    books = load_books()
    print(f"Loaded {len(books)} books")
    print(books[0]["title"])