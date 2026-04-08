import base64
import logging
import os
import re
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from src.api.schemas import AssistantRequest, AssistantResponse
from src.chatbot.chatbot import ask_chatbot
from src.chatbot.image_gen import generate_book_image
from src.chatbot.stt import transcribe_audio_file
from src.chatbot.tools import is_safe
from src.chatbot.tts import text_to_speech_bytes

logger = logging.getLogger(__name__)

APP_TITLE = "Smart Librarian API"
APP_VERSION = "1.0.0"
DEFAULT_ALLOWED_ORIGINS = "http://localhost:3000"
MAX_PROMPT_LENGTH = 1200

UNCLEAR_PROMPT_RESPONSE = (
    "I did not understand your request. Please ask clearly for a book, genre, mood, theme, or recommendation."
)
TOO_LONG_PROMPT_RESPONSE = (
    "Your message is too long. Please keep it shorter and focused on the kind of book you want."
)

MEANINGLESS_INPUTS = {"a", "ok", "test", "???", "...", "hi", "hello"}

app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", DEFAULT_ALLOWED_ORIGINS).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["System"])
async def health() -> dict:
    return {
        "status": "ok",
        "service": APP_TITLE.lower().replace(" ", "-"),
        "version": APP_VERSION,
    }


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def encode_bytes_to_base64(data: bytes) -> str:
    return base64.b64encode(data).decode("utf-8")


def encode_file_to_base64(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists() or not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    return encode_bytes_to_base64(path.read_bytes())


def is_meaningful_prompt(text: str) -> bool:
    cleaned = normalize_text(text)

    if len(cleaned) < 3:
        return False

    if cleaned.lower() in MEANINGLESS_INPUTS:
        return False

    compact = cleaned.replace(" ", "")
    if len(compact) > 2 and len(set(compact)) == 1:
        return False

    chunks = re.findall(r"[A-Za-zÀ-ÿ0-9]+", cleaned)
    if not chunks:
        return False

    total_alnum_length = sum(len(chunk) for chunk in chunks)
    return total_alnum_length >= 3


def build_unclear_response(
    *,
    user_message: str,
    transcribed_text: Optional[str],
) -> AssistantResponse:
    return AssistantResponse(
        user_message=user_message,
        transcribed_text=transcribed_text,
        response=UNCLEAR_PROMPT_RESPONSE,
        title=None,
        audio_generated=False,
        audio_base64=None,
        image_path=None,
        image_base64=None,
    )


def raise_http_error(
    *,
    status_code: int,
    detail: str,
    log_message: str,
    exc: Optional[Exception] = None,
) -> None:
    if exc:
        logger.exception(log_message)
        raise HTTPException(status_code=status_code, detail=detail) from exc

    logger.error(log_message)
    raise HTTPException(status_code=status_code, detail=detail)


def validate_message_length(message: str) -> None:
    if len(message) > MAX_PROMPT_LENGTH:
        raise_http_error(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=TOO_LONG_PROMPT_RESPONSE,
            log_message=f"Prompt exceeded max length of {MAX_PROMPT_LENGTH} characters.",
        )


def validate_message_safety(message: str) -> None:
    try:
        safe = is_safe(message)
    except Exception as exc:
        raise_http_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Moderation failed.",
            log_message="Moderation check failed.",
            exc=exc,
        )

    if not safe:
        raise_http_error(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please use respectful language.",
            log_message="Unsafe user input blocked by moderation.",
        )


def extract_user_message(request: AssistantRequest) -> tuple[str, Optional[str]]:
    user_message = request.message or request.query
    transcribed_text = None

    if request.use_voice_input:
        if not request.input_audio_path:
            raise_http_error(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="input_audio_path is required when use_voice_input is true.",
                log_message="Voice input requested without input_audio_path.",
            )

        try:
            transcribed_text = transcribe_audio_file(request.input_audio_path)
            user_message = transcribed_text
        except FileNotFoundError as exc:
            raise_http_error(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Audio file not found: {exc}",
                log_message="Audio file not found during transcription.",
                exc=exc,
            )
        except Exception as exc:
            raise_http_error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Voice input failed.",
                log_message="Voice transcription failed.",
                exc=exc,
            )

    if not user_message or not user_message.strip():
        raise_http_error(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A message is required.",
            log_message="Request rejected because message was empty.",
        )

    user_message = normalize_text(user_message)
    validate_message_length(user_message)
    validate_message_safety(user_message)

    return user_message, transcribed_text


def get_chatbot_result(user_message: str) -> tuple[str, Optional[str]]:
    try:
        result = ask_chatbot(user_message)
        response_text = normalize_text(result["text"])
        title = result.get("title")
        return response_text, title
    except KeyError as exc:
        raise_http_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chatbot response format invalid: missing {exc}",
            log_message="Chatbot response missing required keys.",
            exc=exc,
        )
    except Exception as exc:
        raise_http_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Chatbot failed.",
            log_message="Chatbot execution failed.",
            exc=exc,
        )


async def generate_audio_response(
    *,
    response_text: str,
    should_generate: bool,
) -> tuple[bool, Optional[str]]:
    if not should_generate:
        return False, None

    try:
        audio_bytes = await text_to_speech_bytes(response_text)
        return True, encode_bytes_to_base64(audio_bytes)
    except Exception as exc:
        raise_http_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Audio generation failed.",
            log_message="Audio generation failed.",
            exc=exc,
        )


def generate_image_response(
    *,
    title: Optional[str],
    should_generate: bool,
) -> tuple[Optional[str], Optional[str]]:
    if not should_generate or not title:
        return None, None

    try:
        image_path = generate_book_image(title)
        image_base64 = encode_file_to_base64(image_path)
        return image_path, image_base64
    except FileNotFoundError as exc:
        raise_http_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generated image file not found: {exc}",
            log_message="Generated image file not found.",
            exc=exc,
        )
    except Exception as exc:
        raise_http_error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Image generation failed.",
            log_message="Image generation failed.",
            exc=exc,
        )


async def build_assistant_response(request: AssistantRequest) -> AssistantResponse:
    user_message, transcribed_text = extract_user_message(request)

    if not is_meaningful_prompt(user_message):
        return build_unclear_response(
            user_message=user_message,
            transcribed_text=transcribed_text,
        )

    response_text, title = get_chatbot_result(user_message)

    audio_generated, audio_base64 = await generate_audio_response(
        response_text=response_text,
        should_generate=request.generate_audio,
    )

    image_path, image_base64 = generate_image_response(
        title=title,
        should_generate=request.generate_image,
    )

    return AssistantResponse(
        user_message=user_message,
        transcribed_text=transcribed_text,
        response=response_text,
        title=title,
        audio_generated=audio_generated,
        audio_base64=audio_base64,
        image_path=image_path,
        image_base64=image_base64,
    )


@app.post("/chat", response_model=AssistantResponse, tags=["Assistant"])
async def chat(request: AssistantRequest) -> AssistantResponse:
    return await build_assistant_response(request)


@app.post("/assistant", response_model=AssistantResponse, tags=["Assistant"])
async def assistant(request: AssistantRequest) -> AssistantResponse:
    return await build_assistant_response(request)