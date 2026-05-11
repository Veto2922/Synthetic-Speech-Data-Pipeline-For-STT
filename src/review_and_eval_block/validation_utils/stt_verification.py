from langchain_core.prompts import prompt
import asyncio
from loguru import logger
from .text_utils import normalize_arabic, text_WER

stt_prompt = """"

Generate a transcription of the audio file in Egyptian Arabic.

1. Numbers MUST be written in words (never digits).
2. English technical/product terms MUST remain in English.
3. Avoid Modern Standard Arabic (MSA) completely.
4. No emojis, no offensive content, no propaganda.
5. don't add and addtional text other then the transcription. strictly return the transcription.


"""


async def transcribe_audio(client, audio_path: str) -> str:
    """
    Transcribes audio using Gemini model.
    """
    uploaded_file = await asyncio.to_thread(client.files.upload, file=audio_path)

    result = await asyncio.to_thread(
        client.models.generate_content,
        model="gemini-2.5-flash",
        contents=[
            stt_prompt,
            uploaded_file,
        ],
    )

    return result.text


async def run_stt_verification(
    client, audio_path: str, original_text: str, max_wer: float = 0.25
) -> dict:
    issues = []
    try:
        # =====================================
        # STT
        # =====================================
        transcript = await transcribe_audio(client, audio_path)

        norm_transcript = normalize_arabic(transcript.strip())
        reference = normalize_arabic(original_text.strip())

        # =====================================
        # WER
        # =====================================
        wer_score = text_WER(reference, norm_transcript)
        passed = wer_score <= max_wer

        if not passed:
            issues.append(f"high wer ({wer_score:.2f})")

        return {
            "passed": passed,
            "wer": wer_score,
            "transcript": norm_transcript,
            "issues": issues,
        }

    except Exception as e:
        logger.exception("STT verification failed")
        return {"passed": False, "wer": 1.0, "transcript": "", "issues": [str(e)]}
