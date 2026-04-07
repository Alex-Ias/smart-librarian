from pathlib import Path
import tempfile

import sounddevice as sd
from scipy.io.wavfile import write

from src.vector_store.utils import get_openai_client

SAMPLE_RATE = 16000
CHANNELS = 1
RECORD_SECONDS = 5
TRANSCRIPTION_MODEL = "gpt-4o-mini-transcribe"


def record_microphone_to_wav(
    duration_seconds: int = RECORD_SECONDS,
    sample_rate: int = SAMPLE_RATE,
) -> str:
    recording = sd.rec(
        int(duration_seconds * sample_rate),
        samplerate=sample_rate,
        channels=CHANNELS,
        dtype="int16",
    )
    sd.wait()

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    temp_path = Path(temp_file.name)
    temp_file.close()

    write(str(temp_path), sample_rate, recording)
    return str(temp_path)


def transcribe_audio_file(audio_file_path: str) -> str:
    client = get_openai_client()

    with open(audio_file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model=TRANSCRIPTION_MODEL,
            file=audio_file,
        )

    return response.text.strip()


def record_and_transcribe(duration_seconds: int = RECORD_SECONDS) -> str:
    audio_file_path = record_microphone_to_wav(duration_seconds=duration_seconds)
    return transcribe_audio_file(audio_file_path)