"""SRP: Document Intake.

Turns a photo (existing moving quote, inventory list, etc.) into the same
job-spec fields the voice interview produces — the second required intake
path per the challenge brief. Only reports fields actually visible in the
image; never invents an address, date, or count that isn't there.
"""

import json

from app.clients import openai_client

_SYSTEM_PROMPT = """You extract residential-moving job details from a photo of a
document — an existing moving quote, an inventory list, or similar. Only report
a field if it is actually visible in the image; use null for anything not shown,
never guess or infer. Respond with JSON matching this shape exactly:
{
  "origin_address": "string|null",
  "destination_address": "string|null",
  "move_date": "string|null (ISO format YYYY-MM-DD if a date is shown)",
  "num_trips": "number|null",
  "num_bags": "number|null (boxes/items count if shown)",
  "notes": "string|null (any other relevant details: large items, quoted price, special instructions)"
}"""


def extract_job_spec_fields(image_bytes: bytes, mime_type: str) -> dict:
    """Best-effort field extraction — returns {} on any failure rather than
    raising, so a bad photo doesn't crash intake; the caller fills gaps with
    safe defaults and the user reviews/corrects before confirming the spec."""
    try:
        raw = openai_client.complete_json_from_image(_SYSTEM_PROMPT, image_bytes, mime_type)
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except Exception:
        return {}
