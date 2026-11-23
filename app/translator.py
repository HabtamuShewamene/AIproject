from deep_translator import GoogleTranslator
from langdetect import detect, LangDetectException
import re


# -------------------------------------------------------
# Sentinel values for language status returned by
# translate_to_english().
#
#   "en"                – already English; no translation needed
#   "unknown"           – langdetect could not identify the language
#   "translation_failed"– language was detected but translation threw
#   <iso-code>          – successfully translated from that language
# -------------------------------------------------------

# -----------------------------
# UNICODE SCRIPT DETECTORS
# -----------------------------
def is_amharic(text: str) -> bool:
    return bool(re.search(r'[\u1200-\u137F]', text))


def is_arabic(text: str) -> bool:
    return bool(re.search(r'[\u0600-\u06FF]', text))


def is_chinese(text: str) -> bool:
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def is_japanese(text: str) -> bool:
    return bool(re.search(r'[\u3040-\u30ff\u31f0-\u31ff]', text))


# -----------------------------
# SAFE LANGUAGE DETECT
# -----------------------------
def safe_detect(text: str) -> str:
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"


# -------------------------------------------------------------------
# translate_to_english(text) -> (translated_text, language_status)
#
# Returns a 2-tuple:
#   translated_text  – English text to pass to the model (may equal
#                      original when already English or on failure)
#   language_status  – one of: "en", "unknown", "translation_failed",
#                      or a BCP-47 language code (e.g. "am", "ar")
# -------------------------------------------------------------------
def translate_to_english(text: str) -> tuple[str, str]:
    text = str(text).strip()

    if not text:
        return "", "unknown"

    # --- script-based language override (robust for Amharic, etc.) ---
    if is_amharic(text):
        detected_language = "am"
    elif is_arabic(text):
        detected_language = "ar"
    elif is_chinese(text):
        detected_language = "zh"
    elif is_japanese(text):
        detected_language = "ja"
    else:
        detected_language = safe_detect(text)

    # English or undetectable → pass through without network call
    if detected_language in ("en", "unknown"):
        return text, detected_language

    # --- attempt translation ---
    try:
        translated = GoogleTranslator(source="auto", target="en").translate(text)
        if not translated or not translated.strip():
            # Translator returned empty string – treat as failure
            return text, "translation_failed"
        return translated.strip(), detected_language

    except Exception as exc:
        # Network outage, quota exceeded, unsupported language, etc.
        # Return original text but flag the status so callers can
        # surface it rather than silently treating it as English.
        print(f"[translator] Translation error ({detected_language}): {exc}")
        return text, "translation_failed"
