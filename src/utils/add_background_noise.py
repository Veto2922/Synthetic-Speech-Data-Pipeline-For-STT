import numpy as np
import soundfile as sf
import random
from scipy.signal import resample_poly


def add_background_noise(
    speech_path: str,
    noise_path: str,
    output_path: str,
    snr_db: float = 10,
):
    # Load
    speech, sr = sf.read(speech_path)
    noise, noise_sr = sf.read(noise_path)

    # Mono
    if speech.ndim > 1:
        speech = speech.mean(axis=1)

    if noise.ndim > 1:
        noise = noise.mean(axis=1)

    speech = speech.astype(np.float32)
    noise = noise.astype(np.float32)

    # 🚀 FAST resampling (key speed improvement)
    if noise_sr != sr:
        gcd = np.gcd(noise_sr, sr)
        noise = resample_poly(noise, sr // gcd, noise_sr // gcd)

    # Repeat if needed
    if len(noise) < len(speech):
        repeats = (len(speech) // len(noise)) + 1
        noise = np.tile(noise, repeats)

    # Random crop
    start = random.randint(0, len(noise) - len(speech))
    noise = noise[start : start + len(speech)]

    # Power (can be slightly optimized later, but fine)
    speech_power = np.mean(speech * speech)
    noise_power = np.mean(noise * noise)

    scale = np.sqrt(speech_power / (10 ** (snr_db / 10) * noise_power + 1e-9))

    noise *= scale

    mixed = speech + noise

    # Normalize safely
    peak = np.max(np.abs(mixed)) + 1e-9
    mixed = mixed / peak

    sf.write(output_path, mixed, sr)

    return output_path
