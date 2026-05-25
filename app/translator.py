from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
import re


# -----------------------------
# LANGUAGE DETECTORS
# -----------------------------
def is_amharic(text):
    return bool(
        re.search(r'[\u1200-\u137F]', text)
    )


def is_arabic(text):
    return bool(
        re.search(r'[\u0600-\u06FF]', text)
    )


def is_chinese(text):
    return bool(
        re.search(r'[\u4e00-\u9fff]', text)
    )


def is_japanese(text):
    return bool(
        re.search(r'[\u3040-\u30ff\u31f0-\u31ff]', text)
    )


# -----------------------------
# SAFE DETECT
# -----------------------------
def safe_detect(text):

    try:
        return detect(text)

    except LangDetectException:
        return "unknown"


# -----------------------------
# TRANSLATOR
# -----------------------------
def translate_to_english(text):

    try:

        text = str(text).strip()

        if not text:
            return "", "unknown"

        # Unicode overrides
        if is_amharic(text):
            language = "am"

        elif is_arabic(text):
            language = "ar"

        elif is_chinese(text):
            language = "zh"

        elif is_japanese(text):
            language = "ja"

        else:
            language = safe_detect(text)

        # Skip translation
        if language in ["en", "unknown"]:
            return text, language

        translated = GoogleTranslator(
            source="auto",
            target="en"
        ).translate(text)

        return translated, language

    except Exception as e:

        print("Translation Error:", e)

        return text, "unknown"