"""Reusable ROSCA UI primitives.

The application shell is intentionally composed in app.py so the visual hierarchy can
stay close to the approved HTML reference. These helpers are kept small for future
component extraction into a full design-system package.
"""

import dash_mantine_components as dmc
from dash_iconify import DashIconify


def icon(name: str, width: int = 18):
    return DashIconify(icon=name, width=width)


def status_badge(label: str, tone: str = "success"):
    colors = {"success": "teal", "warning": "yellow", "danger": "red", "info": "blue"}
    return dmc.Badge(label, color=colors.get(tone, "gray"), variant="light", size="sm", radius="sm")


def metric_card(label: str, value: str, unit: str = "", icon_name: str | None = None):
    lead = dmc.ThemeIcon(icon(icon_name, 17), variant="light", color="rosca", size="lg") if icon_name else None
    content = dmc.Stack([
        dmc.Text(label, size="xs", c="dimmed"),
        dmc.Group([dmc.Text(value, fw=850, fz="xl"), dmc.Text(unit, size="xs", c="dimmed")], gap=4),
    ], gap=0)
    return dmc.Paper(dmc.Group([lead, content] if lead else [content], wrap="nowrap"), withBorder=True, p="md", radius="md", className="metric-card")
