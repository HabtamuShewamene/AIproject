from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# =========================================
# TWITTER/X API
# =========================================

TWITTER_BEARER_TOKEN = os.getenv(
    "TWITTER_BEARER_TOKEN"
)

# =========================================
# APIFY API
# =========================================

APIFY_TOKEN = os.getenv("APIFY_TOKEN")
TWITTER_COOKIE = os.getenv("TWITTER_COOKIE")

# =========================================
# MODEL PATH
# =========================================

MODEL_PATH = os.getenv(
    "MODEL_PATH",
    "models/bert_sentiment"
)

# =========================================
# PREDICTION SETTINGS
# =========================================

# Minimum softmax probability to commit to a label.
# When the winning class sits below this threshold the
# API returns label="uncertain" and sets low_confidence=True.
ABSTENTION_THRESHOLD: float = float(
    os.getenv("ABSTENTION_THRESHOLD", "0.45")
)

# Maximum input length in characters accepted by /predict.
# Inputs exceeding this are truncated to the first N chars
# and flagged via processing_status="truncated".
MAX_INPUT_CHARS: int = int(
    os.getenv("MAX_INPUT_CHARS", "2000")
)

# Minimum input length in characters.
# Inputs shorter than this return processing_status="too_short".
MIN_INPUT_CHARS: int = int(
    os.getenv("MIN_INPUT_CHARS", "3")
)

# =========================================
# API SETTINGS
# =========================================

API_TITLE = "SentiAI — AI Sentiment Analysis API"

API_VERSION = "2.0.0"

# Maximum number of items in a single batch prediction request
MAX_BATCH_SIZE: int = int(os.getenv("MAX_BATCH_SIZE", "50"))

# Request timeout in seconds for social scraping and model inference
REQUEST_TIMEOUT_SECONDS: int = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "30"))

# Allowed CORS origins
CORS_ORIGINS: list[str] = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001",
    ).split(",")
    if origin.strip()
]

# Structured logging level
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()

