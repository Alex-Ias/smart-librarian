from pydantic import BaseModel


class AssistantRequest(BaseModel):
    message: str | None = None
    query: str | None = None
    use_voice_input: bool = False
    input_audio_path: str | None = None
    generate_audio: bool = False
    generate_image: bool = False


class AssistantResponse(BaseModel):
    user_message: str
    transcribed_text: str | None = None
    response: str
    title: str | None = None
    audio_generated: bool = False
    audio_base64: str | None = None
    image_path: str | None = None
    image_base64: str | None = None
