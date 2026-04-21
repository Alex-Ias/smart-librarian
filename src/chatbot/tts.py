import asyncio
import ctypes
import tempfile
import time
from pathlib import Path

import edge_tts
from langdetect import LangDetectException, detect

DEFAULT_VOICE = "en-US-AriaNeural"

VOICE_MAP = {
    "en": "en-US-AriaNeural",
    "ro": "ro-RO-EmilNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "es": "es-ES-ElviraNeural",
    "it": "it-IT-ElsaNeural",
}


def detect_language(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return "en"


def select_voice(language_code: str) -> str:
    return VOICE_MAP.get(language_code, DEFAULT_VOICE)


async def _generate_temp_audio_file(text: str) -> str:
    if not text or not text.strip():
        raise ValueError("Text for speech generation cannot be empty.")

    language_code = detect_language(text)
    voice = select_voice(language_code)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp_path = Path(temp_file.name)
    temp_file.close()

    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(str(temp_path))

    return str(temp_path)


def _mci_send(command: str) -> int:
    return ctypes.windll.winmm.mciSendStringW(command, None, 0, None)


def _play_audio_windows(audio_file: str) -> None:
    alias = "smart_librarian_audio"

    _mci_send(f'close {alias}')
    error = _mci_send(f'open "{audio_file}" type mpegvideo alias {alias}')
    if error != 0:
        raise RuntimeError("Could not open audio file for playback.")

    error = _mci_send(f'play {alias} wait')
    _mci_send(f'close {alias}')

    if error != 0:
        raise RuntimeError("Could not play audio file.")

# For API usage: generate audio as bytes so the backend can return it in an HTTP response.
async def _synthesize_to_bytes(text: str) -> bytes:
    if not text or not text.strip():
        raise ValueError("Text for speech generation cannot be empty.")

    temp_audio_file = await _generate_temp_audio_file(text)
    temp_path = Path(temp_audio_file)

    try:
        return temp_path.read_bytes()
    finally:
        temp_path.unlink(missing_ok=True)


async def text_to_speech_bytes(text: str) -> bytes:
    return await _synthesize_to_bytes(text)