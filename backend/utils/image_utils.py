from __future__ import annotations

import base64


def decode_base64_image(image_b64: str) -> bytes:
    """Decode a base64 string (optionally with data URL prefix) into bytes."""

    if not image_b64:
        raise ValueError("image is required")

    # Handle data URLs: data:image/jpeg;base64,...
    if "," in image_b64 and image_b64.strip().lower().startswith("data:"):
        image_b64 = image_b64.split(",", 1)[1]

    return base64.b64decode(image_b64, validate=True)
