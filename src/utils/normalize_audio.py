import numpy as np


def normalize_audio(
    audio: np.ndarray
):
    peak = np.max(np.abs(audio))

    if peak > 0:
        audio = audio / peak

    return audio
