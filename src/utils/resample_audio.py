import numpy as np
from scipy.signal import resample_poly


def resample_audio(
    audio: np.ndarray,
    original_sr: int,
    target_sr: int,
):
    if original_sr == target_sr:
        return audio

    gcd = np.gcd(original_sr, target_sr)

    audio = resample_poly(
        audio,
        target_sr // gcd,
        original_sr // gcd
    )

    return audio
