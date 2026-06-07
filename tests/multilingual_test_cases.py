TEST_CASES = [

    # =====================
    # ENGLISH
    # =====================

    {
        "text": "I love this product",
        "expected": "positive"
    },

    {
        "text": "I hate this product",
        "expected": "negative"
    },

    {
        "text": "This is amazing",
        "expected": "positive"
    },

    {
        "text": "This is terrible",
        "expected": "negative"
    },

    # =====================
    # AMHARIC
    # =====================

    {
        "text": "በጣም ጥሩ ነው",
        "expected": "positive"
    },

    {
        "text": "እጅግ መጥፎ ነው",
        "expected": "negative"
    },

    {
        "text": "ደስ ብሎኛል",
        "expected": "positive"
    },

    {
        "text": "አልወደድኩትም",
        "expected": "negative"
    },

    # =====================
    # SARCASM
    # =====================

    {
        "text": "Amazing. My code crashed again.",
        "expected": "negative"
    },

    {
        "text": "Wow great. Another bug in production.",
        "expected": "negative"
    },

    {
        "text": "I absolutely love waiting 3 hours for support.",
        "expected": "negative"
    },

    # =====================
    # MIXED
    # =====================

    {
        "text": "This project በጣም ጥሩ ነው",
        "expected": "positive"
    },

    {
        "text": "I hate this project በጣም",
        "expected": "negative"
    }
]