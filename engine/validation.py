from __future__ import annotations

from .models import RotorParameters, ValidationIssue, ValidationReport


def validate_engineering_parameters(params: RotorParameters) -> ValidationReport:
    issues: list[ValidationIssue] = []

    rules = [
        ("main_external", params.main_external > 0, "Main external diameter must be greater than zero.", "Enter a positive diameter."),
        ("gate_external", params.gate_external > 0, "Gate external diameter must be greater than zero.", "Enter a positive diameter."),
        ("main_pitch", params.main_pitch > 0, "Main pitch diameter must be greater than zero.", "Enter a positive pitch diameter."),
        ("clearance", params.clearance >= 0, "Clearance cannot be negative.", "Use zero or a positive clearance."),
        ("leading_angle", 0 < params.leading_angle < 89, "Leading angle must be between 0° and 89°.", "Review the leading angle."),
        ("trailing_angle", 0 < params.trailing_angle < 89, "Trailing angle must be between 0° and 89°.", "Review the trailing angle."),
        ("points", 20 <= params.points <= 1000, "Profile resolution must be between 20 and 1000 points in preview mode.", "Use a value from 20 to 1000."),
    ]
    for field, ok, message, action in rules:
        if not ok:
            issues.append(ValidationIssue(field, "error", message, action))

    if params.main_external < params.main_pitch:
        issues.append(ValidationIssue("main_external", "warning", "Main external diameter is below the pitch diameter.", "Confirm the intended rotor geometry."))
    if params.gate_external < params.main_pitch:
        issues.append(ValidationIssue("gate_external", "warning", "Gate external diameter is below the pitch diameter.", "Confirm the intended rotor geometry."))
    if params.clearance == 0:
        issues.append(ValidationIssue("clearance", "warning", "Zero clearance is a nominal preview condition, not an engineering acceptance criterion.", "Confirm the required design clearance before release."))

    return ValidationReport(valid=not any(i.level == "error" for i in issues), issues=issues)


def validate_result(data: dict) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for key in ("main_x", "main_y", "gate_x", "gate_y"):
        if key not in data or len(data[key]) < 20:
            issues.append(ValidationIssue(key, "error", f"Result does not contain enough points for {key}.", "Regenerate the geometry."))
    return ValidationReport(valid=not any(i.level == "error" for i in issues), issues=issues)
