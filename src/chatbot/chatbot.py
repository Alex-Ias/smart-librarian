import json

from src.chatbot.tools import get_summary_by_title
from src.vector_store.retriever import retrieve_books
from src.vector_store.utils import get_openai_client

MODEL_NAME = "gpt-4.1-mini"

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

SYSTEM_PROMPT = (
    "You are an AI librarian. "
    "Use only the retrieved books as context. "
    "Do not use outside knowledge. "
    "Do not ask follow-up questions. "
    "Do not offer to provide more details later. "
    "Do not say things like 'Would you like a more detailed summary?' or "
    "'I can give you more details if you want'. "
    "If the user asks for a recommendation or asks about a book, respond directly. "
    "If there is a suitable match, choose exactly one book, explain briefly why it matches, "
    "then call the tool get_summary_by_title with the exact title of that book. "
    "After receiving the tool result, provide the final answer in the same response. "
    "The final answer must contain: "
    "1. the recommended book title and author, "
    "2. one short reason why it matches, "
    "3. the full summary returned by the tool. "
    "Do not ask the user anything at the end. "
    "Do not add optional follow-up suggestions. "
    "If no suitable match exists, say clearly: "
    "'I could not find a relevant recommendation based on your request.'"
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
            parts.append(f"Themes: {book['themes']}")

        if book.get("short_summary"):
            parts.append(f"Short Summary: {book['short_summary']}")

        lines.append("\n".join(parts))

    return "\n\n".join(lines)


def execute_tool(function_name: str, arguments: dict) -> str:
    if function_name == "get_summary_by_title":
        title = arguments.get("title", "").strip()

        if not title:
            return "No title was provided to the tool."

        summary = get_summary_by_title(title)
        return summary or f"No summary found for '{title}'."

    return f"Unsupported tool: {function_name}"


def ask_chatbot(user_query: str, n_results: int = 3) -> dict:
    client = get_openai_client()

    retrieved_books = retrieve_books(user_query, n_results=n_results)
    context = build_context(retrieved_books)

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT,
        },
        {
            "role": "user",
            "content": (
                f"User request: {user_query}\n\n"
                f"Retrieved books:\n{context}"
            ),
        },
    ]

    first_response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=TOOLS,
        tool_choice="auto",
    )

    assistant_message = first_response.choices[0].message
    recommended_title = None

    if not assistant_message.tool_calls:
        return {
            "text": assistant_message.content or "No response generated.",
            "title": None,
        }

    messages.append(assistant_message)

    for tool_call in assistant_message.tool_calls:
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)

        if function_name == "get_summary_by_title":
            recommended_title = arguments.get("title")

        tool_result = execute_tool(function_name, arguments)

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result,
            }
        )

    final_response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
    )

    return {
        "text": final_response.choices[0].message.content or "No final response generated.",
        "title": recommended_title,
    }