# Synthetic-Speech-Data-Pipeline-For-STT


# Text Generation Block — README Documentation

## Overview

The `Text Generation Block` is the first stage of the Synthetic Speech Data Pipeline (S.S.D.P).
Its responsibility is to generate high-quality Egyptian Arabic text prompts that will later be synthesized into speech using a TTS system.

The generated prompts are specifically designed for downstream Speech-To-Text (STT) training, with a strong focus on:

* realism
* dialect correctness
* diversity
* structured metadata
* TTS compatibility
* long-running pipeline reliability

This block was intentionally designed as an isolated modular component to ensure:

* High Cohesion
* Low Coupling
* Extensibility
* Reusability
* Production-readiness

The block does not contain any TTS-specific implementation logic.
Instead, it produces structured semantic prompt records that can later be consumed by independent audio synthesis systems.

---

# Goals

The block aims to:

* Generate realistic Egyptian Arabic utterances
* Simulate real-world conversational speech
* Produce metadata-rich prompts for controllable TTS synthesis
* Support dataset diversity across multiple conversational domains
* Normalize and validate text before entering downstream stages
* Support scalable asynchronous generation workflows

---

# Architecture

## High-Level Flow

```text
Category Sampling
        ↓
Prompt Construction
        ↓
LLM Structured Generation
        ↓
Text Normalization
        ↓
Validation
        ↓
Metadata Enrichment
        ↓
JSONL Persistence
```

---

# Component Design

The block is organized into multiple isolated responsibilities.

## 1. Schema Layer

Responsible for defining strict structured contracts between the LLM and downstream systems.

Implemented using:

* Pydantic
* Python Enums

### Responsibilities

* Enforce structured outputs
* Restrict categorical values
* Validate generated records
* Improve consistency and reliability

### Example Controlled Categories

* Emotion
* Speaker Style
* Speaking Rate
* Background Noise
* Conversation Category

This prevents the LLM from hallucinating unsupported values.

---

## 2. Prompt Engineering Layer

The system prompt was designed specifically for Egyptian Arabic STT dataset generation.

### Main Objectives

* Generate only Egyptian Arabic dialect
* Prevent Modern Standard Arabic (MSA)
* Force numbers to be written as words
* Preserve English technical terms
* Preserve punctuation
* Avoid emojis and noisy symbols
* Ensure schema compliance

### Example Constraints

```text
- Numbers MUST be written in words
- English product words remain in English
- Output MUST be valid JSON only
```

This significantly improves downstream STT data quality.

---

# Egyptian Arabic Design Considerations

Egyptian Arabic introduces several practical STT challenges:

| Challenge                       | Mitigation                           |
| ------------------------------- | ------------------------------------ |
| Non-standard spelling           | Text normalization                   |
| Arabic-English code switching   | Explicit schema field                |
| Numeric pronunciation ambiguity | Numbers written as words             |
| Informal conversational speech  | Dialect-focused prompting            |
| TTS pronunciation instability   | Metadata-guided synthesis            |
| Synthetic monotony              | Diverse speaking styles and emotions |

The system was intentionally designed to expose these variations instead of suppressing them.

---

# Structured Semantic Metadata

Instead of generating plain text only, the system generates metadata-rich prompt records.

Example:

```json
{
  "text": "ابعتلي ال location لما توصل.",
  "emotion": "happy",
  "speaker_style": "casual",
  "speaking_rate": "normal",
  "background_noise": "street_noise"
}
```

This metadata is later used by downstream TTS systems to control:

* prosody
* speaking rate
* emotional expression
* environmental realism
* speaker simulation

---

# Controlled Diversity Strategy

To avoid dataset collapse toward a small subset of scenarios, the system uses controlled category sampling.

## Categories Include

* delivery
* shopping
* healthcare
* transportation
* customer_support
* emergency
* restaurant
* news

This improves:

* dataset balance
* speaker diversity
* acoustic variety
* linguistic coverage

---

# Async Generation Architecture

Large-scale synthetic data generation is inherently long-running.

To address this, the system was designed with asynchronous execution support.

Implemented using:

```python
asyncio
```

---

# Parallel Generation

The pipeline supports concurrent LLM requests using:

```python
asyncio.gather()
```

This allows multiple prompts to be generated simultaneously.

Benefits:

* faster throughput
* scalable generation
* efficient API utilization

---

# Concurrency Control

A semaphore-based concurrency limiter was implemented:

```python
asyncio.Semaphore(max_concurrent_tasks)
```

Purpose:

* prevent provider overload
* avoid rate limiting
* stabilize generation workloads

---

# Provider-Level Batching

The system supports provider-native batching using:

```python
structured_model.abatch()
```

This reduces:

* API overhead
* request latency
* total generation cost

The batching layer splits categories into provider batches for efficient processing.

---

# JSONL Persistence & Incremental Saving

Generated records are incrementally saved to disk in JSONL format.

Example:

```json
{"id":"...","text":"..."}
{"id":"...","text":"..."}
```

---

# Why JSONL?

JSONL was intentionally selected because it:

* supports streaming workflows
* scales to large datasets
* enables resumability
* allows incremental writes
* integrates well with ML pipelines

This also acts as a lightweight caching mechanism.

---

# Resumability & Fault Tolerance

Incremental persistence ensures generation progress is not lost if:

* the process crashes
* API failures occur
* long-running jobs stop unexpectedly

This improves reliability for large-scale generation.

---

# Logging & Observability

Structured logging was implemented using:

```python
loguru
```

The system logs:

* generation start/end
* batch execution
* validation failures
* processing errors
* generation durations

Example:

```text
✅ Sample generated | topic=delivery | status=generated
```

This improves observability and debugging.

---

# Text Normalization Pipeline

A dedicated normalization layer was implemented before persistence.

## Operations Include

* Unicode normalization
* Emoji removal
* Arabic diacritics removal
* Tatweel removal
* Weird symbol cleanup
* Digit removal
* Whitespace normalization

This ensures downstream STT consistency.

---

# Validation Layer

Additional validation checks were implemented beyond LLM prompting.

## Examples

### Digit Validation

Ensures numeric digits do not appear in text.

```python
validate_no_digits()
```

### Schema Validation

Ensures strict compliance with the expected output schema.

Implemented using:

```python
Pydantic validation
```

---

# Metadata Enrichment

System-generated metadata is added after LLM generation.

Examples:

* id
* created_at
* schema_version
* status
* review_status
* speaker_id

These fields are intentionally generated outside the LLM to improve determinism and consistency.

---

# Separation of Concerns

The block intentionally separates:

| Responsibility              | Owner            |
| --------------------------- | ---------------- |
| Semantic content generation | LLM              |
| System metadata             | Pipeline         |
| Validation                  | Validation Layer |
| Persistence                 | Storage Layer    |
| Concurrency                 | Async Layer      |

This improves modularity and maintainability.

---

# Reliability Features Implemented

## Implemented

* Async generation
* Parallel processing
* Provider batching
* Incremental persistence
* Structured logging
* Schema validation
* Text normalization
* Concurrency control


---

# Output Format

Final records are exported as JSONL.

Example:

```json
{
  "id": "...",
  "schema_version": "1.0",
  "text": "الو، انت وصلت فين؟",
  "emotion": "neutral",
  "speaker_style": "phone_call",
  "status": "generated"
}
```

This format was selected because it is:

* training-friendly
* streamable
* scalable
* easy to integrate with PyTorch/HuggingFace datasets

---

# Design Philosophy

This block was intentionally designed as:

```text
Semantic Speech Data Generation Infrastructure
```

rather than a simple text generation script.

The focus was placed on:

* data quality
* pipeline reliability
* modularity
* STT-awareness
* scalability
* production-oriented engineering practices

rather than only maximizing generation speed or volume.



# Audio Generation Block (TTS Block)

## Overview

The Audio Generation Block is responsible for converting structured Egyptian Arabic text prompts into synthetic speech audio files suitable for Speech-To-Text (STT) training.

This block receives validated prompt records from the Text Generation Block and produces:

* WAV audio files
* Audio metadata manifests (`JSONL`)
* Speaker-conditioned synthetic speech
* Training-ready audio artifacts

The design focuses on:

* Modularity
* Scalability
* Async execution
* Cross-platform compatibility
* Dataset traceability
* STT-oriented data quality

---

# Architecture

```text
Structured Prompt JSON
        │
        ▼
TTSPromptBuilder
        │
        ▼
Gemini TTS Service
        │
        ├── Voice Selection
        ├── Async Generation
        ├── Concurrency Control
        ├── WAV Export
        ├── Metadata Logging
        └── Caching / Skip Existing
        │
        ▼
Generated WAV Files
        │
        ▼
Audio Metadata JSONL
```

---

# Input Format

The block consumes structured prompt records generated from the previous stage.

Example:

```json
{
  "id": "f2e1c0d5",
  "text": "ممكن تبعتلي ال location على WhatsApp؟",
  "emotion": "speak cheerfully and positively",
  "speaker_style": "use a casual conversational tone",
  "speaking_rate": "speaking_rate: normal",
  "energy": "with moderate energy",
  "background_noise": "clean audio",
  "speaker_id": "2"
}
```

---

# Design Choices and Rationale

## 1. Structured Prompt Conditioning

Instead of sending raw text directly to the TTS model, the system builds a structured prompt containing:

* Emotion
* Speaking style
* Speaking rate
* Energy level

Example:

```text
speak cheerfully and positively,
use a casual conversational tone,
speaking_rate: normal,
with moderate energy.

Say in Egyptian Arabic:
ممكن تبعتلي ال location على WhatsApp؟
```

### Why?

Synthetic STT datasets become weak if every sample sounds identical.

Conditioning the TTS model increases:

* Acoustic diversity
* Prosodic diversity
* Speaker variability
* Real-world robustness

This helps reduce overfitting to a single synthetic voice style.

---

# 2. Speaker Mapping Layer

The system maps internal `speaker_id` values to Gemini prebuilt voices.

Example:

```python
self.speaker_id_map = {
    "1": "Zephyr",
    "2": "Kore",
    "3": "Algenib",
    "4": "Algieba"
}
```

### Why?

This abstraction layer decouples:

```text
Dataset speaker identity
FROM
Provider-specific voice names
```

Benefits:

* Easier provider migration
* Easier voice replacement
* Consistent dataset metadata
* Better maintainability

---

# 3. Async Audio Generation

Audio synthesis is implemented asynchronously using:

```python
asyncio
asyncio.to_thread()
asyncio.gather()
```

### Why?

TTS generation is a long-running IO-bound task.

Async execution enables:

* Parallel synthesis
* Higher throughput
* Better GPU/API utilization
* Faster dataset generation

This is especially important for large-scale synthetic dataset generation.

---

# 4. Concurrency Control

The service uses:

```python
asyncio.Semaphore(max_concurrent_tasks)
```

### Why?

Without concurrency control:

* API rate limits may be exceeded
* Memory usage may spike
* Provider instability may occur

The semaphore guarantees controlled parallelism and safer scaling behavior.

---

# 5. WAV Export

Generated PCM audio is converted into WAV format.

### Why WAV?

WAV is widely used in STT pipelines because it is:

* Lossless
* Simple to process
* Framework compatible
* Standard for speech datasets

This improves compatibility with:

* Whisper
* NVIDIA NeMo
* Hugging Face datasets
* Kaldi
* SpeechBrain

---

# 6. Metadata Manifest (JSONL)

Each generated audio sample is logged into a JSONL manifest.

Example:

```json
{
  "audio_id": "f2e1c0d5",
  "prompt_id": "f2e1c0d5",
  "audio_path": "audio_outputs/f2e1c0d5.wav",
  "voice_name": "Kore",
  "speaker_id": "2",
  "tts_model": "gemini-2.5-flash-preview-tts",
  "sample_rate": 24000,
  "status": "generated",
  "review_status": "pending"
}
```

### Why JSONL?

JSONL provides:

* Append-only writing
* Streaming compatibility
* Easy sharding
* Scalable dataset processing
* Easy downstream ingestion

This format is commonly used in ML data pipelines.

---

# 7. Caching / Skip Existing Files

Before generation, the system checks:

```python
if output_path.exists():
```

### Why?

This prevents:

* Duplicate generation
* Wasted API calls
* Recomputing existing audio
* Accidental overwrites

This also improves resumability for interrupted jobs.

---

# 8. Cross-Platform Path Handling

All paths use `pathlib.Path`.

### Why?

This ensures compatibility across:

* Windows
* Linux
* macOS
* Docker containers
* Cloud environments

Avoiding hardcoded separators improves deployment portability.

---

# 9. Logging and Observability

The pipeline uses `loguru` for structured logging.

Example logs:

```text
🎤 Generating audio | id=abc123
✅ Audio generated | id=abc123 | time=2.14s
❌ Audio generation failed | id=abc123
```

### Why?

Long-running pipelines require observability for:

* Monitoring
* Debugging
* Failure tracking
* Performance analysis

---

# STT-Oriented Considerations

The block was designed specifically for STT dataset generation rather than generic TTS usage.

Key considerations:

## Egyptian Arabic Focus

The prompts are generated in spoken Egyptian Arabic rather than Modern Standard Arabic (MSA).

This is important because:

* Most speech systems underperform on dialectal Arabic
* Egyptian Arabic contains heavy code-switching
* Pronunciation varies significantly from written Arabic

---

## Controlled Acoustic Diversity

The pipeline intentionally varies:

* Emotion
* Speaking style
* Energy
* Speaking rate
* Speaker identity

This helps simulate realistic speech conditions.

---

## Code-Switching Support

The generated prompts may contain mixed Arabic-English terms such as:

```text
WhatsApp
location
delivery
```

This reflects real conversational Egyptian Arabic.

---

# Reliability Features

The implementation includes several reliability-focused features:

| Feature            | Purpose                    |
| ------------------ | -------------------------- |
| Async execution    | Faster generation          |
| Semaphore          | Concurrency control        |
| JSONL manifests    | Incremental persistence    |
| Caching            | Avoid duplicate generation |
| Logging            | Observability              |
| Structured schemas | Validation and consistency |

---

# Output Artifacts

The block produces:

## 1. Audio Files

```text
audio_outputs/
├── sample_001.wav
├── sample_002.wav
└── ...
```

---

## 2. Metadata Manifest

```text
data/
└── synthetic_audio_dataset.jsonl
```

---

# Limitations

Current limitations include:

* Synthetic voices may still sound less natural than human recordings
* Limited speaker inventory
* No automatic audio quality scoring yet
* No automatic pronunciation verification
* No forced alignment validation

These limitations are expected in the current scope and can be improved in future iterations.

---

# Future Improvements

Potential future upgrades:

* Background noise augmentation
* Automatic STT verification loop
* MOS-style audio quality scoring
* Pronunciation validation
* Retry policies
* Distributed synthesis workers
* Speaker balancing strategies
* Dataset quality dashboards

---

# Conclusion

This block was designed as a scalable and modular synthetic speech generation service focused on Egyptian Arabic STT data generation.

The implementation prioritizes:

* Dataset diversity
* Reliability
* Scalability
* Observability
* Training-readiness

while keeping the architecture extensible for future improvements such as augmentation, validation, and automated review systems.


---



# Synthetic Speech Data Augmentation Pipeline for STT

## Overview

This module is responsible for **audio augmentation and dataset finalization** for Speech-to-Text (STT) training.

The goal is to transform validated synthetic speech samples into a more realistic and production-ready dataset by:

* Adding realistic background noise
* Generating augmented audio variations
* Preserving original clean samples
* Preventing duplicate augmentations
* Building a final scalable metadata dataset
* Increasing acoustic diversity for robust STT training

---

# Pipeline Architecture

```text
                 ┌─────────────────────┐
                 │ accepted.jsonl      │
                 │ validated samples   │
                 └──────────┬──────────┘
                            │
                            ▼
              ┌──────────────────────────┐
              │ AudioAugmentationService │
              └──────────┬───────────────┘
                         │
         ┌───────────────┼────────────────┐
         │                                │
         ▼                                ▼
 ┌─────────────────┐            ┌──────────────────┐
 │ Clean Audio     │            │ Noisy Audio      │
 │ Keep Original   │            │ Add Noise        │
 └────────┬────────┘            └────────┬─────────┘
          │                              │
          ▼                              ▼
 ┌─────────────────┐          ┌─────────────────────┐
 │ Save Metadata   │          │ Generate New WAV    │
 │ with_noise=False│          │ *_with_noise.wav    │
 └────────┬────────┘          └────────┬────────────┘
          │                              │
          └──────────────┬───────────────┘
                         ▼
          ┌────────────────────────────┐
          │ final_dataset_metadata.jsonl │
          └────────────────────────────┘
```

---

# Main Objective

Synthetic TTS audio is usually:

* Too clean
* Too perfect
* Missing environmental variability

This hurts STT model generalization in real-world scenarios.

This augmentation pipeline solves this by introducing:

* Street noise
* Crowd noise
* Realistic acoustic conditions
* Signal-to-noise variations

This significantly improves:

* Robustness
* Noise tolerance
* Real-world transcription quality

---

# Core Components

## 1. Input Dataset

The pipeline starts from:

```text
accepted.jsonl
```

This file contains only validated audio samples that already passed:

* Audio quality validation
* STT verification
* WER filtering

Each record contains:

```json
{
  "audio_id": "...",
  "audio_path": "...",
  "text": "...",
  "background_noise": "background crowd"
}
```

---

# 2. Noise Mapping System

The pipeline maps semantic noise labels to actual WAV files.

Example:

```python
NOISE_MAP = {
    "background street noise": "street_noise.wav",
    "background crowd": "crowd_noise.wav",
}
```

This design allows easy extension with new environments:

* Cafe noise
* Car noise
* Airport announcements
* Office ambience
* Rain
* Keyboard typing

---

# 3. Audio Augmentation Engine

The augmentation engine:

1. Loads clean speech
2. Loads noise audio
3. Resamples noise if needed
4. Randomly crops noise
5. Scales noise using SNR
6. Mixes speech + noise
7. Normalizes final waveform
8. Saves augmented audio

Generated file naming:

```text
original.wav
→
original_with_noise.wav
```

---

# 4. SNR-Based Mixing

The system uses:

```text
Signal-to-Noise Ratio (SNR)
```

to control noise intensity.

Example:

```python
snr_db = 10
```

Lower SNR:

* harder audio
* more realistic
* noisier speech

Higher SNR:

* cleaner audio
* easier transcription

This creates controllable difficulty levels for STT training.

---

# 5. Metadata Finalization

All records are saved into:

```text
final_dataset_metadata.jsonl
```

This file becomes the final training manifest.

It contains:

* Original clean samples
* Augmented noisy samples
* Augmentation metadata
* Parent-child relationships

Example:

```json
{
  "audio_id": "abc_with_noise",
  "parent_audio_id": "abc",
  "with_noise": true,
  "augmentation": {
    "type": "background_noise",
    "noise_type": "background crowd",
    "snr_db": 10
  }
}
```

---

# Duplicate Prevention System

One major challenge in dataset pipelines is:

```text
Repeated augmentation
```

Without protection:

```text
sample.wav
→ sample_with_noise.wav
→ sample_with_noise_with_noise.wav
```

This pipeline prevents this using:

## Existing Audio ID Cache

At startup:

```python
load_existing_audio_ids()
```

loads all processed IDs from:

```text
final_dataset_metadata.jsonl
```

Then before augmentation:

```python
if new_audio_id in EXISTING_AUDIO_IDS:
    skip
```

This guarantees:

* Idempotent processing
* Safe reruns
* No duplicate metadata
* No duplicated WAV generation

---

# Key Features

## Fast and Lightweight

Optimizations include:

* `resample_poly()` for efficient resampling
* Random noise cropping
* Minimal memory overhead
* JSONL streaming

---

## Modular Architecture

Utilities are separated from the service layer.

### Utils

* Audio processing
* JSONL handling
* Noise mixing
* Existing ID loading

### Service Class

Responsible for orchestration:

* dataset iteration
* augmentation logic
* metadata management
* logging

This improves:

* maintainability
* testing
* scalability

---

# Logging System

The pipeline uses Loguru for structured logging.

Example logs:

```text
INFO  Starting augmentation
INFO  Adding background noise
SUCCESS Augmented sample created
WARNING Sample already exists
ERROR Noise file missing
```

This makes debugging and monitoring significantly easier.

---

# Why This Pipeline is Useful for STT

## 1. Improves Generalization

Models trained only on clean TTS data fail in real environments.

Noise augmentation helps the model learn:

* robustness
* speech separation
* noisy phoneme recognition

---

## 2. Simulates Real-World Conditions

The pipeline introduces realistic acoustic variability.

Examples:

* crowd conversations
* traffic
* outdoor environments

This makes training data closer to production data.

---

## 3. Increases Dataset Diversity

From one validated sample:

```text
clean version
+
noisy version
```

This effectively expands the dataset size and variability.

---

## 4. Safer Training Data Generation

The pipeline ensures:

* no corrupted duplicate records
* reproducible augmentation
* traceable metadata
* parent-child sample tracking

---

# Recommended Future Improvements

## Multi-SNR Augmentation

Generate multiple difficulty levels:

```text
sample_snr5.wav
sample_snr10.wav
sample_snr20.wav
```

---

## Parallel Processing

Use:

* asyncio
* multiprocessing
* thread pools

to speed up augmentation on large datasets.

---

## Additional Augmentations

Possible future augmentations:

* Reverberation
* Speed perturbation
* Pitch shifting
* Echo simulation
* Codec compression
* Telephone simulation

---

## Dataset Versioning

Add:

```json
"dataset_version": "v2"
```

for reproducibility and experiment tracking.

---

# Final Result

The pipeline produces:

## Audio Files

```text
audio_outputs/
├── sample.wav
├── sample_with_noise.wav
```

## Metadata

```text
final_dataset_metadata.jsonl
```

Containing:

* clean samples
* noisy samples
* augmentation metadata
* validation information

---

# Final Benefits

This architecture provides:

* scalable STT dataset generation
* realistic noisy speech simulation
* duplicate-safe augmentation
* modular clean design
* production-friendly metadata tracking
* efficient dataset expansion
* improved STT robustness and generalization



# README — STT Dataset Formatting Pipeline

## Overview

After generating and validating synthetic speech data, the next step is preparing the dataset in a format compatible with Speech-to-Text (STT) training frameworks such as:

* Whisper
* Hugging Face Transformers
* NeMo
* ESPnet
* SpeechBrain

This module converts:

```text
final_dataset_metadata.jsonl
```

plus all generated WAV files into a clean, training-ready dataset.

---

# Why We Need a Formatting Stage

Raw synthetic pipelines usually produce:

* scattered audio files
* inconsistent sample rates
* mixed audio channels
* metadata in JSONL format
* paths tied to internal pipelines

Training frameworks require:

* standardized audio format
* clean directory layout
* unified metadata schema
* stable relative paths

This formatting layer solves that.

---

# Selected Dataset Format

## Final Structure

```text
ready_dataset/
├── metadata.csv
└── wavs/
    ├── sample_000001.wav
    ├── sample_000002.wav
    └── ...
```

---

# Why This Format Was Chosen

This structure is widely compatible with modern STT pipelines.

## Advantages

### 1. Whisper Compatibility

Whisper training pipelines commonly use:

```csv
audio,transcription
```

style metadata.

---

### 2. Hugging Face Datasets Compatibility

Easy loading using:

```python
datasets.load_dataset(...)
```

or Pandas.

---

### 3. Simple and Scalable

CSV metadata is:

* lightweight
* streamable
* easy to debug
* easy to edit manually

---

### 4. Portable

The dataset becomes fully self-contained.

You can:

* zip it
* upload to Hugging Face
* train locally
* move across machines

without changing paths.

---

# Final Metadata Schema

## metadata.csv

| audio                  | transcription        |
| ---------------------- | -------------------- |
| wavs/sample_000001.wav | مرحبا كيف حالك       |
| wavs/sample_000002.wav | أريد طلب بيتزا كبيرة |

---

# Audio Standardization

The formatter provides configurable preprocessing:

| Feature         | Purpose                    |
| --------------- | -------------------------- |
| Resampling      | Standardize sample rate    |
| Mono conversion | Reduce training complexity |
| Normalization   | Stable audio amplitude     |
| WAV export      | Maximum STT compatibility  |

---

# Recommended Audio Settings

## Recommended for Whisper

| Setting     | Value    |
| ----------- | -------- |
| Sample Rate | 16000 Hz |
| Channels    | Mono     |
| Format      | WAV      |
| PCM         | 16-bit   |

---

# Why 16kHz Mono?

Most STT systems are optimized for:

```text
16kHz mono speech
```

Benefits:

* lower storage
* faster training
* lower VRAM usage
* reduced preprocessing complexity
* standard speech frequency coverage

Human speech intelligibility mainly lies below:

```text
8kHz
```

Thus:

```text
16kHz sample rate
```

is usually sufficient.

---

# Pipeline Architecture

```text
final_dataset_metadata.jsonl
            │
            ▼
 ┌─────────────────────────┐
 │ DatasetFormatterService │
 └────────────┬────────────┘
              │
    ┌─────────┼──────────┐
    │                    │
    ▼                    ▼
Read Metadata      Process Audio
                         │
                         ▼
              ┌──────────────────┐
              │ Resample Audio   │
              │ Convert to Mono  │
              │ Normalize        │
              └────────┬─────────┘
                       │
                       ▼
               Save WAV Files
                       │
                       ▼
             Generate metadata.csv
                       │
                       ▼
                 ready_dataset/
```

---

# Processing Flow

## Step 1 — Load Metadata

Read:

```text
final_dataset_metadata.jsonl
```

Each record contains:

* audio path
* transcription
* metadata
* augmentation info

---

## Step 2 — Validate Audio

Check:

* file exists
* readable audio
* non-empty transcription

---

## Step 3 — Audio Standardization

Each audio file is:

### Resampled

Example:

```python
target_sample_rate = 16000
```

---

### Converted to Mono

Stereo:

```text
[L, R]
```

becomes:

```text
(L + R) / 2
```

---

### Normalized

Prevents:

* clipping
* unstable loudness

---

## Step 4 — Save Final WAV

Files are renamed into stable sequential names:

```text
sample_000001.wav
sample_000002.wav
```

This avoids:

* OS path issues
* UUID complexity
* duplicate naming problems

---

## Step 5 — Generate metadata.csv

The formatter generates:

```csv
audio,transcription
```

mapping every audio file to its transcript.

---

# Why Sequential File Names?

Instead of:

```text
759c7a5b-78a7.wav
```

we use:

```text
sample_000001.wav
```

Benefits:

* cleaner datasets
* easier debugging
* deterministic ordering
* easier sharding

---

# Configurable Features

The formatter should support configurable parameters.

## Example

```python
formatter = DatasetFormatterService(
    target_sample_rate=16000,
    mono=True,
    normalize_audio=True,
)
```

---

# Recommended Future Extensions

## Train / Validation / Test Split

Automatically generate:

```text
train.csv
valid.csv
test.csv
```

---

## Hugging Face Export

Direct export into:

```python
DatasetDict
```

---

## Duration Filtering

Remove:

* too short clips
* too long clips

---

## Language Filtering

Support multilingual datasets.

---

## Dataset Statistics

Generate:

* total hours
* average duration
* vocabulary size
* speaker distribution

---

# Example Final Dataset

```text
ready_dataset/
├── metadata.csv
└── wavs/
    ├── sample_000001.wav
    ├── sample_000002.wav
    ├── sample_000003.wav
    └── sample_000004.wav
```

metadata.csv

```csv
audio,transcription
wavs/sample_000001.wav,السلام عليكم
wavs/sample_000002.wav,أريد كوب قهوة
```

---

# Key Benefits of This Design

## Framework Agnostic

Works with nearly all STT frameworks.

---

## Production Ready

Clean separation between:

* metadata
* audio
* augmentation pipeline

---

## Easy to Scale

Supports:

* millions of files
* distributed storage
* cloud training

---

## Reproducible

Deterministic naming + CSV metadata.

---

# Final Goal

This formatting stage transforms synthetic validated audio into:

```text
A clean, standardized, training-ready STT dataset
```

suitable for:

* Whisper fine-tuning
* Arabic ASR training
* multilingual speech models
* noisy speech robustness training
* production-grade STT pipelines
