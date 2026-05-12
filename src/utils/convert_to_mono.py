import numpy as np


def convert_to_mono(
    audio: np.ndarray
):
    if audio.ndim > 1:
        audio = audio.mean(axis=1)

    return audio
