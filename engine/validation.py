from __future__ import annotations

from .models import RotorParameters, ValidationIssue, ValidationReport


def validate_engineering_parameters(params: RotorParameters) -> ValidationReport:
    """Validate input safety and known preview constraints.

    This deliberately does not invent compressor engineering relationships. The
    current repository exposes a visualization adapter, not a validated solver.
    """
    issues: list[ValidationIssue] = []
    rules = [
        ("main_external", params.main_external > 0, "Main external diameter must be greater than zero.", "Enter a positive diameter."),
        ("gate_external", params.gate_external > 0, "Gate external diameter must be greater than zero.", "Enter a positive diameter."),
        ("main_pitch", params.main_pitch > 0, "Main pitch diameter must be greater than zero.", "Enter a positive pitch diameter."),
        ("clearance", params.clearance >= 0, "Clearance cannot be negative.", "Use zero or a positive clearance."),
        ("leading_angle", params.leading_angle >= 0, "Leading angle cannot be negative.", "Review the leading angle."),
        ("trailing_angle", params.trailing_angle >= 0, "Trailing angle cannot be negative.", "Review the trailing angle."),
        ("points", 20 <= params.points <= 1000, "Preview resolution must be between 20 and 1000 points.", "Use a value from 20 to 1000."),
    ]
    for field, ok, message, action in rules:
        if not ok:
            issues.append(ValidationIssue(field, "error", message, action))
    if params.clearance == 0:
        issues.append(ValidationIssue("clearance", "warning", "Zero clearance is a preview condition, not an engineering acceptance criterion.", "Confirm the required design clearance before release."))
    return ValidationReport(valid=not any(i.level == "error" for i in issues), issues=issues)


def validate_result(data: dict) -> ValidationReport:
    issues: list[ValidationIssue] = []
    for key in ("main_x", "main_y", "gate_x", "gate_y"):
        if key not in data or len(data[key]) < 20:
            issues.append(ValidationIssue(key, "error", f"Result does not contain enough points for {key}.", "Regenerate the geometry."))
    return ValidationReport(valid=not any(i.level == "error" for i in issues), issues=issues)
