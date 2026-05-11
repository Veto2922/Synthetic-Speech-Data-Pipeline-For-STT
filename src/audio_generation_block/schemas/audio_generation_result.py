from pydantic import BaseModel


class AudioGenerationResult(BaseModel):
    audio_id: str
    prompt_id: str

    audio_path: str

    text: str

    voice_name: str
    speaker_id: str
    tts_model: str

    background_noise: str

    sample_rate: int

    status: str
    review_status: str
