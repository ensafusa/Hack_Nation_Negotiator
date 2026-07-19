"""Endpoints for Job Spec & Doc Intake — thin: validate request, call store, return.
No business logic here (see models/job_spec.py for shape, store.py for persistence)."""

import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.job_spec import JobSpec
from app.services import document_intake, geo
from app.store import job_specs

router = APIRouter(prefix="/api/specs", tags=["specs"])


@router.post("", response_model=JobSpec)
def create_spec(spec: JobSpec):
    if not spec.job_spec_id:
        spec.job_spec_id = str(uuid.uuid4())

    # Distance is always server-computed from lat/lng when both points are
    # present — never trust a distance_miles value sent by the client.
    if None not in (spec.origin_lat, spec.origin_lng, spec.destination_lat, spec.destination_lng):
        spec.distance_miles = geo.haversine_distance_miles(
            spec.origin_lat, spec.origin_lng, spec.destination_lat, spec.destination_lng
        )
    else:
        spec.distance_miles = None

    job_specs[spec.job_spec_id] = spec
    return spec


@router.post("/from-document", response_model=JobSpec)
async def create_spec_from_document(file: UploadFile = File(...)):
    """Second required intake path: a photo of an existing quote, inventory
    list, etc. Produces the same JobSpec shape as the voice interview and
    the manual form — fields not visible in the image are left blank/zeroed
    rather than guessed, so the user must review and correct via the normal
    confirm flow before any calls are made (same as every other intake path)."""
    image_bytes = await file.read()
    fields = document_intake.extract_job_spec_fields(image_bytes, file.content_type or "image/jpeg")

    spec = JobSpec(
        job_spec_id=str(uuid.uuid4()),
        origin_address=fields.get("origin_address") or "",
        destination_address=fields.get("destination_address") or "",
        move_date=fields.get("move_date") or "",
        num_trips=fields.get("num_trips") or 1,
        num_bags=fields.get("num_bags") or 0,
        notes=fields.get("notes"),
        source="document_upload",
        confirmed_by_user=False,
    )
    job_specs[spec.job_spec_id] = spec
    return spec


@router.get("/{job_spec_id}", response_model=JobSpec)
def get_spec(job_spec_id: str):
    spec = job_specs.get(job_spec_id)
    if not spec:
        raise HTTPException(status_code=404, detail="job_spec not found")
    return spec


@router.post("/{job_spec_id}/confirm", response_model=JobSpec)
def confirm_spec(job_spec_id: str):
    spec = job_specs.get(job_spec_id)
    if not spec:
        raise HTTPException(status_code=404, detail="job_spec not found")
    spec.confirmed_by_user = True
    return spec
