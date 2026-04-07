from src.vector_store.vector_store import load_books
from src.vector_store.utils import get_openai_client


def get_summary_by_title(title: str) -> str:
    if not title:
        return "No title provided."

    books = load_books()

    normalized_title = title.strip().lower()

    for book in books:
        book_title = book.get("title", "").strip().lower()

        if book_title == normalized_title:
            return book.get("full_summary", "No summary available for this book.")

    return f"No full summary found for title: {title}"


def is_safe(text: str) -> bool:
    client = get_openai_client()

    response = client.moderations.create(
        model="omni-moderation-latest",
        input=text
    )

    return not response.results[0].flagged