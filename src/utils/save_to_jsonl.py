import json
from pathlib import Path


def save_to_jsonl(output_path: Path, record: dict):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
