import asyncio
import json


from datetime import datetime

from loguru import logger
from google.genai import types
from pathlib import Path

from .prompts.tts_prompt_builder import TTSPromptBuilder
from .schemas.audio_generation_result import AudioGenerationResult
from ..utils.process_wav_file import process_wave_file


class AudioGenerationTTSService:
    def __init__(
        self,
        client,
        tts_model_name="gemini-2.5-flash-preview-tts",
        output_dir="data/audio_outputs",
        jsonl_path="data/synthetic_audio_dataset.jsonl",
        max_concurrent_tasks=5,
    ):
        self.client = client

        self.tts_model_name = tts_model_name

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.jsonl_path = Path(jsonl_path)
        self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)

        # concurrency control
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

        self.speaker_id_map = {
            "1": "Zephyr",
            "2": "Kore",
            "3": "Algenib",
            "4": "Algieba",
        }

        logger.info("✅ GeminiTTSService initialized")

    # =====================================================
    # Save JSONL
    # =====================================================

    def save_to_jsonl(self, record: dict):
        with open(self.jsonl_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    # =====================================================
    # Generate ONE audio sample
    # =====================================================

    async def generate_audio(self, prompt_record: dict):
        async with self.semaphore:
            start_time = datetime.utcnow()

            try:
                logger.info(f"🎤 Generating audio | " f"id={prompt_record['id']}")

                audio_id = prompt_record["id"]

                output_path = self.output_dir / f"{audio_id}.wav"

                # ======================================
                # Caching / Skip Existing
                # ======================================

                if output_path.exists():
                    logger.info(f"⏭️ Skipping existing audio | " f"id={audio_id}")

                    return None

                # ======================================
                # Build TTS Prompt
                # ======================================

                tts_prompt = TTSPromptBuilder.build(prompt_record)

                # ======================================
                # Select Voice
                # ======================================

                speaker_id = prompt_record["speaker_id"]

                voice_name = self.speaker_id_map[speaker_id]

                # ======================================
                # Generate Audio
                # Run blocking API in thread
                # ======================================

                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=self.tts_model_name,
                    contents=tts_prompt,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=(
                                    types.PrebuiltVoiceConfig(voice_name=voice_name)
                                )
                            )
                        ),
                    ),
                )

                # ======================================
                # Extract PCM
                # ======================================

                pcm_data = response.candidates[0].content.parts[0].inline_data.data

                # ======================================
                # Save WAV
                # ======================================

                await asyncio.to_thread(process_wave_file, str(output_path), pcm_data)

                # ======================================
                # Build Result Schema
                # ======================================

                result = AudioGenerationResult(
                    audio_id=audio_id,
                    prompt_id=prompt_record["id"],
                    audio_path=str(output_path),
                    text=prompt_record["text"],
                    background_noise=prompt_record["background_noise"],
                    voice_name=voice_name,
                    speaker_id=speaker_id,
                    tts_model=self.tts_model_name,
                    sample_rate=24000,
                    status="generated",
                    review_status="pending",
                )

                # ======================================
                # Save Metadata JSONL
                # ======================================

                self.save_to_jsonl(result.model_dump())

                duration = (datetime.utcnow() - start_time).total_seconds()

                logger.success(
                    f"✅ Audio generated | " f"id={audio_id} | " f"time={duration:.2f}s"
                )

                return result

            except Exception as e:
                logger.error(
                    f"❌ Audio generation failed | "
                    f"id={prompt_record.get('id')} | "
                    f"error={str(e)}"
                )

                return None

    # =====================================================
    # Generate Multiple Audio Samples in Parallel
    # =====================================================

    async def generate_parallel(self, prompt_records: list[dict]):
        logger.info(
            f"🚀 Starting parallel TTS generation | " f"samples={len(prompt_records)}"
        )

        tasks = [self.generate_audio(record) for record in prompt_records]

        results = await asyncio.gather(*tasks)

        # remove failed/skipped
        results = [r for r in results if r is not None]

        logger.success(f"🏁 Parallel TTS completed | " f"generated={len(results)}")

        return results
