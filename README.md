
# Synthetic Speech Data Pipeline for STT (S.S.D.P)

## Overview

The Synthetic Speech Data Pipeline (S.S.D.P) is an end-to-end system designed to generate **high-quality, Egyptian Arabic speech datasets** for Speech-to-Text (STT) model training.

The main objective is not only to synthesize speech, but to **simulate real-world acoustic conditions** that STT systems encounter in production.

In real environments, speech is rarely clean — it includes:

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

# 🧾 Final Summary

This pipeline implements a **production-grade synthetic speech generation system** optimized for Egyptian Arabic STT training.

What makes it strong is not just synthesis, but **realism engineering**, achieved through:

* emotional speech conditioning 🎭
* multi-speaker synthesis 🗣️
* background noise simulation 🌫️
* structured data generation 📦

The goal is to bridge the gap between synthetic and real-world speech distributions, improving downstream STT robustness in realistic environments.

