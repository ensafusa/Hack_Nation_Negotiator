import json
from unittest.mock import patch

import fitz
from fastapi.testclient import TestClient

from app.main import app
from app.services import document_intake

client = TestClient(app)


def _make_test_pdf(text: str) -> bytes:
    with fitz.open() as doc:
        page = doc.new_page()
        page.insert_text((50, 50), text, fontsize=11)
        return doc.tobytes()


# --- document_intake.extract_job_spec_fields ---------------------------------


def test_extracts_fields_from_valid_response():
    payload = {
        "origin_address": "123 Main St, Charlotte, NC",
        "destination_address": "456 Oak Ave, Rock Hill, SC",
        "move_date": "2026-08-08",
        "num_trips": 1,
        "num_bags": 20,
        "notes": "Piano needs special handling.",
    }
    with patch.object(document_intake.openai_client, "complete_json_from_image", return_value=json.dumps(payload)):
        fields = document_intake.extract_job_spec_fields(b"fake-image-bytes", "image/png")
    assert fields == payload


def test_returns_empty_dict_on_openai_failure():
    with patch.object(document_intake.openai_client, "complete_json_from_image", side_effect=RuntimeError("boom")):
        fields = document_intake.extract_job_spec_fields(b"fake-image-bytes", "image/png")
    assert fields == {}


def test_returns_empty_dict_on_non_json_response():
    with patch.object(document_intake.openai_client, "complete_json_from_image", return_value="not json"):
        fields = document_intake.extract_job_spec_fields(b"fake-image-bytes", "image/png")
    assert fields == {}


def test_returns_empty_dict_when_response_is_not_an_object():
    with patch.object(document_intake.openai_client, "complete_json_from_image", return_value="[1, 2, 3]"):
        fields = document_intake.extract_job_spec_fields(b"fake-image-bytes", "image/png")
    assert fields == {}


# --- PDF support (regression test: OpenAI vision rejects PDFs outright) ------


def test_pdf_is_converted_to_png_before_calling_openai():
    """This is the exact bug found via manual testing: a PDF exported from
    Google Docs was passed straight through with mime_type='application/pdf',
    which OpenAI's vision endpoint silently rejects -- and the old broad
    except swallowed the error, returning {} with no indication why."""
    pdf_bytes = _make_test_pdf("Origin: 123 Main St, Charlotte, NC")

    with patch.object(document_intake.openai_client, "complete_json_from_image", return_value="{}") as mock_vision:
        document_intake.extract_job_spec_fields(pdf_bytes, "application/pdf")

    mock_vision.assert_called_once()
    called_mime_type = mock_vision.call_args.args[2]
    assert called_mime_type == "image/png"


def test_pdf_extraction_returns_real_fields_end_to_end():
    """No mocking of the PDF conversion itself -- confirms fitz actually
    renders a readable page, only the final OpenAI call is mocked."""
    pdf_bytes = _make_test_pdf("Origin: 6161 Brookshire Blvd, Charlotte, NC")
    payload = {"origin_address": "6161 Brookshire Blvd, Charlotte, NC"}

    with patch.object(document_intake.openai_client, "complete_json_from_image", return_value=json.dumps(payload)):
        fields = document_intake.extract_job_spec_fields(pdf_bytes, "application/pdf")

    assert fields == payload


def test_non_pdf_image_bytes_are_passed_through_unchanged():
    with patch.object(document_intake.openai_client, "complete_json_from_image", return_value="{}") as mock_vision:
        document_intake.extract_job_spec_fields(b"fake-png-bytes", "image/png")

    mock_vision.assert_called_once_with(document_intake._SYSTEM_PROMPT, b"fake-png-bytes", "image/png")


def test_corrupt_pdf_is_logged_and_returns_empty_dict_not_a_crash():
    with patch.object(document_intake.logger, "exception") as mock_log:
        fields = document_intake.extract_job_spec_fields(b"not a real pdf", "application/pdf")

    assert fields == {}
    mock_log.assert_called_once()


# --- POST /api/specs/from-document endpoint -----------------------------------


def test_endpoint_builds_job_spec_from_extracted_fields():
    payload = {
        "origin_address": "123 Main St, Charlotte, NC",
        "destination_address": "456 Oak Ave, Rock Hill, SC",
        "move_date": "2026-08-08",
        "num_trips": 2,
        "num_bags": 15,
        "notes": "Fragile items in the study.",
    }
    with patch.object(document_intake.openai_client, "complete_json_from_image", return_value=json.dumps(payload)):
        response = client.post(
            "/api/specs/from-document",
            files={"file": ("quote.png", b"fake-image-bytes", "image/png")},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["origin_address"] == payload["origin_address"]
    assert body["destination_address"] == payload["destination_address"]
    assert body["move_date"] == payload["move_date"]
    assert body["num_trips"] == 2
    assert body["num_bags"] == 15
    assert body["notes"] == payload["notes"]
    assert body["source"] == "document_upload"
    assert body["confirmed_by_user"] is False
    assert body["job_spec_id"]


def test_endpoint_accepts_pdf_upload():
    pdf_bytes = _make_test_pdf("Origin: 6161 Brookshire Blvd, Charlotte, NC")
    payload = {"origin_address": "6161 Brookshire Blvd, Charlotte, NC", "num_bags": 24}

    with patch.object(document_intake.openai_client, "complete_json_from_image", return_value=json.dumps(payload)):
        response = client.post(
            "/api/specs/from-document",
            files={"file": ("quote.pdf", pdf_bytes, "application/pdf")},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["origin_address"] == payload["origin_address"]
    assert body["num_bags"] == 24
    assert body["source"] == "document_upload"


def test_endpoint_uses_safe_defaults_when_nothing_is_extracted():
    with patch.object(document_intake.openai_client, "complete_json_from_image", return_value="{}"):
        response = client.post(
            "/api/specs/from-document",
            files={"file": ("blank.png", b"fake-image-bytes", "image/png")},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["origin_address"] == ""
    assert body["destination_address"] == ""
    assert body["move_date"] == ""
    assert body["num_trips"] == 1
    assert body["num_bags"] == 0
    assert body["notes"] is None
    assert body["source"] == "document_upload"


def test_created_spec_is_retrievable_via_get():
    with patch.object(document_intake.openai_client, "complete_json_from_image", return_value="{}"):
        create_response = client.post(
            "/api/specs/from-document",
            files={"file": ("blank.png", b"fake-image-bytes", "image/png")},
        )
    job_spec_id = create_response.json()["job_spec_id"]

    get_response = client.get(f"/api/specs/{job_spec_id}")
    assert get_response.status_code == 200
    assert get_response.json()["job_spec_id"] == job_spec_id
