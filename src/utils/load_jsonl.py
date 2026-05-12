import json
from pathlib import Path
from loguru import logger


def load_jsonl(jsonl_path: Path):
    records = []

    with open(jsonl_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except Exception as e:
                logger.warning(f"Failed parsing line: {e}")

    return records
