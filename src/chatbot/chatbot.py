import difflib
import json
import logging
import re
from collections import Counter
from functools import lru_cache

from src.chatbot.tools import get_summary_by_title
from src.vector_store.retriever import retrieve_books
from src.vector_store.utils import get_openai_client
from src.vector_store.vector_store import load_books

MODEL_NAME = "gpt-4o-mini"
NO_MATCH_RESPONSE = "I could not find a relevant recommendation based on your request."
QUERY_TOKEN_PATTERN = re.compile(r"[0-9A-Za-zÀ-ÖØ-öø-ÿ']+")

logger = logging.getLogger(__name__)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_summary_by_title",
            "description": "Return the full summary for an exact book title.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The exact title of the recommended book."
                    }
                },
                "required": ["title"]
            }
        }
    }
]

SELECTION_PROMPT = (
    "You are an AI librarian selecting one book recommendation. "
    "Use only the retrieved books as context. "
    "Do not use outside knowledge. "
    "Do not ask follow-up questions. "
    "If the user request is unintelligible, random characters, or meaningless text, do not recommend any book. "
    "Never translate or modify the book title. "
    "Keep the title exactly as it appears in the retrieved data. "
    "If there is a suitable match, you MUST call the tool get_summary_by_title with the exact title before giving any recommendation. "
    "If no suitable match exists, do not call any tool and reply exactly with: "
    "'I could not find a relevant recommendation based on your request.' "
    "That exact sentence is the only exception to the same-language rule."
)

QUERY_VALIDATION_PROMPT = (
    "Decide whether the user's input is meaningful enough for a book recommendation search. "
    "Treat clear genres, moods, themes, subjects, book titles, and short descriptive words as meaningful. "
    "Treat random letters, gibberish, keyboard mashing, and unintelligible text as not meaningful. "
    "Examples of meaningful input: mystery, romance, thrilling, stoicism, python, dystopian politics. "
    "Examples of not meaningful input: asasasadaws, qwertyuiopasdf, zzzzxxyyqq. "
    "Reply with exactly one token: MEANINGFUL or NOT_MEANINGFUL."
)

FINAL_RESPONSE_PROMPT = (
    "You are an AI librarian writing the final answer. "
    "Use only the user request, the selected book details, and the provided tool summary. "
    "Do not use outside knowledge. "
    "Do not ask follow-up questions. "
    "Do not offer more details later. "
    "Always answer entirely in the same language as the user's request. "
    "Never mix languages in the final answer. "
    "Use natural, fluent, and idiomatic language. "
    "Use correct grammar in the user's language. "
    "Never translate or modify the book title. "
    "Keep the title exactly as provided. "
    "Write plain text only. "
    "Do not use markdown. "
    "Do not use bold, bullet points, headings, labels, or quotation marks around the title. "
    "Write exactly 2 short paragraphs. "
    "Paragraph 1: Recommend exactly one book and explain briefly why it matches the user request. "
    "Paragraph 2: Provide a faithful and complete translation of the provided tool summary if needed. "
    "The second paragraph must be based only on the provided tool summary, while preserving all of its meaning and detail."
)


def build_context(retrieved_books: list[dict]) -> str:
    if not retrieved_books:
        return "No relevant books were retrieved."

    lines = []

    for book in retrieved_books:
        parts = [
            f"Title: {book.get('title', 'Unknown')}",
            f"Author: {book.get('author', 'Unknown')}",
            f"Genre: {book.get('genre', 'Unknown')}",
            f"Year: {book.get('year', 'Unknown')}",
        ]

        if book.get("themes"):
            themes = book["themes"]
            if isinstance(themes, list):
                themes = ", ".join(themes)
            parts.append(f"Themes: {themes}")

        if book.get("short_summary"):
            parts.append(f"Short Summary: {book['short_summary']}")

        lines.append("\n".join(parts))

    return "\n\n".join(lines)


def normalize_text(value) -> str:
    if value is None:
        return ""

    return re.sub(r"\s+", " ", str(value)).strip()


def normalize_for_match(value: str) -> str:
    return normalize_text(value).casefold()


def extract_query_tokens(text: str) -> list[str]:
    return [
        normalize_for_match(token)
        for token in QUERY_TOKEN_PATTERN.findall(text)
        if normalize_text(token)
    ]


@lru_cache(maxsize=1)
def get_reference_terms() -> tuple[str, ...]:
    terms = set()

    for book in load_books():
        for field in ("title", "author", "short_summary", "full_summary"):
            value = normalize_text(book.get(field, ""))
            terms.update(
                normalize_for_match(token)
                for token in QUERY_TOKEN_PATTERN.findall(value)
                if len(normalize_text(token)) >= 3
            )

        for field in ("themes", "genre"):
            for item in book.get(field, []):
                value = normalize_text(item)
                terms.update(
                    normalize_for_match(token)
                    for token in QUERY_TOKEN_PATTERN.findall(value)
                    if len(normalize_text(token)) >= 3
                )

    return tuple(sorted(terms))


def get_single_token_candidate(user_query: str) -> str | None:
    tokens = [
        token
        for token in extract_query_tokens(user_query)
        if len(token) >= 3 and not token.isdigit()
    ]

    if len(tokens) != 1:
        return None

    return tokens[0]


def has_reference_match(token: str) -> bool:
    reference_terms = get_reference_terms()

    if token in reference_terms:
        return True

    return bool(difflib.get_close_matches(token, reference_terms, n=1, cutoff=0.88))


def has_strong_gibberish_pattern(token: str) -> bool:
    letters_only = "".join(char for char in token if char.isalpha())
    if len(letters_only) < 6:
        return False

    unique_ratio = len(set(letters_only)) / len(letters_only)
    vowels = sum(char in "aeiouyăâî" for char in letters_only)
    bigrams = [letters_only[index:index + 2] for index in range(len(letters_only) - 1)]
    trigrams = [letters_only[index:index + 3] for index in range(len(letters_only) - 2)]
    max_bigram_repeats = max(Counter(bigrams).values(), default=0)
    max_trigram_repeats = max(Counter(trigrams).values(), default=0)

    return (
        (len(letters_only) >= 8 and unique_ratio < 0.45)
        or max_trigram_repeats >= 3
        or (max_bigram_repeats >= 3 and unique_ratio < 0.55)
        or (len(letters_only) >= 8 and vowels == 0)
    )


def looks_like_suspicious_query(user_query: str) -> bool:
    token = get_single_token_candidate(user_query)
    if not token or len(token) < 6:
        return False

    return not has_reference_match(token)


def get_book_by_title(title: str, retrieved_books: list[dict]) -> dict | None:
    normalized_title = normalize_for_match(title)

    for book in retrieved_books:
        book_title = book.get("title")
        if book_title and normalize_for_match(book_title) == normalized_title:
            return book

    return None


def execute_tool(function_name: str, arguments: dict) -> str:
    if function_name == "get_summary_by_title":
        title = normalize_text(arguments.get("title", ""))

        if not title:
            raise ValueError("No title was provided to the tool.")

        summary = get_summary_by_title(title)
        if not summary or summary.startswith("No full summary found"):
            raise ValueError(f"No summary found for '{title}'.")

        return summary

    raise ValueError(f"Unsupported tool: {function_name}")


def parse_tool_arguments(raw_arguments: str) -> dict:
    try:
        arguments = json.loads(raw_arguments or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError("Tool arguments are not valid JSON.") from exc

    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a JSON object.")

    return arguments


def extract_title_from_response(response_text: str, retrieved_books: list[dict]) -> str | None:
    if not response_text:
        return None

    normalized_response = normalize_for_match(response_text)
    titles = [
        book.get("title")
        for book in retrieved_books
        if book.get("title")
    ]

    for title in sorted(titles, key=len, reverse=True):
        if normalize_for_match(title) in normalized_response:
            return title

    return None


def looks_like_no_match(response_text: str) -> bool:
    if not response_text:
        return False

    normalized = normalize_for_match(response_text)
    patterns = [
        normalize_for_match(NO_MATCH_RESPONSE),
        "could not find",
        "no suitable match",
        "nu am gasit",
        "nu pot gasi",
        "nu am g\u0103sit",
        "nu pot g\u0103si",
    ]
    return any(normalize_for_match(p) in normalized for p in patterns)


def build_selection_messages(user_query: str, context: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": SELECTION_PROMPT,
        },
        {
            "role": "user",
            "content": (
                f"User request: {user_query}\n\n"
                f"Retrieved books:\n{context}"
            ),
        },
    ]


def build_final_messages(user_query: str, selected_book: dict, tool_summary: str) -> list[dict]:
    return [
        {
            "role": "system",
            "content": FINAL_RESPONSE_PROMPT,
        },
        {
            "role": "user",
            "content": (
                f"User request: {user_query}\n\n"
                f"Selected book:\n{build_context([selected_book])}\n\n"
                f"Tool summary:\n{tool_summary}"
            ),
        },
    ]


def create_chat_completion(**kwargs):
    try:
        return get_openai_client().chat.completions.create(**kwargs)
    except Exception as exc:
        raise RuntimeError("OpenAI chat completion failed.") from exc


def is_meaningful_query(user_query: str) -> bool:
    if not looks_like_suspicious_query(user_query):
        return True

    token = get_single_token_candidate(user_query)

    try:
        response = create_chat_completion(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": QUERY_VALIDATION_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"User input: {normalize_text(user_query)}",
                },
            ],
        )
        verdict = normalize_for_match(response.choices[0].message.content or "")

        if "not_meaningful" in verdict:
            return False

        if "meaningful" in verdict:
            return True
    except RuntimeError:
        logger.exception("Query validation failed for input: %s", user_query)

    return not has_strong_gibberish_pattern(token or "")


def choose_recommended_title(assistant_text: str, assistant_tool_calls, retrieved_books: list[dict]) -> str | None:
    for tool_call in assistant_tool_calls or []:
        function_name = tool_call.function.name
        raw_arguments = tool_call.function.arguments

        if function_name != "get_summary_by_title":
            logger.warning("Ignoring unsupported tool call: %s", function_name)
            continue

        try:
            arguments = parse_tool_arguments(raw_arguments)
        except ValueError:
            logger.exception("Failed to parse tool arguments: %s", raw_arguments)
            continue

        candidate_title = arguments.get("title", "")
        matched_book = get_book_by_title(candidate_title, retrieved_books)

        if matched_book:
            return matched_book["title"]

        logger.warning("Tool called with title outside retrieved results: %s", candidate_title)

    return extract_title_from_response(assistant_text, retrieved_books)


def ask_chatbot(user_query: str, n_results: int = 3) -> dict:
    if not is_meaningful_query(user_query):
        return {
            "text": NO_MATCH_RESPONSE,
            "title": None,
        }

    retrieved_books = retrieve_books(user_query, n_results=n_results)
    if not retrieved_books:
        return {
            "text": NO_MATCH_RESPONSE,
            "title": None,
        }

    context = build_context(retrieved_books)
    selection_messages = build_selection_messages(user_query, context)

    first_response = create_chat_completion(
        model=MODEL_NAME,
        messages=selection_messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    assistant_message = first_response.choices[0].message
    assistant_text = assistant_message.content or ""
    recommended_title = choose_recommended_title(
        assistant_text,
        assistant_message.tool_calls,
        retrieved_books,
    )

    if not recommended_title:
        no_match_text = assistant_text if looks_like_no_match(assistant_text) else NO_MATCH_RESPONSE
        return {
            "text": no_match_text,
            "title": None,
        }

    selected_book = get_book_by_title(recommended_title, retrieved_books)
    if not selected_book:
        return {
            "text": NO_MATCH_RESPONSE,
            "title": None,
        }

    try:
        tool_summary = execute_tool(
            "get_summary_by_title",
            {"title": selected_book["title"]},
        )
    except ValueError:
        logger.exception("Tool execution failed for title: %s", selected_book["title"])
        return {
            "text": NO_MATCH_RESPONSE,
            "title": None,
        }

    final_response = create_chat_completion(
        model=MODEL_NAME,
        messages=build_final_messages(user_query, selected_book, tool_summary),
    )

    final_text = final_response.choices[0].message.content or "No final response generated."
    final_text = normalize_text(final_text) or NO_MATCH_RESPONSE

    if looks_like_no_match(final_text):
        return {
            "text": NO_MATCH_RESPONSE,
            "title": None,
        }

    return {
        "text": final_text,
        "title": selected_book["title"],
    }