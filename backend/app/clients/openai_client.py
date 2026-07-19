"""Thin wrapper around the OpenAI API — no domain logic here.

Only responsibility: send a prompt (with optional JSON schema), return the raw
completion. Callers (extraction.py, ranking.py, document_intake.py) own the
prompt content and interpret the response.
"""

import base64
from functools import lru_cache

from openai import OpenAI

from app.config import settings


@lru_cache
def _get_client() -> OpenAI:
    """Created lazily on first use, not at import time — so the app can boot
    even before this key is configured; it only fails when actually called."""
    return OpenAI(api_key=settings.openai_api_key)


def complete_json(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini") -> str:
    """Run a chat completion constrained to JSON output, return the raw JSON string."""
    response = _get_client().chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


def complete_json_from_image(
    system_prompt: str,
    image_bytes: bytes,
    mime_type: str,
    user_prompt: str = "Extract the requested fields from this image.",
    model: str = "gpt-4o-mini",
) -> str:
    """Same contract as complete_json, but the user turn is an image (vision).
    Used for document intake — a photo of an existing quote, inventory list, etc."""
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    data_uri = f"data:{mime_type};base64,{encoded}"
    response = _get_client().chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_prompt},
                    {"type": "image_url", "image_url": {"url": data_uri}},
                ],
            },
        ],
    )
    return response.choices[0].message.content
