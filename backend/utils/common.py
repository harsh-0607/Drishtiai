from __future__ import annotations

import hashlib
from typing import Optional


def sha256_bytes(data: bytes) -> str:
    """Return SHA-256 hex digest for bytes."""

    return hashlib.sha256(data).hexdigest()


def safe_language(lang: Optional[str]) -> str:
    """Normalize language to a short code used by DRISHTI.

    Supported examples: hi, en, ta, te, bn, mr, gu, kn, ml, pa.
    Defaults to 'hi'.
    """

    if not lang:
        return "hi"

    lang = lang.strip().lower()
    if not lang:
        return "hi"

    # Accept BCP-47 like 'hi-IN'
    if "-" in lang:
        lang = lang.split("-", 1)[0]

    supported = {"hi", "en", "ta", "te", "bn", "mr", "gu", "kn", "ml", "pa"}
    return lang if lang in supported else "hi"
