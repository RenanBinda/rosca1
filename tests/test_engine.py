from engine.models import RotorParameters
from engine.validation import validate_engineering_parameters


def test_default_parameters_have_no_blocking_errors():
    report = validate_engineering_parameters(RotorParameters())
    assert report.valid
    assert not report.errors


def test_negative_clearance_is_blocking():
    report = validate_engineering_parameters(RotorParameters(clearance=-0.1))
    assert not report.valid
    assert any(i.field == "clearance" for i in report.errors)


def test_preview_resolution_is_capped_at_engine_limit():
    report = validate_engineering_parameters(RotorParameters(points=5000))
    assert not report.valid
    assert any(i.field == "points" for i in report.errors)
