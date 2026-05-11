import re
from difflib import SequenceMatcher
from jiwer import wer

def normalize_arabic(text: str) -> str:
    # Basic Arabic normalization as provided in the notebook
    text = text.lower()
    text = re.sub(r'[ًٌٍَُِّْـ]', '', text)  # Remove diacritics
    text = re.sub(r'[^\w\s]', '', text)    # Remove punctuation
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def text_similarity(text1: str, text2: str) -> float:
    return SequenceMatcher(None, text1, text2).ratio()

def text_WER(reference: str, hypothesis: str) -> float:
    return wer(reference, hypothesis)
