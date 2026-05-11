import re
import unicodedata


# =========================================================
# Arabic Text Normalization
# =========================================================

ARABIC_DIACRITICS = re.compile(
    """
    ّ    | # Shadda
    َ    | # Fatha
    ً    | # Tanwin Fath
    ُ    | # Damma
    ٌ    | # Tanwin Damm
    ِ    | # Kasra
    ٍ    | # Tanwin Kasr
    ْ    | # Sukun
    ـ      # Tatweel
""",
    re.VERBOSE,
)


# Emojis + symbols
EMOJI_PATTERN = re.compile(
    "["
    "\U0001f600-\U0001f64f"  # emoticons
    "\U0001f300-\U0001f5ff"  # symbols & pictographs
    "\U0001f680-\U0001f6ff"  # transport & map
    "\U0001f1e0-\U0001f1ff"  # flags
    "\U00002700-\U000027bf"
    "\U000024c2-\U0001f251"
    "]+",
    flags=re.UNICODE,
)


# Remove weird/special characters
SPECIAL_CHARS_PATTERN = re.compile(r"[^؀-ۿa-zA-Z\s\.,!\؟،]")


DIGIT_PATTERN = re.compile(r"\d")


def normalize_text(text: str) -> str:
    """
    Normalize Egyptian Arabic text for STT datasets.

    - Remove emojis
    - Remove Arabic diacritics
    - Remove weird symbols
    - Remove tatweel
    - Normalize whitespace
    - Ensure no digits exist
    """

    # Unicode normalization
    text = unicodedata.normalize("NFKC", text)

    # Remove emojis
    text = EMOJI_PATTERN.sub("", text)

    # Remove tashkeel
    text = ARABIC_DIACRITICS.sub("", text)

    # Remove weird characters
    text = SPECIAL_CHARS_PATTERN.sub("", text)

    # Remove digits
    text = DIGIT_PATTERN.sub("", text)

    # Normalize spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def validate_no_digits(text: str) -> bool:
    """
    Ensure text contains no numeric digits.
    """
    return not bool(DIGIT_PATTERN.search(text))
