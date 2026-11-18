"""Text preparation for embedding.

The knowledge base moved from the MiniLM embedding model to multilingual E5 last week.
`prepare` is what the new indexer runs on every passage before embedding it."""
import re
import unicodedata

# Amharic is written with several letters that sound the same; writers use them
# interchangeably (ሀ/ሐ/ኀ, ሰ/ሠ, ጸ/ፀ, አ/ዐ). Each Ethiopic letter row holds the seven vowel
# orders of one consonant, so a whole row folds onto its canonical row.
_FOLD_ROWS = {0x1210: 0x1200, 0x1280: 0x1200, 0x1220: 0x1230, 0x1340: 0x1338, 0x12D0: 0x12A0}


def fold_letters(text):
    out = []
    for ch in text:
        cp = ord(ch)
        if 0x1200 <= cp <= 0x137F:
            base, order = cp - (cp - 0x1200) % 8, (cp - 0x1200) % 8
            if base in _FOLD_ROWS:
                ch = chr(_FOLD_ROWS[base] + order)
        out.append(ch)
    return "".join(out)


def prepare(text, role):
    """role is "passage" or "query"; E5 models expect the role as a prefix."""
    text = unicodedata.normalize("NFC", text)
    text = fold_letters(text)
    text = text.replace("፡", " ")              # Ethiopic wordspace ፡ is a space
    text = re.sub(r"\s+", " ", text).strip()
    return f"{role}: {text}"


def prepare_legacy(text):
    """The preparation used with the MiniLM model."""
    text = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", text).strip()
