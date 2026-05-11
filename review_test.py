import asyncio
import json
import os
from dotenv import load_dotenv
from google import genai
from src.review_and_eval_block.data_validation_service import AudioValidationService

async def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    # Initialize service
    # Note: Adjust paths as needed based on where the script is run
    audio_val = AudioValidationService(
        client=client,
        accepted_jsonl="notebooks/data/accepted_modular.jsonl",
        rejected_jsonl="notebooks/data/rejected_modular.jsonl"
    )

    # Load some test data
    DATA_PATH = "notebooks/data/synthetic_audio_dataset.jsonl"
    audio_data = []
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            for line in f:
                audio_data.append(json.loads(line))
    else:
        print(f"Data path {DATA_PATH} not found.")
        return

    if not audio_data:
        print("No audio data to validate.")
        return

    # Validate a single sample
    print("Testing single sample validation...")
    await audio_val.validate_sample(audio_data[0])

    # Validate parallel
    print("Testing parallel validation...")
    batch = audio_data[:3]
    await audio_val.validate_parallel(batch)

if __name__ == "__main__":
    asyncio.run(main())
