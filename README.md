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
