import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

from google import genai

from langchain.chat_models import init_chat_model

# pyrefly: ignore [missing-import]
from src.synthetic_data_gen_block.synthetic_text_Dataset_generator import (
    SyntheticTextDatasetGenerator,
)

# pyrefly: ignore [missing-import]
from src.audio_generation_block.Audio_Generation_TTS_Service import (
    AudioGenerationTTSService,
)

# pyrefly: ignore [missing-import]
from src.review_and_eval_block.data_validation_service import (
    AudioValidationService,
)

# pyrefly: ignore [missing-import]
from src.add_background_noise_block.audio_augmentation_service import (
    AudioAugmentationService,
)

# pyrefly: ignore [missing-import]
from src.data_formating_block.dataset_formatter_service import (
    DatasetFormatterService,
)

# pyrefly: ignore [missing-import]
from src.synthetic_data_gen_block.shcemas.enums_schemas import Category


# =========================================================
# CONFIG
# =========================================================

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

BASE_DIR = Path(__file__).resolve().parent

NOISE_DIR = BASE_DIR / "data" / "background_noise"

PROJECT_DIR = BASE_DIR / "data" / "project_2"


INPUT_METADATA_PATH = PROJECT_DIR / "final_dataset_metadata.jsonl"

OUTPUT_DATASET_DIR = PROJECT_DIR / "dataset"

OUTPUT_WAV_DIR = OUTPUT_DATASET_DIR / "wavs"

METADATA_CSV_PATH = OUTPUT_DATASET_DIR / "metadata.csv"


NOISE_MAP = {
    "background street noise": "street_noise.wav",
    "background crowd": "crowd_noise.wav",
}


# =========================================================
# PIPELINE CONTROLLER
# =========================================================


class PipelineRunner:
    def __init__(
        self,
        GEMINI_API_KEY,
        Project_Name,
        TEXT_MODEL_NAME="gemini-2.5-flash-lite",
        TTS_MODEL_NAME="gemini-2.5-flash-preview-tts",
        STT_MODEL_NAME="gemini-2.5-flash-lite",
        categories=None,
    ):
        self.TEXT_MODEL_NAME = TEXT_MODEL_NAME
        self.TTS_MODEL_NAME = TTS_MODEL_NAME
        self.STT_MODEL_NAME = STT_MODEL_NAME

        if categories is None:
            self.all_categories = [cat.value for cat in Category]
        else:
            self.all_categories = categories

        self.model = init_chat_model(
            TEXT_MODEL_NAME,
            model_provider="google-genai",
            temperature=0.7,
            max_tokens=1000,
            api_key=GEMINI_API_KEY,
        )

        self.client = genai.Client(api_key=GEMINI_API_KEY)

        self.BASE_DIR = Path(__file__).resolve().parents[1]
        self.PROJECT_DIR = self.BASE_DIR / "data" / Project_Name

        # for data formatting
        self.INPUT_METADATA_PATH = self.PROJECT_DIR / "final_dataset_metadata.jsonl"
        self.OUTPUT_DATASET_DIR = self.PROJECT_DIR / "dataset"
        self.OUTPUT_WAV_DIR = self.OUTPUT_DATASET_DIR / "wavs"
        self.METADATA_CSV_PATH = self.OUTPUT_DATASET_DIR / "metadata.csv"

        self.NOISE_DIR = self.BASE_DIR / "data" / "background_noise"
        self.NOISE_MAP = {
            "background street noise": "street_noise.wav",
            "background crowd": "crowd_noise.wav",
        }

    # =====================================================
    # STAGE 1: TEXT GENERATION
    # =====================================================

    async def run_text_generation(self, samples_per_category=1, batch_size=10):
        logger.info("🚀 Stage 1: Text Generation")

        generator = SyntheticTextDatasetGenerator(
            model=self.model,
            model_name=self.TEXT_MODEL_NAME,
            output_file=str(self.PROJECT_DIR / "synthetic_text_dataset.jsonl"),
        )

        await generator.generate_batches(
            categories=self.all_categories,
            samples_per_category=samples_per_category,
            batch_size=batch_size,
        )

    # # =====================================================
    # # STAGE 2: TTS GENERATION
    # # =====================================================

    async def run_tts_generation(self):
        logger.info("🎙️ Stage 2: TTS Generation")

        text_path = self.PROJECT_DIR / "synthetic_text_dataset.jsonl"

        records = [json.loads(l) for l in open(text_path, "r", encoding="utf-8")]

        service = AudioGenerationTTSService(
            client=self.client,
            tts_model_name=self.TTS_MODEL_NAME,
            output_dir=str(self.PROJECT_DIR / "audio_outputs"),
            jsonl_path=str(self.PROJECT_DIR / "synthetic_audio_dataset.jsonl"),
            max_concurrent_tasks=4,
        )

        await service.generate_parallel(records)

    # # =====================================================
    # # STAGE 3: VALIDATION
    # # =====================================================

    async def run_validation(
        self,
        min_duration=1.0,
        max_duration=30.0,
        min_rms=0.005,
        max_wer=0.3,
    ):
        logger.info("🧪 Stage 3: Validation")

        path = self.PROJECT_DIR / "synthetic_audio_dataset.jsonl"

        records = [json.loads(l) for l in open(path, "r", encoding="utf-8")]

        validator = AudioValidationService(
            gemini_client=self.client,
            stt_model_name=self.STT_MODEL_NAME,
            accepted_jsonl=str(self.PROJECT_DIR / "accepted.jsonl"),
            rejected_jsonl=str(self.PROJECT_DIR / "rejected.jsonl"),
            min_duration=min_duration,
            max_duration=max_duration,
            min_rms=min_rms,
            max_wer=max_wer,
        )

        await validator.validate_parallel(records)

    # # =====================================================
    # # STAGE 4: AUGMENTATION
    # # =====================================================

    def run_augmentation(self, snr_db=10):
        logger.info("🔊 Stage 4: Augmentation")

        records = [
            json.loads(l)
            for l in open(self.PROJECT_DIR / "accepted.jsonl", "r", encoding="utf-8")
        ]

        service = AudioAugmentationService(
            metadata_output_path=self.PROJECT_DIR / "final_dataset_metadata.jsonl",
            noise_dir=self.NOISE_DIR,
            noise_map=self.NOISE_MAP,
            snr_db=snr_db,
            base_dir=self.BASE_DIR,
        )

        service.augment_dataset(records)

    # # =====================================================
    # # STAGE 5: FORMATTING
    # # =====================================================

    def run_formatting(self, target_sample_rate=16000, mono=True, normalize=True):
        logger.info("📦 Stage 5: Dataset Formatting")

        formatter = DatasetFormatterService(
            metadata_path=self.INPUT_METADATA_PATH,
            metadata_csv_path=self.METADATA_CSV_PATH,
            output_dataset_dir=self.OUTPUT_DATASET_DIR,
            base_dir=self.BASE_DIR,
            target_sample_rate=target_sample_rate,
            mono=mono,
            normalize=normalize,
        )

        formatter.build_dataset()

    # # =====================================================
    # # FULL PIPELINE
    # # =====================================================

    # async def run_all(self):
    #     await self.run_text_generation()

    #     await self.run_tts_generation()

    #     await self.run_validation()

    #     self.run_augmentation()

    #     self.run_formatting()


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    all_categories = [cat.value for cat in Category]

    runner = PipelineRunner(categories=all_categories[:5])

    asyncio.run(runner.run_all())
