import re


# -----------------------------
# CLEAN EXTRA SPACES
# -----------------------------
def normalize_spaces(text):

    return re.sub(
        r"\s+",
        " ",
        str(text)
    ).strip()


# -----------------------------
# SAFE LOWERCASE
# -----------------------------
def safe_lower(text):

    return str(text).lower().strip()