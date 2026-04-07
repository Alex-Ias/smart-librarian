from pathlib import Path
import base64

from src.vector_store.utils import get_openai_client

IMAGE_MODEL = "gpt-image-1"


def build_image_prompt(title: str) -> str:
    return (
        f"Create a cinematic, highly detailed book cover illustration for the novel '{title}'. "
        f"No text, no title, no typography. "
        f"Focus on atmosphere, mood, and key themes of the story. "
        f"Professional, artistic, dramatic lighting."
    )


def generate_book_image(title: str, output_file: str = "artifacts/book.png") -> str:
    client = get_openai_client()

    prompt = build_image_prompt(title)

    result = client.images.generate(
        model=IMAGE_MODEL,
        prompt=prompt,
        size="1024x1024",
    )

    image_bytes = base64.b64decode(result.data[0].b64_json)

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "wb") as f:
        f.write(image_bytes)

    return str(output_path)