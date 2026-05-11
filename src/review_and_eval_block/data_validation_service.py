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


class AudioValidationService:
    def __init__(
        self,
        gemini_client,
        accepted_jsonl="data/accepted.jsonl",
        rejected_jsonl="data/rejected.jsonl",
        min_duration=1.0,
        max_duration=30.0,
        min_rms=0.005,
        max_wer: float = 0.25,
    ):
        self.gemini_client = gemini_client

        self.accepted_jsonl = Path(accepted_jsonl)
        self.rejected_jsonl = Path(rejected_jsonl)

        self.accepted_jsonl.parent.mkdir(parents=True, exist_ok=True)

        self.max_wer = max_wer

        self.min_duration = min_duration
        self.max_duration = max_duration
        self.min_rms = min_rms

    # =====================================================
    # SAVE JSONL
    # =====================================================

    def save_result(self, result: dict, accepted: bool):
        output_file = self.accepted_jsonl if accepted else self.rejected_jsonl

        with open(output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

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
            self.gemini_client, audio_path, original_text, self.max_wer
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
        logger.info(f"🚀 Starting validation batch | " f"samples={len(records)}")

        tasks = [self.validate_sample(r) for r in records]

        results = await asyncio.gather(*tasks)

        logger.success(f"🏁 Validation completed | " f"samples={len(results)}")

        return results
