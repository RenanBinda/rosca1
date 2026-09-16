from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

SimulationStatus = Literal["idle", "running", "completed", "blocked", "error"]


@dataclass(frozen=True)
class RotorParameters:
    main_external: float = 321.3
    gate_external: float = 321.3
    main_pitch: float = 201.46
    clearance: float = 0.0
    leading_angle: float = 10.0
    trailing_angle: float = 10.0
    points: int = 200
    preset: str = "SRM-A"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RotorParameters":
        keys = {f.name for f in cls.__dataclass_fields__.values()}
        return cls(**{k: data[k] for k in keys if k in data})


@dataclass
class ValidationIssue:
    field: str
    level: Literal["error", "warning", "info"]
    message: str
    action: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ValidationReport:
    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.level == "error"]

    @property
    def warnings(self) -> list[ValidationIssue]:
        return [i for i in self.issues if i.level == "warning"]

    def to_dict(self) -> dict[str, Any]:
        return {"valid": self.valid, "issues": [i.to_dict() for i in self.issues]}


@dataclass
class SimulationState:
    status: SimulationStatus = "idle"
    stage: str = "Ready"
    progress: int = 0
    started_at: str | None = None
    completed_at: str | None = None
    parameter_hash: str = ""
    result_id: str | None = None
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def start(self, parameter_hash: str) -> None:
        self.status = "running"
        self.stage = "Preparing"
        self.progress = 0
        self.started_at = datetime.now(timezone.utc).isoformat()
        self.completed_at = None
        self.parameter_hash = parameter_hash
        self.result_id = None
        self.warnings.clear()
        self.errors.clear()

    def finish(self, result_id: str, warnings: list[str] | None = None) -> None:
        self.status = "completed"
        self.stage = "Completed"
        self.progress = 100
        self.completed_at = datetime.now(timezone.utc).isoformat()
        self.result_id = result_id
        self.warnings = warnings or []

    def fail(self, message: str) -> None:
        self.status = "error"
        self.stage = "Error"
        self.errors.append(message)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Project:
    name: str = "Untitled ROSCA project"
    version: str = "2.0"
    parameters: RotorParameters = field(default_factory=RotorParameters)
    simulation: SimulationState = field(default_factory=SimulationState)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "version": self.version,
            "parameters": self.parameters.to_dict(),
            "simulation": self.simulation.to_dict(),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
