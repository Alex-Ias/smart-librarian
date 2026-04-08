from pathlib import Path
import base64

from src.vector_store.utils import get_openai_client

IMAGE_MODEL = "gpt-image-1"

def build_image_prompt(title: str, summary: str | None = None, style: str = "cinematic fantasy") -> str:
    prompt = (
        f"Create a highly detailed vertical book-cover illustration inspired by '{title}', "
        f"in a {style} style. "
        f"No text, no typography, no watermark. "
        f"Professional composition, dramatic focal point, atmospheric background, rich textures, volumetric lighting, "
        f"strong storytelling, elegant color palette, premium publishing aesthetic. "
        f"Avoid clutter, low detail, awkward anatomy, extra limbs, blurry faces, and generic poster composition. "
    )
    if summary:
        prompt += f"Use this story context for visual inspiration: {summary}. "
    return prompt


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