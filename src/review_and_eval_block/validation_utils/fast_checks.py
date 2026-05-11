import numpy as np
import soundfile as sf
from .audio_utils import get_audio_duration, compute_rms_energy, detect_clipping

def run_fast_checks(
    audio_path: str,
    text: str,
    min_duration: float = 1.0,
    max_duration: float = 30.0,
    min_rms: float = 0.005
) -> dict:
    issues = []

    # =========================================
    # Duration
    # =========================================
    duration = get_audio_duration(audio_path)

    if duration < min_duration:
        issues.append(f"audio too short ({duration:.2f}s)")

    if duration > max_duration:
        issues.append(f"audio too long ({duration:.2f}s)")

    # =========================================
    # Load audio
    # =========================================
    audio, sr = sf.read(audio_path)
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    audio = audio.astype(np.float32)

    # =========================================
    # RMS / Silence
    # =========================================
    rms = compute_rms_energy(audio)
    if rms < min_rms:
        issues.append(f"low audio energy ({rms:.6f})")

    # =========================================
    # Clipping
    # =========================================
    if detect_clipping(audio):
        issues.append("audio clipping detected")

    # =========================================
    # Empty text
    # =========================================
    if len(text.strip()) == 0:
        issues.append("empty text")

    # =========================================
    # Final
    # =========================================
    passed = len(issues) == 0

    return {
        "passed": passed,
        "issues": issues,
        "duration": duration
    }
