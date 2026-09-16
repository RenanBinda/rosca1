from __future__ import annotations

import hashlib
import json
import uuid

from engine.models import RotorParameters, ValidationReport
from engine.profile import generate_profile_preview
from engine.validation import validate_engineering_parameters, validate_result


def parameter_hash(params: RotorParameters) -> str:
    payload = json.dumps(params.to_dict(), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]


def validate_project(params: RotorParameters) -> ValidationReport:
    return validate_engineering_parameters(params)


def calculate_preview(params: RotorParameters) -> tuple[str, dict, ValidationReport]:
    result_id = f"ROSCA-{uuid.uuid4().hex[:10].upper()}"
    data = generate_profile_preview(params.to_dict())
    report = validate_result(data)
    return result_id, data, report
