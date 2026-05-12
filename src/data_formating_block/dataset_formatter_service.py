from pathlib import Path

import numpy as np
import pandas as pd
import soundfile as sf
from loguru import logger


from ..utils.convert_to_mono import convert_to_mono
from ..utils.normalize_audio import normalize_audio
from ..utils.resample_audio import resample_audio
from ..utils.load_jsonl import load_jsonl


class DatasetFormatterService:
    def __init__(
        self,
        metadata_path: Path,
        output_dataset_dir: Path,
        base_dir: Path,
        metadata_csv_path: Path,
        target_sample_rate: int = 16000,
        mono: bool = True,
        normalize: bool = True,
    ):
        self.metadata_path = metadata_path
        self.metadata_csv_path = metadata_csv_path

        self.base_dir = base_dir

        self.output_dataset_dir = output_dataset_dir

        self.output_wav_dir = output_dataset_dir / "wavs"

        self.target_sample_rate = target_sample_rate

        self.mono = mono

        self.normalize = normalize

        # create dirs
        self.output_wav_dir.mkdir(parents=True, exist_ok=True)

    # =====================================================
    # PROCESS SINGLE AUDIO
    # =====================================================

    def process_audio(
        self,
        input_audio_path: Path,
        output_audio_path: Path,
    ):
        audio, sr = sf.read(input_audio_path)

        audio = audio.astype(np.float32)

        # =============================================
        # MONO
        # =============================================

        if self.mono:
            audio = convert_to_mono(audio)

        # =============================================
        # RESAMPLE
        # =============================================

        audio = resample_audio(audio, sr, self.target_sample_rate)

        # =============================================
        # NORMALIZE
        # =============================================

        if self.normalize:
            audio = normalize_audio(audio)

        # =============================================
        # SAVE WAV
        # =============================================

        sf.write(output_audio_path, audio, self.target_sample_rate, subtype="PCM_16")

    # =====================================================
    # FORMAT DATASET
    # =====================================================

    def build_dataset(self):
        logger.info("Loading metadata...")

        records = load_jsonl(self.metadata_path)

        logger.info(f"Loaded samples: {len(records)}")

        csv_rows = []

        processed_count = 0
        skipped_count = 0

        for idx, record in enumerate(records):
            try:
                # =====================================
                # GET AUDIO
                # =====================================

                original_audio_path = (self.base_dir / record["audio_path"]).resolve()

                if not original_audio_path.exists():
                    logger.warning(f"Audio missing: " f"{original_audio_path}")

                    skipped_count += 1
                    continue

                # =====================================
                # TRANSCRIPTION
                # =====================================

                transcription = record["text"].strip()

                if len(transcription) == 0:
                    logger.warning(f"Empty transcription | " f"id={record['audio_id']}")

                    skipped_count += 1
                    continue

                # =====================================
                # OUTPUT NAME
                # =====================================

                filename = f"sample_{idx:06d}.wav"

                output_audio_path = self.output_wav_dir / filename

                # =====================================
                # PROCESS AUDIO
                # =====================================

                self.process_audio(original_audio_path, output_audio_path)

                # =====================================
                # CSV ROW
                # =====================================

                csv_rows.append(
                    {
                        "audio": (f"wavs/{filename}"),
                        "transcription": (transcription),
                    }
                )

                processed_count += 1

                logger.success(f"Processed | " f"{filename}")

            except Exception as e:
                logger.exception(
                    f"Failed processing sample | " f"id={record.get('audio_id')}"
                )

                skipped_count += 1

        # =================================================
        # SAVE CSV
        # =================================================

        df = pd.DataFrame(csv_rows)

        df.to_csv(self.metadata_csv_path, index=False, encoding="utf-8-sig")

        logger.success(
            f"Dataset formatting completed | "
            f"processed={processed_count} | "
            f"skipped={skipped_count}"
        )

        logger.info(f"Metadata saved to: " f"{self.metadata_csv_path}")

        logger.info(f"Wavs saved to: " f"{self.output_wav_dir}")
