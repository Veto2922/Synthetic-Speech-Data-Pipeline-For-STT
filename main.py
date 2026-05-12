# pyrefly: ignore [missing-import]
from src.full_pipeline import PipelineRunner
from dotenv import load_dotenv
import os
import asyncio

# pyrefly: ignore [missing-import]
from src.synthetic_data_gen_block.shcemas.enums_schemas import Category


load_dotenv()

Gemini_API_KEY = os.getenv("GEMINI_API_KEY")

all_categories = [cat.value for cat in Category]

print("all_categories: ", all_categories)


if __name__ == "__main__":
    runner = PipelineRunner(
        categories=all_categories[0:5],
        Project_Name="project_1",
        GEMINI_API_KEY=Gemini_API_KEY,
    )
    # number of samples = samples_per_category * number of categories = 5 * 5 = 25 samples per each stage
    asyncio.run(runner.run_text_generation(samples_per_category=5, batch_size=10))

    asyncio.run(runner.run_tts_generation())

    asyncio.run(
        runner.run_validation(
            min_duration=1.0, max_duration=30.0, min_rms=0.005, max_wer=0.3
        )
    )
    runner.run_augmentation(snr_db=10)

    runner.run_formatting(target_sample_rate=16000, mono=True, normalize=True)
