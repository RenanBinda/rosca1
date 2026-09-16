from __future__ import annotations

import dash_mantine_components as dmc
from dash_iconify import DashIconify


def analysis_toolbar():
    return dmc.Group([
        dmc.Tooltip(dmc.ActionIcon(DashIconify(icon="tabler:zoom-in", width=17), id="zoom-in", variant="subtle", size="lg"), label="Zoom in"),
        dmc.Tooltip(dmc.ActionIcon(DashIconify(icon="tabler:zoom-out", width=17), id="zoom-out", variant="subtle", size="lg"), label="Zoom out"),
        dmc.Tooltip(dmc.ActionIcon(DashIconify(icon="tabler:arrows-maximize", width=17), id="fit-view", variant="subtle", size="lg"), label="Fit view"),
        dmc.Tooltip(dmc.ActionIcon(DashIconify(icon="tabler:ruler-measure", width=17), id="measure-tool", variant="subtle", size="lg"), label="Measure"),
        dmc.Divider(orientation="vertical", h=22),
        dmc.SegmentedControl(id="analysis-mode", data=[
            {"label": "Profile", "value": "profile"},
            {"label": "Clearance", "value": "clearance"},
            {"label": "Deviation", "value": "deviation"},
        ], value="profile", size="xs"),
    ], gap=4, className="analysis-toolbar")
