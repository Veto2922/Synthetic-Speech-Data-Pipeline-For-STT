import json
from pathlib import Path


def load_existing_audio_ids(metadata_path: Path) -> set[str]:
    existing_ids = set()

    if not metadata_path.exists():
        return existing_ids

    with open(metadata_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)

                existing_ids.add(record["audio_id"])

            except Exception:
                continue

    return existing_ids
