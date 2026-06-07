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
# API SETTINGS
# =========================================

API_TITLE = "Twitter/X Sentiment Analysis API"

API_VERSION = "1.0.0"
