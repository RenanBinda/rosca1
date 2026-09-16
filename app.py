"""ROSCA application entrypoint.

The task-oriented interface lives in app_v2.py so the legacy prototype remains
available in Git history while the evolution branch runs the new workspace.
"""
from app_v2 import app, server


if __name__ == "__main__":
    app.run(debug=True)
