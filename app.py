"""ROSCA application entrypoint.

The production evolution UI is implemented in app_v3.py.
"""
from app_v3 import app, server


if __name__ == "__main__":
    app.run(debug=True)
