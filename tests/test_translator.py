from langdetect.lang_detect_exception import LangDetectException

from app import translator


def test_safe_detect_returns_unknown_on_detection_error(monkeypatch):
    def raise_error(_text):
        raise LangDetectException(0, "failed")

    monkeypatch.setattr(translator, "detect", raise_error)

    assert translator.safe_detect("???") == "unknown"


def test_translate_to_english_returns_blank_for_empty_input():
    translated_text, language = translator.translate_to_english("   ")

    assert translated_text == ""
    assert language == "unknown"


def test_translate_to_english_skips_translation_for_english(monkeypatch):
    monkeypatch.setattr(translator, "safe_detect", lambda _text: "en")

    translated_text, language = translator.translate_to_english("Hello world")

    assert translated_text == "Hello world"
    assert language == "en"


def test_translate_to_english_uses_translator_for_non_english(monkeypatch):
    class FakeTranslator:
        def __init__(self, source, target):
            assert source == "auto"
            assert target == "en"

        def translate(self, text):
            assert text == "hola"
            return "hello"

    monkeypatch.setattr(translator, "safe_detect", lambda _text: "es")
    monkeypatch.setattr(translator, "GoogleTranslator", FakeTranslator)

    translated_text, language = translator.translate_to_english("hola")

    assert translated_text == "hello"
    assert language == "es"
