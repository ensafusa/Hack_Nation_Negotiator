"""SRP: Document Intake.

Turns a photo or PDF (existing moving quote, inventory list, etc.) into the
same job-spec fields the voice interview produces — the second required
intake path per the challenge brief. Only reports fields actually visible in
the document; never invents an address, date, or count that isn't there.
"""

import json
import logging

import fitz  # PyMuPDF

from app.clients import openai_client

logger = logging.getLogger(__name__)

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

_PDF_MIME_TYPES = {"application/pdf"}


def _pdf_first_page_to_png(pdf_bytes: bytes) -> bytes:
    """OpenAI's vision endpoint only accepts actual images, not PDFs — this
    renders the first page to PNG bytes so PDF-exported quotes (a very
    common case: 'downloaded my quote as a PDF') still work."""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        page = doc[0]
        pix = page.get_pixmap(dpi=200)
        return pix.tobytes("png")


def extract_job_spec_fields(document_bytes: bytes, mime_type: str) -> dict:
    """Best-effort field extraction — returns {} on any failure rather than
    raising, so a bad file doesn't crash intake; the caller fills gaps with
    safe defaults and the user reviews/corrects before confirming the spec.
    Failures ARE logged (not silently swallowed) so real issues are visible
    in server logs instead of just showing up as an empty result.
    """
    try:
        image_bytes, image_mime_type = document_bytes, mime_type
        if mime_type in _PDF_MIME_TYPES:
            image_bytes = _pdf_first_page_to_png(document_bytes)
            image_mime_type = "image/png"

        raw = openai_client.complete_json_from_image(_SYSTEM_PROMPT, image_bytes, image_mime_type)
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            logger.warning("document_intake: OpenAI response was not a JSON object: %r", raw)
            return {}
        return parsed
    except Exception:
        logger.exception("document_intake: extraction failed for mime_type=%s", mime_type)
        return {}
