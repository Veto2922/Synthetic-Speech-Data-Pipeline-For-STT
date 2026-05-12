import gradio as gr
import os
import json
import asyncio
import zipfile
from pathlib import Path
from dotenv import load_dotenv
from src.full_pipeline import PipelineRunner
from src.synthetic_data_gen_block.shcemas.enums_schemas import Category
import pandas as pd
import shutil

load_dotenv()


# Helper function to zip a directory
def zip_directory(directory_path, zip_path):
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(directory_path):
            for file in files:
                zipf.write(
                    os.path.join(root, file),
                    os.path.relpath(
                        os.path.join(root, file), os.path.join(directory_path, "..")
                    ),
                )


CUSTOM_CSS = """
.gradio-container {
    background: linear-gradient(135deg, #1e1e2f 0%, #2a2a40 100%);
    color: #ffffff;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}
.gr-button-primary {
    background: linear-gradient(90deg, #6366f1 0%, #a855f7 100%) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
}
.gr-button-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
}
.gr-tabs {
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
}
.gr-tab-button {
    color: rgba(255, 255, 255, 0.6) !important;
}
.gr-tab-button-active {
    color: #ffffff !important;
    border-bottom: 2px solid #6366f1 !important;
}
.gr-box {
    background: rgba(255, 255, 255, 0.05) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 12px !important;
}
"""


class GradioApp:
    def __init__(self):
        self.runner = None
        self.project_name = ""
        self.api_key = ""

    def initialize_runner(self, api_key, project_name, categories):
        if not api_key:
            return "❌ Please enter a valid Gemini API Key."
        if not project_name:
            return "❌ Please enter a Project Name."
        if not categories:
            return "❌ Please select at least one category."

        self.api_key = api_key
        self.project_name = project_name
        try:
            self.runner = PipelineRunner(
                GEMINI_API_KEY=api_key, Project_Name=project_name, categories=categories
            )
            return f"✅ Pipeline Runner initialized for project: **{project_name}**"
        except Exception as e:
            return f"❌ Error initializing runner: {str(e)}"

    async def run_text_gen(self, samples_per_category, batch_size, model_name):
        if not self.runner:
            return None, "❌ Error: Runner not initialized."

        try:
            # Update runner's model if it changed
            if self.runner.TEXT_MODEL_NAME != model_name:
                from langchain.chat_models import init_chat_model

                self.runner.TEXT_MODEL_NAME = model_name
                self.runner.model = init_chat_model(
                    model_name,
                    model_provider="google-genai",
                    temperature=0.7,
                    max_tokens=1000,
                    api_key=self.api_key,
                )

            await self.runner.run_text_generation(
                samples_per_category=int(samples_per_category),
                batch_size=int(batch_size),
            )

            # Load sample data for preview
            text_path = self.runner.PROJECT_DIR / "synthetic_text_dataset.jsonl"
            samples = []
            if text_path.exists():
                with open(text_path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        samples.append(json.loads(line))
                        if i >= 4:
                            break

            df = pd.DataFrame(samples)
            return df, "✅ Text Generation Complete."
        except Exception as e:
            return None, f"❌ Error during Text Gen: {str(e)}"

    async def run_tts_gen(self, model_name):
        if not self.runner:
            return None, None, "❌ Error: Runner not initialized."

        try:
            self.runner.TTS_MODEL_NAME = model_name
            await self.runner.run_tts_generation()

            # Load sample audio for preview
            audio_jsonl = self.runner.PROJECT_DIR / "synthetic_audio_dataset.jsonl"
            audio_samples = [None, None]
            if audio_jsonl.exists():
                with open(audio_jsonl, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if i >= 2:
                            break
                        data = json.loads(line)
                        audio_path = data.get("audio_path")
                        if audio_path:
                            # Ensure path is absolute for Gradio
                            abs_path = os.path.abspath(audio_path)
                            audio_samples[i] = abs_path

            return audio_samples[0], audio_samples[1], "✅ TTS Generation Complete."
        except Exception as e:
            return None, None, f"❌ Error during TTS Gen: {str(e)}"

    async def run_val(self, min_dur, max_dur, min_rms, max_wer, model_name):
        if not self.runner:
            return None, None, "❌ Error: Runner not initialized."

        try:
            self.runner.STT_MODEL_NAME = model_name
            await self.runner.run_validation(
                min_duration=float(min_dur),
                max_duration=float(max_dur),
                min_rms=float(min_rms),
                max_wer=float(max_wer),
            )

            # Count accepted and rejected records
            accepted_path = self.runner.PROJECT_DIR / "accepted.jsonl"
            rejected_path = self.runner.PROJECT_DIR / "rejected.jsonl"

            val_samples = [None, None]
            acc_count = 0
            if accepted_path.exists():
                with open(accepted_path, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        acc_count += 1
                        if i < 2:
                            data = json.loads(line)
                            audio_path = data.get("audio_path")
                            if audio_path:
                                val_samples[i] = os.path.abspath(audio_path)

            rej_count = 0
            if rejected_path.exists():
                with open(rejected_path, "r", encoding="utf-8") as f:
                    rej_count = sum(1 for _ in f)

            return (
                val_samples[0],
                val_samples[1],
                acc_count,
                rej_count,
                f"✅ Validation Complete. Found {acc_count} accepted and {rej_count} rejected samples.",
            )
        except Exception as e:
            return None, None, 0, 0, f"❌ Error during Validation: {str(e)}"

    def run_add_background_noise(self, snr_db):
        if not self.runner:
            return None, None, "❌ Error: Runner not initialized."

        try:
            self.runner.run_augmentation(snr_db=int(snr_db))

            # Load sample audio
            final_metadata = self.runner.PROJECT_DIR / "final_dataset_metadata.jsonl"
            samples = [None, None]
            if final_metadata.exists():
                with open(final_metadata, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if i >= 2:
                            break
                        data = json.loads(line)
                        audio_path = data.get("audio_path")
                        if audio_path:
                            samples[i] = os.path.abspath(audio_path)

            return samples[0], samples[1], "✅ Background Noise Added Successfully."
        except Exception as e:
            return None, None, f"❌ Error during adding noise: {str(e)}"

    def run_format(self, sr, mono, norm):
        if not self.runner:
            return None, "❌ Error: Runner not initialized."

        try:
            self.runner.run_formatting(
                target_sample_rate=int(sr), mono=bool(mono), normalize=bool(norm)
            )

            # Prepare zip for download
            zip_name = f"{self.project_name}_formatted.zip"
            zip_path = self.runner.PROJECT_DIR / zip_name
            zip_directory(self.runner.OUTPUT_DATASET_DIR, zip_path)

            return str(zip_path), "✅ Formatting Complete. Download your dataset below."
        except Exception as e:
            return None, f"❌ Error during Formatting: {str(e)}"

    async def run_full_pipeline(
        self,
        samples_per_category,
        batch_size,
        text_model,
        tts_model,
        stt_model,
        progress=gr.Progress(),
    ):
        if not self.runner:
            return None, None, None, "❌ Error: Runner not initialized."

        try:
            # 1. Text Generation
            progress(0, desc="🚀 Starting End-to-End Pipeline...")
            progress(0.1, desc="📝 Stage 1: Generating Synthetic Text...")
            await self.run_text_gen(samples_per_category, batch_size, text_model)

            # 2. TTS Generation
            progress(0.3, desc="🎙️ Stage 2: TTS Audio Generation...")
            await self.run_tts_gen(tts_model)

            # 3. Validation
            progress(0.5, desc="🧪 Stage 3: Quality Validation...")
            await self.run_val(1.0, 30.0, 0.005, 0.3, stt_model)

            # 4. Add Background Noise
            progress(0.7, desc="🔊 Stage 4: Adding Background Noise...")
            self.run_add_background_noise(10)

            # 5. Formatting
            progress(0.9, desc="📦 Stage 5: Final Formatting...")
            zip_path, _ = self.run_format(16000, True, True)

            progress(1.0, desc="✅ Pipeline Complete!")

            # Collect some audio samples for preview
            final_metadata = self.runner.PROJECT_DIR / "final_dataset_metadata.jsonl"
            samples = [None, None]
            if final_metadata.exists():
                with open(final_metadata, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if i >= 2:
                            break
                        data = json.loads(line)
                        samples[i] = os.path.abspath(data.get("audio_path"))

            # Collect stats
            acc_count = 0
            if (self.runner.PROJECT_DIR / "accepted.jsonl").exists():
                with open(
                    self.runner.PROJECT_DIR / "accepted.jsonl", "r", encoding="utf-8"
                ) as f:
                    acc_count = sum(1 for _ in f)

            rej_count = 0
            if (self.runner.PROJECT_DIR / "rejected.jsonl").exists():
                with open(
                    self.runner.PROJECT_DIR / "rejected.jsonl", "r", encoding="utf-8"
                ) as f:
                    rej_count = sum(1 for _ in f)

            return (
                samples[0],
                samples[1],
                zip_path,
                f"✅ Full Pipeline Execution Successful. (Accepted: {acc_count}, Rejected: {rej_count})\nResults ready for download.",
            )

        except Exception as e:
            return None, None, None, f"❌ Error during Full Pipeline: {str(e)}"


app_logic = GradioApp()

GEMINI_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-2.5-flash-preview-tts",
    "gemini-3.1-flash-tts-preview",
]

with gr.Blocks() as demo:
    gr.Markdown("# 🚀 Advanced STT Synthetic Data Pipeline")
    gr.Markdown(
        "Transform your ideas into high-quality speech datasets with Gemini-powered synthetic data generation."
    )

    with gr.Tabs():
        with gr.Tab("🛠️ 1. Configuration"):
            with gr.Column(elem_classes="gr-box"):
                with gr.Row():
                    api_key_input = gr.Textbox(
                        label="Gemini API Key",
                        placeholder="Enter your API key here...",
                        type="password",
                        value="",
                    )
                    project_name_input = gr.Textbox(
                        label="Project Name", value="project_stt_v1"
                    )

                categories_input = gr.CheckboxGroup(
                    choices=[cat.value for cat in Category],
                    label="Select Target Categories",
                    value=[cat.value for cat in list(Category)[:5]],
                )

                init_btn = gr.Button("🚀 Initialize Pipeline", variant="primary")
                init_status = gr.Markdown()

        with gr.Tab("📝 2. Text Generation"):
            with gr.Column(elem_classes="gr-box"):
                gr.Markdown("""
                **Calculation Note:**
                `number of samples = samples_per_category * number of categories = 5 * 5 = 25 samples per each stage`
                """)
                with gr.Row():
                    text_model_input = gr.Dropdown(
                        choices=GEMINI_MODELS,
                        value="gemini-2.5-flash",
                        label="Gemini Text Model",
                    )
                    samples_per_cat = gr.Number(label="Samples per Category", value=2)
                    batch_size = gr.Number(label="Batch Size", value=10)

                text_gen_btn = gr.Button("✨ Generate Synthetic Text")
                text_preview = gr.DataFrame(label="Generated Text Samples (Preview)")
                text_status = gr.Markdown()

        with gr.Tab("🎙️ 3. TTS Generation"):
            with gr.Column(elem_classes="gr-box"):
                tts_model_input = gr.Dropdown(
                    choices=GEMINI_MODELS,
                    value="gemini-2.5-flash-preview-tts",
                    label="Gemini TTS Model",
                )
                tts_gen_btn = gr.Button("🔊 Generate Audio (TTS)")
                with gr.Row():
                    tts_audio_1 = gr.Audio(label="Sample 1", type="filepath")
                    tts_audio_2 = gr.Audio(label="Sample 2", type="filepath")
                tts_status = gr.Markdown()

        with gr.Tab("🧪 4. Validation"):
            with gr.Column(elem_classes="gr-box"):
                with gr.Row():
                    stt_model_input = gr.Dropdown(
                        choices=GEMINI_MODELS,
                        value="gemini-2.5-flash-lite",
                        label="Gemini STT Model",
                    )
                    min_dur = gr.Slider(0.1, 5.0, value=1.0, label="Min Duration (s)")
                    max_dur = gr.Slider(5.0, 60.0, value=30.0, label="Max Duration (s)")
                with gr.Row():
                    min_rms = gr.Slider(0.001, 0.1, value=0.005, label="Min RMS")
                    max_wer = gr.Slider(0.0, 1.0, value=0.3, label="Max WER")

                val_btn = gr.Button("🔍 Run Quality Validation")
                with gr.Row():
                    accepted_count_out = gr.Number(
                        label="✅ Accepted Samples", value=0, interactive=False
                    )
                    rejected_count_out = gr.Number(
                        label="❌ Rejected Samples", value=0, interactive=False
                    )
                with gr.Row():
                    val_audio_1 = gr.Audio(label="Validated Sample 1", type="filepath")
                    val_audio_2 = gr.Audio(label="Validated Sample 2", type="filepath")
                val_status = gr.Markdown()

        with gr.Tab("🔊 5. Add Background Noise"):
            with gr.Column(elem_classes="gr-box"):
                snr_db_input = gr.Slider(
                    0, 30, value=10, label="Background Noise SNR (dB)"
                )
                noise_btn = gr.Button("🌈 Add Background Noise")
                with gr.Row():
                    noise_audio_1 = gr.Audio(
                        label="Noise Added Sample 1", type="filepath"
                    )
                    noise_audio_2 = gr.Audio(
                        label="Noise Added Sample 2", type="filepath"
                    )
                noise_status = gr.Markdown()

        with gr.Tab("📦 6. Export"):
            with gr.Column(elem_classes="gr-box"):
                with gr.Row():
                    sample_rate_input = gr.Number(
                        label="Target Sample Rate (Hz)", value=16000
                    )
                    mono_input = gr.Checkbox(label="Mono Channel", value=True)
                    norm_input = gr.Checkbox(label="Normalize Volume", value=True)

                format_btn = gr.Button("🎁 Build & Export Dataset", variant="primary")
                download_file = gr.File(label="Download Final Dataset (ZIP)")
                format_status = gr.Markdown()
        with gr.Tab("🚀 End-to-End"):
            with gr.Column(elem_classes="gr-box"):
                gr.Markdown("### Run Full Pipeline with Default Settings")
                gr.Markdown("""
                **Configuration Note:**
                - Stage 1: Text Generation (5 samples per category)
                - Stage 2: TTS Generation
                - Stage 3: Validation (Dur: 1-30s, RMS: 0.005, WER: 0.3)
                - Stage 4: Add Background Noise (SNR: 10dB)
                - Stage 5: Formatting (16k, Mono, Norm)
                
                **Calculation:**
                `number of samples = samples_per_category * number of categories = 5 * 5 = 25 samples per each stage`
                """)

                with gr.Row():
                    full_text_model = gr.Dropdown(
                        choices=GEMINI_MODELS,
                        value="gemini-2.5-flash",
                        label="Text Model",
                    )
                    full_tts_model = gr.Dropdown(
                        choices=GEMINI_MODELS,
                        value="gemini-2.5-flash-preview-tts",
                        label="TTS Model",
                    )
                    full_stt_model = gr.Dropdown(
                        choices=GEMINI_MODELS,
                        value="gemini-2.5-flash-lite",
                        label="STT Model",
                    )

                with gr.Row():
                    full_samples_per_cat = gr.Number(
                        label="Samples per Category", value=5
                    )
                    full_batch_size = gr.Number(label="Batch Size", value=10)

                run_all_btn = gr.Button("🔥 Run Entire Pipeline", variant="primary")

                with gr.Row():
                    full_audio_1 = gr.Audio(label="Result Sample 1", type="filepath")
                    full_audio_2 = gr.Audio(label="Result Sample 2", type="filepath")

                full_download = gr.File(label="Download Full Dataset (ZIP)")
                full_status = gr.Markdown()

    # Event Handlers
    init_btn.click(
        app_logic.initialize_runner,
        inputs=[api_key_input, project_name_input, categories_input],
        outputs=init_status,
    )

    text_gen_btn.click(
        app_logic.run_text_gen,
        inputs=[samples_per_cat, batch_size, text_model_input],
        outputs=[text_preview, text_status],
    )

    tts_gen_btn.click(
        app_logic.run_tts_gen,
        inputs=[tts_model_input],
        outputs=[tts_audio_1, tts_audio_2, tts_status],
    )

    val_btn.click(
        app_logic.run_val,
        inputs=[min_dur, max_dur, min_rms, max_wer, stt_model_input],
        outputs=[
            val_audio_1,
            val_audio_2,
            accepted_count_out,
            rejected_count_out,
            val_status,
        ],
    )

    noise_btn.click(
        app_logic.run_add_background_noise,
        inputs=[snr_db_input],
        outputs=[noise_audio_1, noise_audio_2, noise_status],
    )

    format_btn.click(
        app_logic.run_format,
        inputs=[sample_rate_input, mono_input, norm_input],
        outputs=[download_file, format_status],
    )

    run_all_btn.click(
        app_logic.run_full_pipeline,
        inputs=[
            full_samples_per_cat,
            full_batch_size,
            full_text_model,
            full_tts_model,
            full_stt_model,
        ],
        outputs=[full_audio_1, full_audio_2, full_download, full_status],
    )

if __name__ == "__main__":
    demo.launch(
        theme=gr.themes.Default(),
        css=CUSTOM_CSS,
        server_name="0.0.0.0",
        server_port=7860,
    )
