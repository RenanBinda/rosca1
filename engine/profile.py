"""ROSCA calculation adapter.

The investment proposal defines the interaction/UX layer, but it does not provide
engineering equations for the compressor profile. Therefore this module is an
explicit preview adapter: it keeps the supplied UI defaults and creates a stable
visual dataset for the front-end. Replace `generate_profile_preview` with the
validated ROSCA engineering solver without changing the Dash interaction layer.
"""

from __future__ import annotations
import numpy as np

DEFAULTS = {
    "main_external": 321.3,
    "gate_external": 321.3,
    "main_pitch": 201.46,
    "clearance": 0.0,
    "leading_angle": 10.0,
    "trailing_angle": 10.0,
    "points": 200,
}


def validate_parameters(p: dict) -> list[str]:
    errors = []
    required = ["main_external", "gate_external", "main_pitch", "clearance", "leading_angle", "trailing_angle", "points"]
    for key in required:
        if p.get(key) is None:
            errors.append(f"{key} is required")
    if errors:
        return errors
    if p["main_external"] <= 0 or p["gate_external"] <= 0 or p["main_pitch"] <= 0:
        errors.append("Diameters must be greater than zero")
    if p["main_pitch"] >= p["main_external"]:
        pass  # valid relationship depends on the project solver; do not invent a rule here
    if p["clearance"] < 0:
        errors.append("Clearance cannot be negative")
    if p["points"] < 20:
        errors.append("Number of points must be at least 20")
    return errors


def generate_profile_preview(p: dict) -> dict:
    n = int(p.get("points") or DEFAULTS["points"])
    n = max(20, min(n, 1000))
    theta = np.linspace(-np.pi * 0.88, np.pi * 0.88, n)
    pitch = float(p.get("main_pitch") or DEFAULTS["main_pitch"])
    ext = float(p.get("main_external") or DEFAULTS["main_external"])
    gate_ext = float(p.get("gate_external") or DEFAULTS["gate_external"])
    r = ext / 2.0
    rg = gate_ext / 2.0
    # UI preview shape only — deliberately not presented as a compressor equation.
    modulation = 0.055 * r * np.cos(2.0 * theta) + 0.018 * r * np.sin(3.0 * theta)
    modulation_g = 0.05 * rg * np.cos(2.0 * theta + 0.10) + 0.014 * rg * np.sin(3.0 * theta + 0.2)
    main_r = np.clip(r * 0.72 + modulation + 0.10 * pitch * np.cos(theta) / 10, 1, None)
    gate_r = np.clip(rg * 0.72 + modulation_g + 0.10 * pitch * np.cos(theta + 0.08) / 10, 1, None)
    main_x = main_r * np.cos(theta)
    main_y = main_r * np.sin(theta)
    gate_x = gate_r * np.cos(theta + 0.04)
    gate_y = gate_r * np.sin(theta + 0.04)
    return {"main_x": main_x, "main_y": main_y, "gate_x": gate_x, "gate_y": gate_y}
