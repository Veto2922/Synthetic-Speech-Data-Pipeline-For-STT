from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import os

from src.synthetic_data_gen_block.synthetic_speech_Dataset_generator import (
    SyntheticSpeechDatasetGenerator,
)
from src.synthetic_data_gen_block.prompts.synthetic_speech_Dataset_generator_prompts import (
    SYSTEM_PROMPT,
)

from src.synthetic_data_gen_block.shcemas.enums_schemas import Category


from src.synthetic_data_gen_block.shcemas.synthetic_llm_generator_shcema import (
    LLMGeneratedSchema,
)

from src.audio_generation_block.Audio_Generation_TTS_Service import (
    AudioGenerationTTSService,
)


import asyncio
from loguru import logger
from google import genai
from google.genai import types

load_dotenv()


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

SCHEMA_VERSION = "1.0"
MODEL_NAME = "gemini-2.5-flash-lite"
TTS_MODEL_NAME = "gemini-2.5-flash-preview-tts"


# model = init_chat_model(
#     MODEL_NAME,
#     model_provider="google-genai",
#     temperature=0.7,
#     max_tokens=1000,
#     api_key=GEMINI_API_KEY,
# )

# structure_model = model.with_structured_output(LLMGeneratedSchema)


# synthetic_speech_dataset_generator = SyntheticSpeechDatasetGenerator(
#     structured_model=structure_model,
#     system_prompt=SYSTEM_PROMPT,
#     schema_class=LLMGeneratedSchema,
#     model_name=MODEL_NAME,
#     output_file="data/synthetic_text_dataset.jsonl",
# )

# all_categories = [cat.value for cat in list(Category)]


# asyncio.run(synthetic_speech_dataset_generator.generate_parallel(topics=all_categories))


################################# test the audio generation block


# import json

# text_data = []
# DATA_PATH = "data/synthetic_text_dataset.jsonl"

# with open(DATA_PATH, "r", encoding="utf-8") as f:
#     for line in f:
#         text_data.append(json.loads(line))

# # print(text_data)


# client = genai.Client(api_key=GEMINI_API_KEY)

# audio_gen_service = AudioGenerationTTSService(
#     client=client,
#     tts_model_name=TTS_MODEL_NAME,
#     output_dir="data/audio_outputs",
#     jsonl_path="data/synthetic_audio_dataset.jsonl",
#     max_concurrent_tasks=10,
# )

# asyncio.run(audio_gen_service.generate_parallel(text_data[0:4]))


#####################################################
#####################################################
#####################################################

import json
from src.review_and_eval_block.data_validation_service import AudioValidationService


# Load your dataset
DATA_PATH = "data/synthetic_audio_dataset.jsonl"
with open(DATA_PATH, "r", encoding="utf-8") as f:
    records = [json.loads(line) for line in f]


# Initialize validation service

client = genai.Client(api_key=GEMINI_API_KEY)

validator = AudioValidationService(
    gemini_client=client,
    accepted_jsonl="data/accepted.jsonl",
    rejected_jsonl="data/rejected.jsonl",
)


# Validate in parallel
results = asyncio.run(validator.validate_parallel(records[0:5]))


# Verify outputs
with open("data/accepted.jsonl", "r", encoding="utf-8") as f:
    accepted = [json.loads(line) for line in f]

with open("data/rejected.jsonl", "r", encoding="utf-8") as f:
    rejected = [json.loads(line) for line in f]

print(f"Accepted samples: {len(accepted)}")
print(f"Rejected samples: {len(rejected)}")
