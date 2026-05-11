from .enums_schemas import (
    Emotion,
    SpeakerStyle,
    SpeakingRate,
    BackgroundNoise,
    Category,
    EnergyLevel,
)
from pydantic import BaseModel, Field
from typing import List


class LLMGeneratedSchema(BaseModel):
    text: str = Field(
        ...,
        description=(
            "Natural Egyptian Arabic utterance suitable for STT training. "
            "Numbers must be written in words, not digits. "
            "English technical/product words should remain in English. "
            "Natural punctuation should be preserved."
        ),
    )

    emotion: Emotion = Field(
        ..., description="Emotional speaking style for TTS generation."
    )

    speaker_style: SpeakerStyle = Field(
        ..., description="Speaker persona or conversation style."
    )

    speaking_rate: SpeakingRate = Field(..., description="Speech speed.")

    energy: EnergyLevel = Field(..., description="Voice energy and intensity.")

    background_noise: BackgroundNoise = Field(
        ...,
        description=("Expected environmental background sound or recording condition."),
    )

    category: Category = Field(..., description="Conversation domain or scenario.")

    code_switching: bool = Field(
        ..., description="Whether Arabic and English are mixed."
    )

    contains_numbers: bool = Field(
        ..., description="Whether numeric concepts are mentioned."
    )

    tags: List[str] = Field(..., description="Extra semantic metadata tags.")
