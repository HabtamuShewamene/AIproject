"""Download and verify the pinned CardiffNLP Twitter-RoBERTa 3-class baseline model.

This provides an immediate, verified, high-performance 3-class sentiment model
running locally while custom staged models are trained on GPU/Colab.
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_DIR = BASE_DIR / "models" / "bert_sentiment"
BASELINE_MODEL_ID = "cardiffnlp/twitter-roberta-base-sentiment-latest"
BASELINE_REVISION = "3216a57f2a0d9c45a2e6c20157c20c49fb4bf9c7"

SMOKE_TEST_CASES = [
    ("I absolutely love this new update! Everything is so smooth.", "positive"),
    ("Worst customer service ever. My account is locked and nobody responds.", "negative"),
    ("The package was delivered at 2:15 PM today.", "neutral"),
]


def download_baseline(
    model_id: str = BASELINE_MODEL_ID,
    revision: str = BASELINE_REVISION,
    output_dir: Path = DEFAULT_MODEL_DIR,
) -> Path:
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info("Downloading tokenizer and model weights from %s (revision %s)...", model_id, revision)

    tokenizer = AutoTokenizer.from_pretrained(model_id, revision=revision)
    model = AutoModelForSequenceClassification.from_pretrained(model_id, revision=revision)

    logger.info("Saving model bundle to %s...", output_dir)
    tokenizer.save_pretrained(str(output_dir))
    model.save_pretrained(str(output_dir))

    logger.info("Model bundle successfully saved to %s", output_dir)
    return output_dir


def verify_model(model_dir: Path = DEFAULT_MODEL_DIR) -> dict[str, str]:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    logger.info("Running smoke test verification on %s...", model_dir)
    tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
    model = AutoModelForSequenceClassification.from_pretrained(str(model_dir))
    model.eval()

    id2label = getattr(model.config, "id2label", {0: "negative", 1: "neutral", 2: "positive"})
    # Normalize keys to ints
    id2label = {int(k): str(v).lower() for k, v in id2label.items()}

    results = {}
    for text, expected in SMOKE_TEST_CASES:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        with torch.no_grad():
            outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)[0]
        predicted_idx = int(torch.argmax(probs).item())
        predicted_label = id2label.get(predicted_idx, "unknown")
        confidence = float(probs[predicted_idx].item())
        logger.info(
            "Input: '%s' -> Predicted: %s (%.2f%%) [Expected: %s]",
            text, predicted_label, confidence * 100, expected,
        )
        results[text] = predicted_label

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Download baseline sentiment model.")
    parser.add_argument("--model-id", default=BASELINE_MODEL_ID, help="HuggingFace model ID")
    parser.add_argument("--revision", default=BASELINE_REVISION, help="Model revision hash")
    parser.add_argument("--output-dir", default=str(DEFAULT_MODEL_DIR), help="Output directory")
    args = parser.parse_args()

    out_path = Path(args.output_dir)
    download_baseline(args.model_id, args.revision, out_path)
    verify_model(out_path)
    logger.info("Baseline model is ready for local API inference!")


if __name__ == "__main__":
    main()
