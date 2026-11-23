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


def test_translate_to_english_handles_translation_failure(monkeypatch):
    class FailingTranslator:
        def __init__(self, source, target):
            pass

        def translate(self, _text):
            raise RuntimeError("Google API network timeout")

    monkeypatch.setattr(translator, "safe_detect", lambda _text: "fr")
    monkeypatch.setattr(translator, "GoogleTranslator", FailingTranslator)

    translated_text, language = translator.translate_to_english("bonjour")

    assert translated_text == "bonjour"
    assert language == "translation_failed"


def test_translate_to_english_handles_empty_translation_result(monkeypatch):
    class EmptyResultTranslator:
        def __init__(self, source, target):
            pass

        def translate(self, _text):
            return "   "

    monkeypatch.setattr(translator, "safe_detect", lambda _text: "de")
    monkeypatch.setattr(translator, "GoogleTranslator", EmptyResultTranslator)

    translated_text, language = translator.translate_to_english("Guten Tag")

    assert translated_text == "Guten Tag"
    assert language == "translation_failed"


def test_unicode_script_detectors():
    assert translator.is_amharic("ሰላም ዓለም") is True
    assert translator.is_amharic("Hello world") is False

    assert translator.is_arabic("مرحبا") is True
    assert translator.is_arabic("Hello") is False

    assert translator.is_chinese("你好") is True
    assert translator.is_chinese("Hello") is False

    assert translator.is_japanese("こんにちは") is True
    assert translator.is_japanese("Hello") is False

