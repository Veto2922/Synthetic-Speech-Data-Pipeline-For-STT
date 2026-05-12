from pathlib import Path
import json
from datetime import datetime
from loguru import logger
import asyncio

from .validation_utils.audio_utils import (
    resolve_audio_path,
)
from .validation_utils.stt_verification import (
    run_stt_verification,
)
from .validation_utils.fast_checks import (
    run_fast_checks,
)
from ..utils.load_jsonl import load_jsonl


class AudioValidationService:
    def __init__(
        self,
        gemini_client,
        accepted_jsonl="data/accepted.jsonl",
        rejected_jsonl="data/rejected.jsonl",
        stt_model_name: str = "gemini-2.5-flash-lite",
        min_duration=1.0,
        max_duration=30.0,
        min_rms=0.005,
        max_wer: float = 0.3,
    ):
        self.gemini_client = gemini_client
        self.stt_model_name = stt_model_name

        self.accepted_jsonl = Path(accepted_jsonl)
        self.rejected_jsonl = Path(rejected_jsonl)

        self.accepted_jsonl.parent.mkdir(parents=True, exist_ok=True)

        self.max_wer = max_wer

        self.min_duration = min_duration
        self.max_duration = max_duration
        self.min_rms = min_rms

        # Load already processed IDs to avoid duplicates
        self.processed_ids = self._load_processed_ids()

    def _load_processed_ids(self) -> set:
        processed_ids = set()
        for path in [self.accepted_jsonl, self.rejected_jsonl]:
            if path.exists():
                try:
                    # Using local import if needed or the one from utils
                    records = load_jsonl(path)
                    for r in records:
                        if "audio_id" in r:
                            processed_ids.add(r["audio_id"])
                except Exception as e:
                    logger.warning(f"Could not load processed IDs from {path}: {e}")

        if processed_ids:
            logger.info(f"Loaded {len(processed_ids)} already processed IDs.")
        return processed_ids

    # =====================================================
    # SAVE JSONL
    # =====================================================

    def save_result(self, result: dict, accepted: bool):
        output_file = self.accepted_jsonl if accepted else self.rejected_jsonl

        with open(output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        # Add to processed IDs
        if "audio_id" in result:
            self.processed_ids.add(result["audio_id"])

    # =====================================================
    # STAGE 1 -> FAST RULE FILTERS
    # =====================================================

    def run_fast_checks(self, audio_path: str, text: str):
        return run_fast_checks(
            audio_path, text, self.min_duration, self.max_duration, self.min_rms
        )

    # =====================================================
    # STAGE 2 -> STT VERIFICATION
    # =====================================================

    async def run_stt_verification(self, audio_path: str, original_text: str):
        return await run_stt_verification(
            self.gemini_client,
            audio_path,
            original_text,
            self.max_wer,
            self.stt_model_name,
        )

    # =====================================================
    # FULL VALIDATION PIPELINE
    # =====================================================

    async def validate_sample(self, record: dict):
        logger.info(f"🔍 Validating sample | " f"id={record['audio_id']}")

        audio_path = str(resolve_audio_path(record["audio_path"]))
        original_text = record["text"]

        # =====================================
        # STAGE 1
        # =====================================

        fast_checks = self.run_fast_checks(audio_path, original_text)

        print("fast_checks output: ", fast_checks)

        # =====================================
        # REJECT EARLY
        # =====================================

        if not fast_checks["passed"]:
            record.update(
                {
                    "status": "reviewed",
                    "review_status": "rejected",
                    "duration_seconds": fast_checks["duration"],
                    "wer": None,
                    "transcript": None,
                    "issues": fast_checks["issues"],
                    "validated_at": datetime.utcnow().isoformat(),
                }
            )

            self.save_result(record, accepted=False)

            logger.warning(f"❌ Rejected by stage 1 | " f"id={record['audio_id']}")

            return record

        # =====================================
        # STAGE 2
        # =====================================

        stt_result = await self.run_stt_verification(audio_path, original_text)

        # =====================================
        # CHECK FOR TRANSIENT ERRORS (503, etc.)
        # =====================================
        # If the error is transient, we don't want to save it as rejected.
        # This allows it to be picked up again in the next run.
        is_transient = any(
            "503" in str(issue) or "UNAVAILABLE" in str(issue).upper()
            for issue in stt_result["issues"]
        )

        if is_transient:
            logger.error(
                f"⚠️ Transient error (503/Unavailable) for sample {record['audio_id']}. "
                "Skipping saving to allow retry in next run."
            )
            return record

        accepted = stt_result["passed"]

        review_status = "accepted" if accepted else "rejected"

        # =====================================
        # FINAL RECORD
        # =====================================

        record.update(
            {
                "status": "reviewed",
                "review_status": review_status,
                "duration_seconds": fast_checks["duration"],
                "wer": stt_result["wer"],
                "transcript": stt_result["transcript"],
                "issues": (fast_checks["issues"] + stt_result["issues"]),
                "validated_at": datetime.utcnow().isoformat(),
            }
        )

        self.save_result(record, accepted=accepted)

        logger.success(
            f"✅ Validation complete | "
            f"id={record['audio_id']} | "
            f"decision={review_status}"
        )

        return record

    # =====================================================
    # VALIDATE MULTIPLE
    # =====================================================

    async def validate_parallel(self, records: list[dict]):
        # Filter out already processed records
        to_process = [r for r in records if r.get("audio_id") not in self.processed_ids]
        skipped_count = len(records) - len(to_process)

        if skipped_count > 0:
            logger.info(f"⏭️ Skipping {skipped_count} already processed samples.")

        if not to_process:
            logger.info("✅ All samples in this batch already processed.")
            return []

        logger.info(f"🚀 Starting validation batch | " f"samples={len(to_process)}")

        tasks = [self.validate_sample(r) for r in to_process]

        results = await asyncio.gather(*tasks)

        logger.success(f"🏁 Validation completed | " f"samples={len(results)}")

        return results
