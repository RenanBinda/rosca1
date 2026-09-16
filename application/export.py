from __future__ import annotations

import io
import json
import zipfile
from datetime import datetime, timezone


def build_project_zip(project: dict, coordinates: list[dict], validation: dict, metrics: dict | None = None) -> bytes:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    name = project.get("name", "rosca_project")
    readme = f"# ROSCA project\n\nProject: {name}\nExported: {stamp} UTC\n\nThis package contains preview-analysis data. Validate against the production engineering solver before design release.\n"
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("README.md", readme)
        archive.writestr("project.json", json.dumps(project, indent=2, ensure_ascii=False))
        archive.writestr("validation/validation.json", json.dumps(validation, indent=2, ensure_ascii=False))
        archive.writestr("results/metrics.json", json.dumps(metrics or {}, indent=2, ensure_ascii=False))
        if coordinates:
            columns = list(coordinates[0])
            rows = [",".join(str(row.get(c, "")) for c in columns) for row in coordinates]
            archive.writestr("coordinates/coordinates.csv", ",".join(columns) + "\n" + "\n".join(rows) + "\n")
    return buffer.getvalue()
