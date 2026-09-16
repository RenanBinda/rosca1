from __future__ import annotations

import base64
import io
import json
import math
from typing import Any

import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html, no_update
from dash_iconify import DashIconify

from application.export import build_project_zip
from application.services import calculate_preview, parameter_hash, validate_project
from components.analysis_toolbar import analysis_toolbar
from components.taskflow import action_button, task_rail
from components.theme import FIGURE_DARK, FIGURE_LIGHT, ROSCA_THEME
from engine.models import RotorParameters


dmc.pre_render_color_scheme()
app = dash.Dash(__name__, title="ROSCA — Engineering Workspace", suppress_callback_exceptions=True)
server = app.server

FIELDS = ["main_external", "gate_external", "main_pitch", "clearance", "leading_angle", "trailing_angle", "points"]
DEFAULTS = RotorParameters()


def icon(name: str, width: int = 18):
    return DashIconify(icon=name, width=width)


def field(label: str, id_: str, value: float, suffix: str, *, min_: float | None = None, max_: float | None = None, step: float = 0.1):
    return dmc.Stack([
        dmc.Text(label, size="xs", c="dimmed"),
        dmc.NumberInput(id=id_, value=value, suffix=suffix, min=min_, max=max_, step=step, decimalScale=3, size="sm"),
    ], gap=4)


def parameter_panel() -> dmc.Component:
    return dmc.Stack([
        dmc.Group([dmc.Stack([dmc.Text("ROSCA", size="xs", c="blue", fw=900, style={"letterSpacing": ".14em"}), dmc.Title("Define", order=2)], gap=1), dmc.Badge("Preview solver", color="yellow", variant="light")], justify="space-between"),
        dmc.Text("Start with the design intent. ROSCA keeps the next action visible and explains what must be resolved before calculation.", size="sm", c="dimmed"),
        dmc.Divider(),
        dmc.Select(id="preset", label="Design preset", data=["SRM-A", "SRM-B", "Custom"], value="SRM-A", leftSection=icon("tabler:template"), searchable=False),
        dmc.SimpleGrid([
            field("Main external Ø", "main-external", DEFAULTS.main_external, " mm", min_=0, step=.1),
            field("Gate external Ø", "gate-external", DEFAULTS.gate_external, " mm", min_=0, step=.1),
            field("Main pitch Ø", "main-pitch", DEFAULTS.main_pitch, " mm", min_=0, step=.1),
            field("Profile points", "points", DEFAULTS.points, " points", min_=20, max_=1000, step=10),
        ], cols=2, spacing="sm"),
        dmc.SimpleGrid([
            field("Clearance", "clearance", DEFAULTS.clearance, " mm", min_=0, step=.01),
            field("Leading angle α1", "leading-angle", DEFAULTS.leading_angle, " °", min_=0, step=.5),
            field("Trailing angle α2", "trailing-angle", DEFAULTS.trailing_angle, " °", min_=0, step=.5),
        ], cols=3, spacing="sm"),
        dmc.Group([
            action_button("new", button_id="restore", primary=False),
            action_button("validate", button_id="validate", primary=False),
            action_button("simulate", button_id="simulate", primary=True),
        ], gap="xs"),
        dmc.Alert(id="validation", title="Ready", children="Parameters will be checked before simulation.", color="blue", variant="light", icon=icon("tabler:info-circle")),
    ], gap="md")


def make_2d(data: dict, scheme: str = "dark", mode: str = "profile") -> go.Figure:
    fig = go.Figure()
    for label, x, y, color in [("Main", data["main_x"], data["main_y"], "#38A8FF"), ("Gate", data["gate_x"], data["gate_y"], "#FF6577")]:
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=label, line={"color": color, "width": 2.5}, hovertemplate=f"{label}<br>X=%{{x:.3f}} mm<br>Y=%{{y:.3f}} mm<extra></extra>"))
    if mode == "clearance":
        fig.add_annotation(x=0.02, y=.98, xref="paper", yref="paper", text="Clearance inspection", showarrow=False, font={"size": 12})
    if mode == "deviation":
        fig.add_annotation(x=0.02, y=.98, xref="paper", yref="paper", text="Deviation view — preview data", showarrow=False, font={"size": 12})
    template = FIGURE_DARK if scheme == "dark" else FIGURE_LIGHT
    fig.update_layout(template=template, margin={"l": 12, "r": 12, "t": 18, "b": 12}, hovermode="closest", uirevision="rosca-analysis", xaxis={"title": "X (mm)", "showgrid": True}, yaxis={"title": "Y (mm)", "scaleanchor": "x", "scaleratio": 1, "showgrid": True})
    return fig


def make_3d(data: dict, scheme: str = "dark") -> go.Figure:
    fig = go.Figure()
    n = min(len(data["main_x"]), 220)
    z_values = np.linspace(0, 120, 30)
    for label, xs, ys, phase, color in [("Main", data["main_x"][:n], data["main_y"][:n], 0, "#38A8FF"), ("Gate", data["gate_x"][:n], data["gate_y"][:n], math.pi, "#FF6577")]:
        xx, yy, zz = [], [], []
        for z in z_values:
            c, s = math.cos(phase + .012*z), math.sin(phase + .012*z)
            xx.append(np.asarray(xs)*c - np.asarray(ys)*s); yy.append(np.asarray(xs)*s + np.asarray(ys)*c); zz.append(np.full(n, z))
        fig.add_trace(go.Surface(x=xx, y=yy, z=zz, name=label, showscale=False, opacity=.72, colorscale=[[0,color],[1,color]]))
    fig.update_layout(template=FIGURE_DARK if scheme == "dark" else FIGURE_LIGHT, margin={"l": 0, "r": 0, "t": 10, "b": 0}, scene={"aspectmode":"data", "xaxis_title":"X (mm)", "yaxis_title":"Y (mm)", "zaxis_title":"Z (mm)"})
    return fig


def coordinate_rows(data: dict, limit: int = 100) -> list[dict[str, Any]]:
    rows = []
    for rotor, xs, ys in [("Main", data["main_x"], data["main_y"]), ("Gate", data["gate_x"], data["gate_y"])]:
        for i, (x, y) in enumerate(zip(xs[:limit], ys[:limit]), 1):
            rows.append({"Rotor": rotor, "Point": i, "X (mm)": round(float(x), 4), "Y (mm)": round(float(y), 4), "Radius (mm)": round(float(math.hypot(x,y)), 4), "Status": "Preview"})
    return rows


def shell():
    return dmc.AppShell([
        dmc.AppShellHeader(dmc.Group([
            dmc.Group([dmc.ThemeIcon(icon("tabler:hexagon-3d"), size="md", variant="light", color="blue"), dmc.Title("ROSCA", order=3), dmc.Text("Engineering workspace", size="sm", c="dimmed")], gap="sm"),
            dmc.Group([action_button("open", button_id="open"), action_button("save", button_id="save"), dmc.ColorSchemeToggle(button="light"), action_button("help", button_id="help")], gap=2),
        ], h="100%", px="md", justify="space-between"), withBorder=True),
        dmc.AppShellNavbar(p=["md"], w=78, children=dmc.Stack([
            *[dmc.Tooltip(dmc.ActionIcon(icon(i, 20), id=f"nav-{k}", size="lg", variant="subtle"), label=label, position="right") for k,label,i in [("define","Define","tabler:adjustments"),("simulate","Simulate","tabler:player-play"),("inspect","Inspect","tabler:search"),("deliver","Deliver","tabler:file-export")]],
        ], align="center")),
        dmc.AppShellMain(dmc.Container([
            dcc.Store(id="project-store", storage_type="local", data={"name":"Untitled ROSCA project","version":"2.0"}),
            dcc.Store(id="analysis-store", data={"status":"idle","progress":0,"stage":"Ready","result_id":None}),
            dcc.Download(id="download"),
            dmc.Grid([
                dmc.GridCol(dmc.Stack([task_rail(1), parameter_panel()], gap="md"), span={"base":12,"lg":3}),
                dmc.GridCol(dmc.Stack([
                    dmc.Group([dmc.Stack([dmc.Title("Design workspace", order=2), dmc.Text("Define → validate → simulate → inspect → deliver", size="sm", c="dimmed")], gap=2), dmc.Group([dmc.Badge(id="stage-badge", children="Ready", color="gray"), dmc.Text(id="result-id", size="xs", c="dimmed")], gap="xs")], justify="space-between"),
                    analysis_toolbar(),
                    dmc.Tabs(id="workspace-tabs", value="profile", children=dmc.TabsList([dmc.TabsTab("Profile", value="profile"), dmc.TabsTab("Rotor 3D", value="3d"), dmc.TabsTab("Results", value="results")])),
                    dmc.Box(id="workspace", className="workspace-surface"),
                    dmc.Group([dmc.Progress(id="progress", value=0, animated=False, striped=True, size="sm", style={"flex":1}), dmc.Text(id="progress-label", children="Ready", size="xs", c="dimmed")], gap="sm"),
                    dmc.Alert(id="interaction-hint", title="Next best action", children="Set your parameters, validate them, then run the simulation.", color="blue", variant="light", icon=icon("tabler:bulb")),
                ], gap="md"), span={"base":12,"lg":9}),
            ], gutter="md"),
        ], fluid=True, p="md")),
    ], header={"height":58}, navbar={"width":78,"breakpoint":"sm"}, padding=0)

app.layout = dmc.MantineProvider(theme=ROSCA_THEME, forceColorScheme="dark", children=shell())


def read_params(values):
    return RotorParameters(main_external=float(values[0] or 0), gate_external=float(values[1] or 0), main_pitch=float(values[2] or 0), clearance=float(values[3] or 0), leading_angle=float(values[4] or 0), trailing_angle=float(values[5] or 0), points=int(values[6] or 0))


@app.callback(
    Output("validation", "children"), Output("validation", "title"), Output("validation", "color"),
    Input("validate", "n_clicks"),
    [State(f"{id_}", "value") for id_ in ["main-external","gate-external","main-pitch","clearance","leading-angle","trailing-angle","points"]],
    prevent_initial_call=True,
)
def validate_click(_, *values):
    report = validate_project(read_params(values))
    if report.errors:
        first = report.errors[0]
        return f"{first.message} {first.action}", "Action required", "red"
    if report.warnings:
        return "Parameters are safe for the preview adapter. Review the warning before engineering release.", "Review before release", "yellow"
    return "All known preview constraints are satisfied.", "Ready", "teal"


@app.callback(
    Output("workspace", "children"), Output("progress", "value"), Output("progress-label", "children"), Output("stage-badge", "children"), Output("stage-badge", "color"), Output("result-id", "children"), Output("interaction-hint", "children"),
    Input("simulate", "n_clicks"), Input("workspace-tabs", "value"), Input("analysis-mode", "value"),
    [State(f"{id_}", "value") for id_ in ["main-external","gate-external","main-pitch","clearance","leading-angle","trailing-angle","points"]],
    State("analysis-store", "data"), State("_dash-app-content", "children"),
    prevent_initial_call=False,
)
def workspace_update(simulate_clicks, tab, mode, *args):
    values = args[:7]
    params = read_params(values)
    report = validate_project(params)
    result_id = ""
    progress, stage, color = 0, "Ready", "gray"
    hint = "Set your parameters, validate them, then run the simulation."
    if report.errors:
        data = {"main_x": [], "main_y": [], "gate_x": [], "gate_y": []}
    else:
        result_id, data, result_report = calculate_preview(params)
        if simulate_clicks:
            progress, stage, color = 100, "Completed", "teal"
            hint = "Analysis is ready. Inspect the profile or rotor, then export the project package."
    if tab == "3d":
        body = dmc.Stack([dmc.Group([dmc.Title("Rotor inspection", order=3), dmc.Badge("Interactive 3D", color="blue", variant="light")], justify="space-between"), dcc.Graph(id="rotor-3d", figure=make_3d(data), config={"displaylogo":False,"responsive":True,"scrollZoom":True}, style={"height":"620px"})], gap="sm") if data["main_x"] else dmc.Alert("Resolve the blocking validation issues to generate geometry.", color="red")
    elif tab == "results":
        rows = coordinate_rows(data) if data["main_x"] else []
        body = dmc.Stack([dmc.Group([dmc.Title("Results", order=3), action_button("export", button_id="export", primary=True)], justify="space-between"), dmc.SimpleGrid([dmc.Paper([dmc.Text("Result ID", size="xs", c="dimmed"), dmc.Text(result_id or "—", fw=800)], withBorder=True, p="md"), dmc.Paper([dmc.Text("Validation", size="xs", c="dimmed"), dmc.Text("Pass" if data["main_x"] and report.valid else "Blocked", fw=800)], withBorder=True, p="md")], cols=2), dag.AgGrid(id="results-grid", rowData=rows, columnDefs=[{"field":k} for k in ["Rotor","Point","X (mm)","Y (mm)","Radius (mm)","Status"]], defaultColDef={"sortable":True,"filter":True,"resizable":True}, dashGridOptions={"pagination":True,"paginationPageSize":12}, style={"height":"420px"})], gap="md")
    else:
        body = dmc.Stack([dmc.Group([dmc.Title("Profile inspection", order=3), dmc.Text("Preview geometry · select points by hover", size="sm", c="dimmed")], justify="space-between"), dcc.Graph(id="profile-graph", figure=make_2d(data, mode=mode or "profile"), config={"displaylogo":False,"responsive":True,"scrollZoom":True}, style={"height":"620px"})], gap="sm") if data["main_x"] else dmc.Alert("Resolve the blocking validation issues to generate geometry.", color="red")
    return body, progress, f"{progress}% · {stage}", stage, color, result_id, hint


@app.callback(Output("download", "data"), Input("export", "n_clicks"), [State(f"{id_}", "value") for id_ in ["main-external","gate-external","main-pitch","clearance","leading-angle","trailing-angle","points"]], prevent_initial_call=True)
def export_click(_, *values):
    params = read_params(values)
    report = validate_project(params)
    if report.errors:
        return no_update
    result_id, data, result_report = calculate_preview(params)
    rows = coordinate_rows(data, limit=1000)
    project = {"name":"ROSCA project", "version":"2.0", "parameters":params.to_dict(), "result_id":result_id}
    payload = build_project_zip(project, rows, result_report.to_dict(), {"points":len(data["main_x"]), "solver":"preview"})
    return dcc.send_bytes(lambda b: b.write(payload), "rosca-project.zip")


if __name__ == "__main__":
    app.run(debug=True)
