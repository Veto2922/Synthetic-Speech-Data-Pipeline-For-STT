import json

from pathlib import Path
from copy import deepcopy
from datetime import datetime
from loguru import logger

from ..utils.load_existing_audio_ids import load_existing_audio_ids
from ..utils.save_to_jsonl import save_to_jsonl

from ..utils.add_background_noise import add_background_noise


class AudioAugmentationService:
    def __init__(
        self,
        metadata_output_path: Path,
        noise_dir: Path,
        noise_map: dict,
        snr_db: float = 10,
        base_dir: Path = Path.cwd(),
    ):
        self.metadata_output_path = metadata_output_path

        self.noise_dir = noise_dir

        self.noise_map = noise_map

        self.snr_db = snr_db
        self.base_dir = base_dir

        # load existing ids once
        self.existing_audio_ids = load_existing_audio_ids(metadata_output_path)

        logger.info(
            f"AudioAugmentationService initialized | "
            f"existing_records={len(self.existing_audio_ids)}"
        )

    # =====================================================
    # AUGMENT SINGLE RECORD
    # =====================================================

    def augment_audio_record(
        self,
        record: dict,
    ):
        try:
            original_record = deepcopy(record)

            audio_id = original_record["audio_id"]

            # =====================================
            # SKIP EXISTING CLEAN RECORD
            # =====================================

            if audio_id in self.existing_audio_ids:
                logger.warning(f"Skipping existing record | " f"id={audio_id}")

                return None

            # =====================================
            # CLEAN AUDIO
            # =====================================

            if original_record["background_noise"] == "clean audio":
                logger.info(f"Saving clean sample only | " f"id={audio_id}")

                original_record["with_noise"] = False

                original_record["created_at"] = datetime.utcnow().isoformat()

                save_to_jsonl(self.metadata_output_path, original_record)

                self.existing_audio_ids.add(audio_id)

                logger.success(f"Clean sample saved | " f"id={audio_id}")

                return original_record

            # =====================================
            # AUGMENTED ID
            # =====================================

            augmented_audio_id = audio_id + "_with_noise"

            # =====================================
            # SKIP EXISTING AUGMENTED RECORD
            # =====================================

            if augmented_audio_id in self.existing_audio_ids:
                logger.warning(
                    f"Skipping existing augmented sample | " f"id={augmented_audio_id}"
                )

                return None

            # =====================================
            # GET NOISE FILE
            # =====================================

            noise_type = original_record["background_noise"]

            noise_file = self.noise_map.get(noise_type)

            if noise_file is None:
                logger.warning(f"Unknown noise type | " f"{noise_type}")

                return None

            noise_path = (self.noise_dir / noise_file).resolve()

            if not noise_path.exists():
                logger.error(f"Noise file missing | " f"{noise_path}")

                return None

            # =====================================
            # ORIGINAL AUDIO
            # =====================================

            original_audio_path = (
                self.base_dir / original_record["audio_path"]
            ).resolve()

            if not original_audio_path.exists():
                logger.error(f"Original audio missing | " f"{original_audio_path}")

                return None

            # =====================================
            # OUTPUT PATH
            # =====================================

            output_path = original_audio_path.with_name(
                original_audio_path.stem + "_with_noise.wav"
            )

            # =====================================
            # CREATE WAV
            # =====================================

            if output_path.exists():
                logger.warning(f"Augmented wav already exists | " f"{output_path}")

            else:
                logger.info(
                    f"Adding background noise | "
                    f"id={audio_id} | "
                    f"noise={noise_type}"
                )

                add_background_noise(
                    speech_path=str(original_audio_path),
                    noise_path=str(noise_path),
                    output_path=str(output_path),
                    snr_db=self.snr_db,
                )

                if not output_path.exists():
                    raise FileNotFoundError(
                        f"Failed to create augmented wav | " f"{output_path}"
                    )

                logger.success(f"Augmented wav created | " f"{output_path}")

            # =====================================
            # CREATE METADATA
            # =====================================

            augmented_record = deepcopy(original_record)

            augmented_record["parent_audio_id"] = audio_id

            augmented_record["audio_id"] = augmented_audio_id

            augmented_record["with_noise"] = True

            augmented_record["audio_path"] = str(output_path.relative_to(self.base_dir))

            augmented_record["augmentation"] = {
                "type": "background_noise",
                "noise_type": noise_type,
                "snr_db": self.snr_db,
            }

            augmented_record["created_at"] = datetime.utcnow().isoformat()

            # =====================================
            # SAVE
            # =====================================

            save_to_jsonl(self.metadata_output_path, original_record)
            save_to_jsonl(self.metadata_output_path, augmented_record)

            self.existing_audio_ids.add(augmented_audio_id)

            logger.success(f"Augmented sample saved | " f"id={augmented_audio_id}")

            return augmented_record

        except Exception:
            logger.exception(f"Augmentation failed | " f"id={record.get('audio_id')}")

            return None

    # =====================================================
    # AUGMENT DATASET
    # =====================================================

    def augment_dataset(
        self,
        records: list[dict],
    ):
        augmented_records = []

        logger.info(f"Starting augmentation | " f"samples={len(records)}")

        for record in records:
            result = self.augment_audio_record(record)

            if result is not None:
                augmented_records.append(result)

        logger.success(
            f"Augmentation completed | " f"generated={len(augmented_records)}"
        )

        return augmented_records
