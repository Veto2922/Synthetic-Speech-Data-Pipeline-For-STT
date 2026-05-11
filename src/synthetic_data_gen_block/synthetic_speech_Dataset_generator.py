import asyncio
import json
import random
from pathlib import Path
from uuid import uuid4
from datetime import datetime

from loguru import logger
from langchain_core.messages import SystemMessage, HumanMessage

from ..utils.normalize_text import normalize_text, validate_no_digits


class SyntheticSpeechDatasetGenerator:
    def __init__(
        self,
        structured_model,
        schema_class,
        system_prompt: str,
        model_name: str,
        schema_version: str = "1.0",
        output_file: str = "dataset_output.jsonl",
        max_concurrent_tasks: int = 10,
    ):
        self.structured_model = structured_model
        self.schema_class = schema_class
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.schema_version = schema_version

        self.output_file = Path(output_file)
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

        logger.info("✅ SyntheticSpeechDatasetGenerator initialized")

    # =====================================================
    # Save JSONL
    # =====================================================

    def save_to_jsonl(self, record: dict):
        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")

    # =====================================================
    # Process & Validate Record
    # =====================================================

    def process_record(self, raw_data: dict) -> dict:
        # -------------------------
        # Normalize text
        # -------------------------
        raw_data["text"] = normalize_text(raw_data["text"])

        # -------------------------
        # Validate digits
        # -------------------------
        status = "generated"

        if not validate_no_digits(raw_data["text"]):
            status = "rejected"

        # -------------------------
        # Schema validation
        # -------------------------
        validated = self.schema_class(**raw_data)

        speaker_id = random.choice(["1", "2", "3", "4"])

        final_record = {
            "id": str(uuid4()),
            "schema_version": self.schema_version,
            "created_at": datetime.utcnow().isoformat(),
            "status": status,
            "review_status": "pending",
            "source": self.model_name,
            "speaker_id": speaker_id,
            **validated.model_dump(),
        }

        return final_record

    # =====================================================
    # Generate ONE sample
    # =====================================================

    async def generate_sample(self, topic: str):
        async with self.semaphore:
            start_time = datetime.utcnow()

            logger.info(f"🚀 Generating sample | topic={topic}")

            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Generate one sample about topic: {topic}"),
            ]

            try:
                response = await self.structured_model.ainvoke(messages)

                raw_data = response.model_dump()

                final_record = self.process_record(raw_data)

                # -------------------------
                # Save
                # -------------------------
                self.save_to_jsonl(final_record)

                duration = (datetime.utcnow() - start_time).total_seconds()

                logger.success(
                    f"✅ Sample generated | "
                    f"topic={topic} | "
                    f"status={final_record['status']} | "
                    f"time={duration:.2f}s"
                )

                return final_record

            except Exception as e:
                logger.error(
                    f"❌ Failed sample generation | "
                    f"topic={topic} | "
                    f"error={str(e)}"
                )

                return None

    # =====================================================
    # Generate MULTIPLE samples in parallel
    # =====================================================

    async def generate_parallel(self, topics: list[str]):
        logger.info(f"🔥 Starting parallel generation | " f"topics={len(topics)}")

        tasks = [self.generate_sample(topic) for topic in topics]

        results = await asyncio.gather(*tasks)

        results = [r for r in results if r is not None]

        logger.success(
            f"🏁 Parallel generation completed | " f"successful={len(results)}"
        )

        return results

    # =====================================================
    # Generate BATCHES in parallel
    # =====================================================

    async def generate_batches(
        self, categories: list[str], samples_per_category: int = 5, batch_size: int = 10
    ):
        # samples_per_category = len(categories)

        logger.info(
            f"🚀 Starting generation | "
            f"categories={len(categories)} | "
            f"samples_per_category={samples_per_category} | "
            f"expected_samples={len(categories) * samples_per_category}"
        )

        all_results = []

        # =====================================================
        # EXPAND categories
        # =====================================================

        expanded_categories = []

        for _ in range(samples_per_category):
            for category in categories:
                expanded_categories.append(category)

        random.shuffle(expanded_categories)

        logger.info(
            f"📦 Expanded categories to " f"{len(expanded_categories)} total prompts"
        )

        # =====================================================
        # Split into provider batches
        # =====================================================

        provider_batches = [
            expanded_categories[i : i + batch_size]
            for i in range(0, len(expanded_categories), batch_size)
        ]

        logger.info(f"⚡ Created {len(provider_batches)} provider batches")

        # =====================================================
        # Process provider batches
        # =====================================================

        for batch_index, batch_categories in enumerate(provider_batches):
            logger.info(
                f"🚀 Processing provider batch "
                f"{batch_index + 1}/{len(provider_batches)}"
            )

            try:
                batch_messages = []

                for topic in batch_categories:
                    messages = [
                        SystemMessage(content=self.system_prompt),
                        HumanMessage(
                            content=f"Generate one sample about topic: {topic}"
                        ),
                    ]

                    batch_messages.append(messages)

                # ==========================================
                # PROVIDER BATCH CALL
                # ==========================================

                responses = await self.structured_model.abatch(batch_messages)

                # ==========================================
                # Process responses
                # ==========================================

                for response in responses:
                    try:
                        raw_data = response.model_dump()

                        final_record = self.process_record(raw_data)

                        self.save_to_jsonl(final_record)

                        all_results.append(final_record)

                        logger.success(
                            f"✅ Saved sample | " f"category={final_record['category']}"
                        )

                    except Exception as e:
                        logger.error(
                            f"❌ Failed processing response | " f"error={str(e)}"
                        )

            except Exception as e:
                logger.error(
                    f"❌ Provider batch failed | "
                    f"batch_index={batch_index} | "
                    f"error={str(e)}"
                )

        logger.success(
            f"🏁 Generation completed | " f"total_samples={len(all_results)}"
        )

        return all_results
