import base64
from pathlib import Path

from openai import BadRequestError
from src.vector_store.utils import get_openai_client

IMAGE_MODEL = "gpt-image-1"


def build_image_prompt(title: str) -> str:
    return (
        f"Create a cinematic, highly detailed illustrated book-cover-style artwork inspired by the book titled '{title}'. "
        f"Keep the image fully safe and non-explicit. No nudity, no sexual content, no intimate acts, no minors, and no fetish imagery. "
        f"No text, no title, no letters, no typography, no watermark. "
        f"Polished and visually striking, suitable for a premium modern book cover. "
        f"Focus on strong atmosphere, emotional storytelling, dramatic lighting, rich textures, and memorable composition. "
        f"Prefer symbolic elements, environments, objects, architecture, weather, color, and abstract motifs over close-up human bodies. "
        f"Use elegant color harmony, depth, contrast, and professional digital painting quality. "
        f"Avoid clutter, low detail, distorted anatomy, blurry areas, cheap stock-photo look, or generic fantasy poster style."
    )


def build_safe_fallback_prompt() -> str:
    return (
        "Create a safe, symbolic, non-explicit illustrated book-cover-style image. "
        "No people, no bodies, no nudity, no sexual content, no intimate acts, no minors, and no violence. "
        "No text, no letters, no typography, no watermark. "
        "Use atmospheric lighting, abstract literary motifs, elegant color harmony, rich textures, and premium digital painting quality. "
        "Prefer bookshelves, paper, keys, forests, city lights, stars, waves, fog, architecture, and geometric symbolism."
    )


def is_safety_rejection(error: BadRequestError) -> bool:
    message = str(error).lower()
    return "moderation_blocked" in message or "safety system" in message


def generate_book_image(title: str, output_file: str = "artifacts/book.png") -> str:
    client = get_openai_client()

    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    prompts = [build_image_prompt(title), build_safe_fallback_prompt()]

    for index, prompt in enumerate(prompts):
        try:
            result = client.images.generate(
                model=IMAGE_MODEL,
                prompt=prompt,
                size="1024x1024",
            )
            image_bytes = base64.b64decode(result.data[0].b64_json)

            with open(output_path, "wb") as f:
                f.write(image_bytes)

            return str(output_path)
        except BadRequestError as exc:
            if index == 0 and is_safety_rejection(exc):
                continue
            raise

    raise RuntimeError("Image generation failed after retrying with a safe fallback prompt.")
