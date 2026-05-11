import wave
from pathlib import Path
import numpy as np

# Note: In the notebook, BASE_DIR was Path.cwd().parent
# In a modular structure, we should probably be more specific or allow it to be passed.
# However, I'll stick to the logic provided or use a relative path logic.
# I'll define a constant for the project root if possible, or assume it's called from root.

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def resolve_audio_path(audio_path: str | Path) -> Path:
    audio_path = Path(audio_path)
    if audio_path.is_absolute():
        return audio_path

    # Try relative to project root
    full_path = (PROJECT_ROOT / audio_path).resolve()

    if not full_path.exists():
        raise FileNotFoundError(f"Audio file not found: {full_path}")

    return full_path


def get_audio_duration(audio_path: str) -> float:
    with wave.open(audio_path, "rb") as wf:
        frames = wf.getnframes()
        rate = wf.getframerate()
        duration = frames / float(rate)
    return duration


def compute_rms_energy(audio: np.ndarray) -> float:
    return np.sqrt(np.mean(audio**2))


def detect_clipping(audio: np.ndarray, threshold: float = 0.99) -> bool:
    peak = np.max(np.abs(audio))
    return peak >= threshold
