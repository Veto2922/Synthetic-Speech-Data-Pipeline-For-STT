
# Synthetic Speech Data Pipeline for STT (S.S.D.P)

## Overview

The Synthetic Speech Data Pipeline (S.S.D.P) is an end-to-end system designed to generate **high-quality, Egyptian Arabic speech datasets** for Speech-to-Text (STT) model training.

The main objective is not only to synthesize speech, but to **simulate real-world acoustic conditions** that STT systems encounter in production.

<img width="1905" height="514" alt="image" src="https://github.com/user-attachments/assets/7d32d505-4587-41be-9395-38c66934b70c" />


In real environments, speech is rarely clean; it includes:

* emotions
* multiple speakers
* background noise
* code-switching
* informal dialect variations

This pipeline explicitly models these factors to improve STT robustness.

---

# 🏗️ High-Level Architecture

<img width="1864" height="383" alt="image" src="https://github.com/user-attachments/assets/57df4e15-0643-41c0-ac89-444987d4f5ab" />

Each stage is:

* fully modular
* independently executable
* checkpointed (resumable)
* designed for large-scale generation

---

# 🎯 Design Philosophy

This system was designed as a **data-centric AI pipeline**, not just a generation script.

Core principles:

* realistic acoustic simulation
* modular pipeline architecture
* reproducibility & fault tolerance
* scalability for large datasets
* human-in-the-loop compatibility

---

# 🇪🇬 Egyptian Arabic Challenges

Egyptian Arabic introduces real challenges for STT systems:

| Challenge                | Solution                       |
| ------------------------ | ------------------------------ |          
| informal grammar         | LLM prompt constraints         |
| code-switching           | structured metadata            |
| numeric ambiguity        | numbers written as words       |
| synthetic monotony       | controlled diversity injection |
| TTS pronunciation errors | speaker conditioning           |

---

# 🧩 Pipeline Stages

---

# 1. 📝 Text Generation Stage

<img width="608" height="832" alt="image" src="https://github.com/user-attachments/assets/b3d0fdcd-11f1-4c3f-8157-5cdaba1e0ad6" />


Generates structured Egyptian Arabic prompts using LLMs.

### Key Features:

* strict schema validation (Pydantic + enums)
* Egyptian Arabic-only enforcement
* controlled domain sampling (delivery, support, etc.)
* metadata-rich output
* async and batchin 

### Output Example:

```json id="text_stage"
{
  "text": "ممكن تبعتلي ال location لما توصل؟",
  "emotion": "neutral",
  "speaker_style": "casual",
  "category": "delivery"
}
```

---

# 2. 🎤 Speech Synthesis Stage (TTS)

<img width="665" height="835" alt="image" src="https://github.com/user-attachments/assets/29d3fbc3-0f5c-4d15-a6af-a214d7442ce1" />


This stage converts text into synthetic speech using a TTS system.

## 🔥 Key Enhancements (IMPORTANT)

### 🎭 1. Emotion-Aware Speech Generation

One of the key improvements in this pipeline is that **speech is not generated in a flat neutral tone**.

Instead, each sample is conditioned with emotional context such as:

* happy 🙂
* angry 😠
* excited 🤩
* neutral 😐
* sad 😔

👉 This makes the dataset significantly more realistic and improves STT robustness to different speaking styles.

---

### 🗣️ 2. Multi-Speaker Design


The system supports **multiple synthetic speakers**, not a single voice.

Each sample is mapped to different speaker identities using a speaker abstraction layer.

#### Why this matters:

Real-world STT systems must handle:

* different voices
* accents
* pitch variations
* speaking styles

👉 This prevents overfitting to a single voice distribution.

---

### 🔊 3. Background Noise Injection (Critical for STT Realism)

A major enhancement in this pipeline is the **introduction of realistic background noise**.

Instead of generating clean studio-like audio, the system intentionally simulates real-world environments such as:

* street noise 🚗
* crowd conversations 🧑‍🤝‍🧑
* cafe ambience ☕
* office background 💻

#### Why this is important:

In real STT applications, models rarely receive clean audio.

They typically face:

* noisy environments
* overlapping speech
* environmental interference

👉 Adding noise during dataset generation significantly improves model robustness and generalization.

---

### ⚙️ Technical Features:

* async batch synthesis
* concurrency control (semaphore)
* speaker mapping abstraction
* structured prompt conditioning

---

### Output:

* WAV audio files
* structured metadata JSONL

---

# 3. 🔍 Review & Quality Control Layer

<img width="667" height="767" alt="image" src="https://github.com/user-attachments/assets/04575c10-a51c-43c8-b670-d25351f75a4e" />


Ensures only high-quality samples enter training.

### Includes:

* STT verification filtering
* rule-based validation
* accepted / rejected dataset split
* optional manual review support

---

# 4. 🌫️ Adding background noise Stage

<img width="565" height="844" alt="image" src="https://github.com/user-attachments/assets/136ca5f7-2035-4435-9422-f546664a88e8" />


Enhances dataset realism further.

### Features:

* SNR-based noise mixing
* multiple noise types (street, crowd, etc.)
* clean + noisy version preservation
* duplicate prevention system

### Output:

* original clean audio
* augmented noisy audio
* linked metadata

---

# 5. 📦 Dataset Formatting Stage

<img width="673" height="849" alt="image" src="https://github.com/user-attachments/assets/93c8b7ef-3eac-40ac-aa43-a03042332b11" />


Converts pipeline output into **training-ready STT format**.

### Output Structure:

```text id="dataset_format"
ready_dataset/
├── wavs/
└── metadata.csv
```

### Standardization:

* 16kHz sample rate
* mono audio
* normalized amplitude
* sequential file naming

---

# ⚙️ Reliability Engineering

The pipeline is designed for long-running production workloads.

### Features:

* async execution (asyncio)
* batch processing
* concurrency limits (semaphore)
* checkpointing via JSONL
* resumable execution
* structured logging (loguru)

---

# 📊 Output Format

### metadata.csv

```csv id="csv_output"
audio,transcription
wavs/0001.wav,السلام عليكم
wavs/0002.wav,عايز أطلب دليفري
```

### Audio format:

* WAV
* 16kHz
* mono PCM

---

# 🔑 Key Engineering Decisions

| Decision                   | Reason                             |
| -------------------------- | ---------------------------------- |
| emotions in speech         | improve natural variation          |
| multi-speaker system       | avoid single-voice bias            |
| background noise injection | simulate real-world STT conditions |
| JSONL intermediate format  | scalability & resumability         |
| async architecture         | handle large-scale generation      |


---

---

# 📁 Project Structure

```text
Synthetic-Speech-Data-Pipeline-For-STT/
├── src/                        # Core logic and pipeline blocks
│   ├── synthetic_data_gen_block/ # Stage 1: Text Generation
│   ├── audio_generation_block/   # Stage 2: TTS Synthesis
│   ├── review_and_eval_block/    # Stage 3: Quality Control
│   ├── add_background_noise_block/ # Stage 4: Augmentation
│   ├── data_formating_block/     # Stage 5: Dataset Formatting
│   ├── utils/                    # Shared utilities (audio, text, etc.)
│   └── full_pipeline.py          # Orchestration layer
├── app.py                      # Gradio Web GUI
├── main.py                     # CLI Pipeline Runner
├── Dockerfile                  # Containerization setup
├── pyproject.toml              # UV Dependency management
└── README.md                   # Documentation
```

---

# 🚀 Getting Started

This project uses **[uv](https://github.com/astral-sh/uv)** for extremely fast and reliable Python package management.

### 1. Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone the repository
git clone https://github.com/Veto2922/Synthetic-Speech-Data-Pipeline-For-STT.git
cd Synthetic-Speech-Data-Pipeline-For-STT

# Install dependencies and create virtual environment
uv sync
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory (refer to `.env.example`):

```bash
GEMINI_API_KEY=your_api_key_here
```

---

# 💻 Running the Project

### 🖥️ Gradio Web Interface (Recommended)

To launch the interactive GUI for controlling the pipeline:

```bash
uv run python app.py
```
Then open `http://127.0.0.1:7860` in your browser.

### ⚙️ Command Line Interface

To run the full pipeline via CLI:

```bash
uv run python main.py
```

---

# 🐳 Docker Deployment

You can also run the entire system using Docker:

```bash
# Build the image
docker build -t stt-pipeline .

# Run the container
docker run -p 7860:7860 --env-file .env ssdp-pipeline
```

---

# 📊 Sample Dataset

You can find a sample of the data generated by this pipeline on Hugging Face:
🔗 **[Egyptian Arabic Synthetic STT Dataset](https://huggingface.co/datasets/Abdelrahman2922/Egyptian-Arabic-synthetic-stt)**

---

# 🧾 Final Summary

This pipeline implements a **production-grade synthetic speech generation system** optimized for Egyptian Arabic STT training. What makes it strong is not just synthesis, but **realism engineering**, achieved through:

* emotional speech conditioning 🎭
* multi-speaker synthesis 🗣️
* background noise simulation 🌫️
* structured data generation 📦

The goal is to bridge the gap between synthetic and real-world speech distributions, improving downstream STT robustness in realistic environments.


