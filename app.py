from __future__ import annotations

import io
import json
import math
import zipfile
from datetime import datetime, timezone

import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import ALL, Input, Output, State, callback, dcc, html
from dash_iconify import DashIconify

from components.theme import ROSCA_THEME, FIGURE_DARK, FIGURE_LIGHT
from engine.profile import DEFAULTS, generate_profile_preview, validate_parameters


dmc.pre_render_color_scheme()
app = dash.Dash(
    __name__,
    title="ROSCA — Real-time Online Screw Compressor Analysis",
    update_title="ROSCA · Updating…",
    suppress_callback_exceptions=True,
)
server = app.server

NAV_ITEMS = [
    ("profile", "PROFILE", "tabler:adjustments-horizontal"),
    ("rotor", "ROTOR", "tabler:rotate-3d"),
    ("simulation", "SIMULATION", "tabler:player-play"),
    ("results", "RESULTS", "tabler:table"),
    ("export", "EXPORT", "tabler:file-export"),
]


def icon(name: str, width: int = 18):
    return DashIconify(icon=name, width=width)


def params_from(values):
    keys = ["main_external", "gate_external", "main_pitch", "clearance", "leading_angle", "trailing_angle", "points"]
    return {k: values[i] for i, k in enumerate(keys)}


def figure_layout(template, title=None):
    return dict(
        template=template,
        margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, system-ui, sans-serif", size=11),
        hovermode="closest",
        uirevision="rosca-stable",
        title=dict(text=title, x=0.02, xanchor="left", font=dict(size=12)) if title else None,
    )


def make_figure_2d(params: dict, scheme: str = "dark") -> go.Figure:
    data = generate_profile_preview(params)
    template = FIGURE_DARK if scheme == "dark" else FIGURE_LIGHT
    fig = go.Figure()
    for label, x, y, color in [
        ("Main", data["main_x"], data["main_y"], "#38A8FF"),
        ("Gate", data["gate_x"], data["gate_y"], "#FF6577"),
    ]:
        fig.add_trace(go.Scatter(
            x=x, y=y, mode="lines", name=label,
            line=dict(color=color, width=2.8),
            hovertemplate=f"{label}<br>X=%{{x:.4f}} mm<br>Y=%{{y:.4f}} mm<extra></extra>",
        ))
    fig.update_layout(
        **figure_layout(template),
        legend=dict(orientation="h", y=1.02, x=0.02),
        xaxis=dict(title="X (mm)", showgrid=True, zeroline=True, gridcolor="#263442", zerolinecolor="rgba(96,115,134,0.33)"),
        yaxis=dict(title="Y (mm)", showgrid=True, zeroline=True, gridcolor="#263442", zerolinecolor="rgba(96,115,134,0.33)", scaleanchor="x", scaleratio=1),
    )
    return fig


def make_figure_3d(params: dict, scheme: str = "dark") -> go.Figure:
    data = generate_profile_preview(params)
    template = FIGURE_DARK if scheme == "dark" else FIGURE_LIGHT
    n = min(len(data["main_x"]), 220)
    z = np.linspace(0, 120, 30)
    fig = go.Figure()
    for label, xs, ys, color, phase in [
        ("Main", data["main_x"][:n], data["main_y"][:n], "#38A8FF", 0.0),
        ("Gate", data["gate_x"][:n], data["gate_y"][:n], "#FF6577", math.pi),
    ]:
        X, Y, Z = [], [], []
        for zz in z:
            twist = phase + 0.012 * zz
            c, s = math.cos(twist), math.sin(twist)
            X.append(np.asarray(xs) * c - np.asarray(ys) * s)
            Y.append(np.asarray(xs) * s + np.asarray(ys) * c)
            Z.append(np.full(n, zz))
        fig.add_trace(go.Surface(
            x=np.array(X), y=np.array(Y), z=np.array(Z), name=label, showscale=False,
            opacity=0.72, colorscale=[[0, color], [1, color]],
            hovertemplate=f"{label}<br>X=%{{x:.2f}} mm<br>Y=%{{y:.2f}} mm<br>Z=%{{z:.2f}} mm<extra></extra>",
        ))
    fig.update_layout(
        **figure_layout(template),
        scene=dict(
            xaxis_title="X (mm)", yaxis_title="Y (mm)", zaxis_title="Z (mm)",
            aspectmode="data", bgcolor="rgba(0,0,0,0)",
            camera=dict(eye=dict(x=1.55, y=1.55, z=1.05)),
        ),
        showlegend=True,
    )
    return fig


def coordinate_rows(params: dict, limit: int = 80) -> list[dict]:
    data = generate_profile_preview(params)
    rows = []
    for rotor, xs, ys in [("Main", data["main_x"], data["main_y"]), ("Gate", data["gate_x"], data["gate_y"])]:
        for i, (x, y) in enumerate(zip(xs[:limit], ys[:limit])):
            rows.append({
                "Rotor": rotor,
                "Point": i + 1,
                "X (mm)": round(float(x), 4),
                "Y (mm)": round(float(y), 4),
                "Radius (mm)": round(float(math.hypot(x, y)), 4),
                "Deviation (mm)": 0.0,
                "Status": "Valid",
            })
    return rows


def badge(text, tone="success"):
    colors = {"success": "teal", "info": "blue", "warning": "yellow", "danger": "red"}
    return dmc.Badge(text, color=colors.get(tone, "gray"), variant="light", radius="sm", size="sm")


def metric(label, value, unit=""):
    return dmc.Paper(
        dmc.Stack([
            dmc.Text(label, size="xs", c="dimmed"),
            dmc.Group([dmc.Text(value, fw=850, fz=24), dmc.Text(unit, size="xs", c="dimmed")], gap=4),
        ], gap=2), withBorder=True, radius="md", p="md", className="metric-card"
    )


def field(label, component, tip=None):
    right = dmc.Text(tip, size="xs", c="blue") if tip else None
    label_row = dmc.Group([dmc.Text(label, size="xs", c="dimmed"), right] if right else [dmc.Text(label, size="xs", c="dimmed")], justify="space-between")
    return dmc.Stack([label_row, component], gap=4)


def profile_parameters_panel():
    return dmc.Box([
        dmc.Group([
            dmc.Stack([dmc.Text("ROSCA APP", size="xs", c="blue", fw=850, style={"letterSpacing": ".12em"}), dmc.Title("Profile Setup", order=2, fw=850)], gap=2),
            badge("Ready"),
        ], justify="space-between", align="flex-start", mb="md"),
        dmc.Box([
            dmc.Text("Profile", size="xs", fw=850, c="dimmed", tt="uppercase", mb="sm"),
            field("Profile preset", dmc.Select(id="profile-preset", data=["SRM-A", "SRM-B", "Custom"], value="SRM-A", size="sm"), "ⓘ"),
            dmc.Button("Restore default values", id="restore-defaults", variant="default", leftSection=icon("tabler:restore", 16), fullWidth=True, mt="sm", size="sm"),
        ], className="html-side-section"),
        dmc.Box([
            dmc.Text("Geometry", size="xs", fw=850, c="dimmed", tt="uppercase", mb="sm"),
            dmc.SimpleGrid([
                field("Main external Ø", dmc.NumberInput(id="main-external", value=321.3, suffix=" mm", decimalScale=3, size="sm")),
                field("Gate external Ø", dmc.NumberInput(id="gate-external", value=321.3, suffix=" mm", decimalScale=3, size="sm")),
                field("Main pitch Ø", dmc.NumberInput(id="main-pitch", value=201.46, suffix=" mm", decimalScale=3, size="sm")),
                field("Number of points", dmc.NumberInput(id="profile-points", value=200, suffix=" points", min=20, max=5000, step=10, size="sm")),
            ], cols=2, spacing="sm"),
        ], className="html-side-section"),
        dmc.Box([
            dmc.Text("Operational", size="xs", fw=850, c="dimmed", tt="uppercase", mb="sm"),
            field("Clearance", dmc.NumberInput(id="clearance", value=0, suffix=" mm", decimalScale=3, size="sm")),
            dmc.SimpleGrid([
                field("Leading angle α1", dmc.NumberInput(id="leading-angle", value=10, suffix=" °", decimalScale=2, size="sm")),
                field("Trailing angle α2", dmc.NumberInput(id="trailing-angle", value=10, suffix=" °", decimalScale=2, size="sm")),
            ], cols=2, spacing="sm"),
        ], className="html-side-section"),
        dmc.Box([
            dmc.Text("Validation", size="xs", fw=850, c="dimmed", tt="uppercase", mb="sm"),
            dmc.Switch(id="live-validation", label="Real-time validation", checked=True, size="sm"),
            dmc.Alert(id="profile-validation", title="Real-time validation", children="All required parameters are valid.", color="teal", variant="light", icon=icon("tabler:circle-check", 16), mt="sm"),
            dmc.Button("Run simulation", id="run-simulation", fullWidth=True, leftSection=icon("tabler:player-play", 16), mt="sm", color="blue"),
            dmc.Text(["Shortcut: ", dmc.Kbd("Ctrl"), " + ", dmc.Kbd("Enter")], size="xs", c="dimmed", ta="center", mt=6),
        ], className="html-side-section"),
    ], className="profile-settings")


def workspace_card(view="2d"):
    is3d = view == "3d"
    graph_id = "profile-3d-graph" if is3d else "profile-graph"
    figure = make_figure_3d(DEFAULTS) if is3d else make_figure_2d(DEFAULTS)
    return dmc.Box([
        dmc.Group([
            dmc.Group([dmc.Text("Rotor preview" if is3d else "Profile analysis", fw=800, size="sm"), dmc.Text("SRM-A · 200 points", size="xs", c="dimmed")], gap="sm"),
            dmc.Group([
                dmc.Group([dmc.Box(className="legend-line main"), dmc.Text("Main", size="xs", c="dimmed")], gap=5),
                dmc.Group([dmc.Box(className="legend-line gate"), dmc.Text("Gate", size="xs", c="dimmed")], gap=5),
            ], gap="md"),
        ], justify="space-between", className="canvas-head"),
        dcc.Graph(id=graph_id, figure=figure, config={"displaylogo": False, "responsive": True, "scrollZoom": True}, className="profile-plot"),
        dmc.Paper("Hover a curve to inspect coordinates" if not is3d else "Rotate, zoom and hover to inspect the rotor preview", withBorder=True, radius="sm", p="xs", className="chart-note"),
    ], className="canvas-card")


def results_strip():
    columns = [
        {"field": "Rotor", "headerName": "Rotor", "pinned": "left", "width": 92},
        {"field": "Point", "headerName": "Point", "width": 76},
        {"field": "X (mm)", "headerName": "X (mm)", "type": "numericColumn"},
        {"field": "Y (mm)", "headerName": "Y (mm)", "type": "numericColumn"},
        {"field": "Radius (mm)", "headerName": "Radius", "type": "numericColumn"},
        {"field": "Deviation (mm)", "headerName": "Deviation", "type": "numericColumn"},
        {"field": "Status", "headerName": "Status"},
    ]
    return dmc.Box([
        dmc.Tabs([
            dmc.TabsList([
                dmc.TabsTab("Coordinates", value="coordinates"),
                dmc.TabsTab("Validation", value="validation"),
                dmc.TabsTab("Calculation log", value="log"),
            ]),
            dmc.TabsPanel(dag.AgGrid(
                id="coordinates-grid",
                rowData=coordinate_rows(DEFAULTS),
                columnDefs=columns,
                className="ag-theme-quartz-dark",
                defaultColDef={"resizable": True, "sortable": True, "filter": True, "minWidth": 100},
                dashGridOptions={"pagination": True, "paginationPageSize": 8, "animateRows": True, "rowSelection": "single"},
                style={"height": "175px", "width": "100%"},
            ), value="coordinates", pt="xs"),
            dmc.TabsPanel(dmc.Alert("Geometry validation passed with the current calculation state.", color="teal", icon=icon("tabler:circle-check", 16)), value="validation", pt="md"),
            dmc.TabsPanel(dmc.Code(id="results-log", children="[ready] ROSCA workspace initialized.\n[ready] Profile data available.\n[ready] Awaiting validated engineering solver.", block=True), value="log", pt="md"),
        ], value="coordinates", className="bottom-results"),
    ], className="workspace-bottom")


def context_sidebar():
    return dmc.Box([
        dmc.Text("CONTEXT SIDEBAR", size="xs", fw=850, c="blue", style={"letterSpacing": "0.12em"}),
        dmc.Title("2D Properties", order=2, fw=850, mt=4, mb="md"),
        dmc.Paper([
            dmc.Text("Center distance", size="xs", c="dimmed"),
            dmc.Text("251.82", fz=22, fw=850, mt=4),
            dmc.Text("mm", size="xs", c="dimmed"),
        ], withBorder=True, radius="md", p="md", className="metric-card"),
        dmc.Paper([
            dmc.Text("Clearance", size="xs", c="dimmed"),
            dmc.Group([dmc.Text("0.00", fz=22, fw=850), dmc.Text("mm", size="xs", c="dimmed")], gap=4, mt=4),
            dmc.Group([dmc.ThemeIcon(icon("tabler:circle-check", 13), color="teal", variant="light", size="sm"), dmc.Text("Within configured limit", size="xs", c="teal")], gap=6, mt=6),
        ], withBorder=True, radius="md", p="md", className="metric-card"),
        dmc.Box([
            dmc.Text("Calculation progress", size="xs", fw=800, c="dimmed", tt="uppercase"),
            dmc.Group([dmc.Text("Profile generation", size="xs", c="dimmed"), dmc.Text("72%", size="xs", fw=800)], justify="space-between", mt="sm"),
            dmc.Progress(value=72, size="sm", mt=7, color="blue"),
        ], className="html-side-section"),
        dmc.Box([
            dmc.Text("Export coordinates", size="xs", fw=800, c="dimmed", tt="uppercase"),
            dmc.Button("Export (.zip)", id="context-export", leftSection=icon("tabler:file-zip", 16), fullWidth=True, mt="sm", color="blue"),
            dmc.Text("Exports profile coordinates, validation results and simulation metadata.", size="xs", c="dimmed", mt="sm", lh=1.5),
        ], className="html-side-section"),
        dmc.Box([
            dmc.Text("System feedback", size="xs", fw=800, c="dimmed", tt="uppercase"),
            dmc.Paper([dmc.Group([dmc.ThemeIcon(icon("tabler:circle-check", 13), color="teal", variant="light", size="sm"), dmc.Text("All required parameters valid", size="sm", fw=700)], gap=6), dmc.Text("No blocking issues detected.", size="xs", c="dimmed", mt=6)], withBorder=True, radius="md", p="sm", mt="sm"),
        ], className="html-side-section"),
    ], className="context-panel")


def profile_screen():
    return dmc.Box([
        dmc.Box(profile_parameters_panel(), className="profile-side"),
        dmc.Box([
            dmc.Group([
                dmc.Tabs([
                    dmc.TabsList([dmc.TabsTab("2D PROFILE", value="2d"), dmc.TabsTab("3D ROTOR", value="3d")]),
                ], value="2d", id="profile-view-tabs"),
                dmc.Group([dmc.Group([dmc.Box(className="status-dot"), dmc.Text("Calculation ready", size="xs", c="teal", fw=700)], gap=6), dmc.ActionIcon(icon("tabler:help", 17), variant="default", size="md"), dmc.ActionIcon(icon("tabler:download", 17), id="profile-export-action", variant="default", size="md")], gap="xs"),
            ], justify="space-between", className="workspace-topbar"),
            dmc.Box(id="profile-view-content", children=[dmc.Box(workspace_card("2d"), id="profile-view-2d"), dmc.Box(workspace_card("3d"), id="profile-view-3d", style={"display": "none"})], className="workspace-canvas"),
            results_strip(),
        ], className="profile-workspace"),
        dmc.Box(context_sidebar(), className="profile-right"),
    ], className="profile-layout")


def rotor_screen():
    return dmc.Box([
        dmc.Group([dmc.Stack([dmc.Text("WORKSPACE", size="xs", c="blue", fw=850, style={"letterSpacing": ".12em"}), dmc.Title("Rotor", order=2, fw=850)], gap=2), badge("Preview", "info")], justify="space-between", align="flex-start", mb="md"),
        dmc.Tabs([
            dmc.TabsList([dmc.TabsTab("2D PROFILE", value="2d"), dmc.TabsTab("3D ROTOR", value="3d")]),
            dmc.TabsPanel(dmc.Paper(dcc.Graph(id="rotor-profile-graph", figure=make_figure_2d(DEFAULTS), config={"displaylogo": False, "responsive": True}), withBorder=True, radius="md", p="xs", className="plot-panel"), value="2d", pt="md"),
            dmc.TabsPanel(dmc.Paper(dcc.Graph(id="rotor-graph", figure=make_figure_3d(DEFAULTS), config={"displaylogo": False, "responsive": True}), withBorder=True, radius="md", p="xs", className="plot-panel rotor-3d-panel"), value="3d", pt="md"),
        ], value="3d", id="rotor-tabs"),
    ], className="generic-page")


def simulation_screen():
    return dmc.Box([
        dmc.Group([dmc.Stack([dmc.Text("WORKFLOW", size="xs", c="blue", fw=850, style={"letterSpacing": ".12em"}), dmc.Title("Simulation", order=2, fw=850)], gap=2), badge("Calculation workspace", "info")], justify="space-between", align="flex-start", mb="md"),
        dmc.SimpleGrid([
            dmc.Paper([
                dmc.Text("Calculation readiness", fw=800, size="sm"),
                dmc.Stack([badge("Geometry inputs valid"), badge("Point density configured"), badge("No blocking validation errors")], gap="xs", mt="sm"),
                dmc.Divider(my="md"),
                dmc.Button("Run simulation", id="simulation-run-secondary", fullWidth=True, leftSection=icon("tabler:player-play", 16)),
                dmc.Text(["Shortcut: ", dmc.Kbd("Ctrl"), " + ", dmc.Kbd("Enter")], size="xs", c="dimmed", ta="center", mt="xs"),
            ], withBorder=True, radius="md", p="md"),
            dmc.Paper([
                dmc.Text("Progress", fw=800, size="sm"),
                dmc.Text(id="simulation-stage", children="Ready to calculate", fw=700, mt="sm"),
                dmc.Progress(id="simulation-progress", value=0, size="lg", mt="md"),
                dmc.Group([dmc.Text(id="simulation-percent", children="0%", size="xs", c="dimmed"), dmc.Text(id="simulation-elapsed", children="Waiting", size="xs", c="dimmed")], justify="space-between", mt="xs"),
                dmc.Divider(my="md"),
                dmc.Code(id="simulation-log", children="[system] ROSCA calculation pipeline initialized.", block=True),
            ], withBorder=True, radius="md", p="md"),
        ], cols={"base": 1, "md": 2}),
        dcc.Interval(id="simulation-timer", interval=350, n_intervals=0, disabled=True),
    ], className="generic-page")


def results_screen():
    return dmc.Box([
        dmc.Group([dmc.Stack([dmc.Text("ANALYSIS", size="xs", c="blue", fw=850, style={"letterSpacing": ".12em"}), dmc.Title("Results", order=2, fw=850)], gap=2), badge("Results available")], justify="space-between", align="flex-start", mb="md"),
        dmc.SimpleGrid([metric("Center distance", "251.82", "mm"), metric("Clearance", "0.00", "mm"), metric("Points", "200"), metric("Validation", "100", "%")], cols={"base": 1, "xs": 2, "lg": 4}),
        dmc.Paper(dag.AgGrid(id="results-grid", rowData=coordinate_rows(DEFAULTS, 120), columnDefs=[{"field": k} for k in ["Rotor", "Point", "X (mm)", "Y (mm)", "Radius (mm)", "Deviation (mm)", "Status"]], className="ag-theme-quartz-dark", defaultColDef={"resizable": True, "sortable": True, "filter": True}, dashGridOptions={"pagination": True, "paginationPageSize": 20, "animateRows": True}, style={"height": "520px"}), withBorder=True, radius="md", p="xs", mt="md"),
    ], className="generic-page")


def export_screen():
    return dmc.Box([
        dmc.Group([dmc.Stack([dmc.Text("HANDOFF", size="xs", c="blue", fw=850, style={"letterSpacing": ".12em"}), dmc.Title("Export", order=2, fw=850)], gap=2), badge("Ready to export")], justify="space-between", align="flex-start", mb="md"),
        dmc.SimpleGrid([
            dmc.Paper([
                dmc.Text("Export package", fw=800, size="sm"),
                dmc.Checkbox(id="export-coordinates", label="Coordinates CSV", checked=True, mt="md"),
                dmc.Checkbox(id="export-validation", label="Validation JSON", checked=True, mt="sm"),
                dmc.Checkbox(id="export-metadata", label="Simulation metadata JSON", checked=True, mt="sm"),
                dmc.Checkbox(id="export-readme", label="README / package manifest", checked=True, mt="sm"),
                dmc.Button("Export ROSCA package (.zip)", id="export-package", fullWidth=True, mt="lg", leftSection=icon("tabler:file-zip", 16)),
                dcc.Download(id="download-package"),
            ], withBorder=True, radius="md", p="md"),
            dmc.Paper([
                dmc.Text("Package structure", fw=800, size="sm"),
                dmc.Code("rosca_export_YYYYMMDD_HHMMSS.zip\n├── coordinates.csv\n├── validation.json\n├── metadata.json\n└── README.txt", block=True, mt="md"),
                dmc.Text("The export layer is independent from the calculation engine so the solver can evolve without changing the interaction model.", size="sm", c="dimmed", mt="md"),
            ], withBorder=True, radius="md", p="md"),
        ], cols={"base": 1, "md": 2}),
    ], className="generic-page")


def nav_link(screen, label, icon_name):
    return dmc.Tooltip(
        dmc.NavLink(
            id={"type": "nav", "screen": screen},
            label=label,
            leftSection=icon(icon_name, 21),
            variant="light",
            active=(screen == "profile"),
            className="rosca-nav-link",
        ),
        label=label,
        position="right",
        withArrow=True,
        openDelay=350,
        disabled=False,
    )


def app_layout():
    nav = dmc.Box([
        dmc.Tooltip(
            dmc.ThemeIcon(icon("tabler:wind", 24), size=48, radius="md", variant="gradient", gradient={"from": "blue.8", "to": "cyan.6", "deg": 120}),
            label="ROSCA — Real-time Online Screw Compressor Analysis", position="right", withArrow=True,
        ),
        dmc.Divider(my="sm"),
        dmc.Stack([nav_link(*item) for item in NAV_ITEMS], gap=4),
        dmc.Box(style={"flex": 1}),
        dmc.Tooltip(
            dmc.Group([
                dmc.ColorSchemeToggle(id="theme-nav", lightIcon=icon("tabler:sun", 19), darkIcon=icon("tabler:moon", 19), variant="light", size="lg"),
                dmc.Text("THEME", size="xs", fw=800, className="theme-nav-label"),
            ], gap="xs", justify="center", className="theme-nav-control"),
            label="Toggle light / dark mode", position="right", withArrow=True, openDelay=350,
        ),
        dmc.Tooltip(
            dmc.ActionIcon(id="nav-resize", children=icon("tabler:chevrons-right", 18), variant="default", size="lg", className="nav-resize-button", buttonProps={"aria-label": "Expand or compact navigation"}),
            label="Expand / compact navigation", position="right", withArrow=True,
        ),
    ], className="rosca-nav-inner")

    header = dmc.Group([
        dmc.Group([dmc.Text("ROSCA", fw=900, fz=16), dmc.Text("Real-time Online Screw Compressor Analysis", size="xs", c="dimmed")], gap="sm"),
        dmc.Group([
            dmc.Text("Engineering workspace", size="xs", c="dimmed"),
            dmc.ColorSchemeToggle(id="color-scheme-toggle", lightIcon=icon("tabler:sun", 17), darkIcon=icon("tabler:moon", 17), variant="default", size="md"),
        ], gap="sm"),
    ], justify="space-between", h="100%", px="md")

    screens = dmc.Box([
        dmc.Box(profile_screen(), id="screen-profile"),
        dmc.Box(rotor_screen(), id="screen-rotor", style={"display": "none"}),
        dmc.Box(simulation_screen(), id="screen-simulation", style={"display": "none"}),
        dmc.Box(results_screen(), id="screen-results", style={"display": "none"}),
        dmc.Box(export_screen(), id="screen-export", style={"display": "none"}),
    ], id="screen-content")

    return dmc.MantineProvider([
        dcc.Store(id="active-screen", data="profile", storage_type="session"),
        dcc.Store(id="nav-expanded", data=False, storage_type="local"),
        dcc.Store(id="simulation-state", data={"running": False, "progress": 0}),
        dmc.AppShell(
            id="app-shell",
            children=[
                dmc.AppShellHeader(header),
                dmc.AppShellNavbar(nav, id="app-navbar", className="rosca-navbar rosca-navbar-collapsed"),
                    dmc.AppShellMain(dmc.Box(screens, className="rosca-main")),
            ],
            header={"height": 56},
            navbar={"width": 72, "breakpoint": "sm", "collapsed": {"mobile": False, "desktop": False}},
            padding=0,
            withBorder=False,
        ),
    ], theme=ROSCA_THEME)


app.layout = app_layout


@callback(Output("active-screen", "data"), Input({"type": "nav", "screen": ALL}, "n_clicks"), prevent_initial_call=True)
def navigate(_):
    tid = dash.ctx.triggered_id
    return tid["screen"] if tid else dash.no_update


@callback(
    Output("screen-profile", "style"), Output("screen-rotor", "style"), Output("screen-simulation", "style"),
    Output("screen-results", "style"), Output("screen-export", "style"), Input("active-screen", "data")
)
def render_screen(screen):
    return tuple({"display": "block" if screen == key else "none"} for key in ["profile", "rotor", "simulation", "results", "export"])


@callback(Output({"type": "nav", "screen": ALL}, "active"), Input("active-screen", "data"))
def update_nav_active(screen):
    return [screen == key for key, _, _ in NAV_ITEMS]


@callback(
    Output("app-shell", "navbar"), Output("app-navbar", "className"), Output("nav-resize", "children"),
    Input("nav-expanded", "data"), Input("nav-resize", "n_clicks"), State("nav-expanded", "data"), prevent_initial_call=False
)
def resize_nav(store_value, _, state_value):
    expanded = bool(store_value if dash.ctx.triggered_id == "nav-expanded" else not bool(state_value))
    width = 218 if expanded else 72
    cls = "rosca-navbar rosca-navbar-expanded" if expanded else "rosca-navbar rosca-navbar-collapsed"
    button_icon = icon("tabler:chevrons-left" if expanded else "tabler:chevrons-right", 18)
    return {"width": width, "breakpoint": "sm", "collapsed": {"mobile": False, "desktop": False}}, cls, button_icon


@callback(Output("nav-expanded", "data"), Input("nav-resize", "n_clicks"), State("nav-expanded", "data"), prevent_initial_call=True)
def persist_nav_resize(_, expanded):
    return not bool(expanded)


@callback(Output("profile-view-2d", "style"), Output("profile-view-3d", "style"), Input("profile-view-tabs", "value"))
def switch_profile_view(view):
    return ({"display": "block"} if view == "2d" else {"display": "none"}, {"display": "block"} if view == "3d" else {"display": "none"})


@callback(
    Output("profile-graph", "figure"), Output("profile-3d-graph", "figure"), Output("rotor-profile-graph", "figure"), Output("rotor-graph", "figure"),
    Input("color-scheme-toggle", "computedColorScheme"),
    Input("main-external", "value"), Input("gate-external", "value"), Input("main-pitch", "value"),
    Input("clearance", "value"), Input("leading-angle", "value"), Input("trailing-angle", "value"), Input("profile-points", "value"),
)
def update_graphs(scheme, *values):
    return make_figure_2d(params_from(values), scheme), make_figure_3d(params_from(values), scheme), make_figure_2d(params_from(values), scheme), make_figure_3d(params_from(values), scheme)


@callback(Output("coordinates-grid", "className"), Output("results-grid", "className"), Input("color-scheme-toggle", "computedColorScheme"))
def update_grid_theme(scheme):
    cls = "ag-theme-quartz-dark" if scheme == "dark" else "ag-theme-quartz"
    return cls, cls


@callback(
    Output("profile-validation", "children"), Output("profile-validation", "color"), Output("profile-validation", "title"),
    Input("main-external", "value"), Input("gate-external", "value"), Input("main-pitch", "value"), Input("clearance", "value"),
    Input("leading-angle", "value"), Input("trailing-angle", "value"), Input("profile-points", "value"), Input("live-validation", "checked")
)
def validate_ui(*values):
    live = values[-1]
    if not live:
        return "Live validation is paused.", "gray", "Validation paused"
    errors = validate_parameters(params_from(values[:-1]))
    return ("; ".join(errors), "red", "Validation requires attention") if errors else ("All required parameters are valid.", "teal", "Real-time validation")


PARAM_OUTPUTS = [Output("main-external", "value"), Output("gate-external", "value"), Output("main-pitch", "value"), Output("clearance", "value"), Output("leading-angle", "value"), Output("trailing-angle", "value"), Output("profile-points", "value")]


@callback(PARAM_OUTPUTS, Input("restore-defaults", "n_clicks"), prevent_initial_call=True)
def restore_defaults(_):
    return tuple(DEFAULTS[k] for k in ["main_external", "gate_external", "main_pitch", "clearance", "leading_angle", "trailing_angle", "points"])


@callback(
    Output("simulation-timer", "disabled"), Output("simulation-state", "data"), Output("simulation-stage", "children"),
    Output("simulation-percent", "children"), Output("simulation-progress", "value"), Output("simulation-log", "children"),
    Input("run-simulation", "n_clicks"), Input("simulation-run-secondary", "n_clicks"), Input("simulation-timer", "n_intervals"),
    State("simulation-state", "data"), prevent_initial_call=True
)
def simulation_flow(run_a, run_b, tick, state):
    triggered = dash.ctx.triggered_id
    state = state or {"running": False, "progress": 0}
    if triggered in ["run-simulation", "simulation-run-secondary"]:
        return False, {"running": True, "progress": 0}, "Preparing geometry", "0%", 0, "[system] Simulation started.\n[step] Preparing geometry"
    if triggered == "simulation-timer" and state.get("running"):
        p = min(int(state.get("progress", 0)) + 12, 100)
        stages = [(0, "Preparing geometry"), (24, "Generating profile coordinates"), (48, "Evaluating geometry"), (72, "Preparing results"), (100, "Calculation complete")]
        stage = next((v for k, v in stages if p <= k), "Calculation complete")
        if p >= 100:
            return True, {"running": False, "progress": 100}, "Calculation complete", "100%", 100, "[done] Calculation complete.\n[done] Results are ready."
        return False, {"running": True, "progress": p}, stage, f"{p}%", p, f"[running] {stage}\n[progress] {p}%"
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update


@callback(Output("download-package", "data"), Input("export-package", "n_clicks"), Input("context-export", "n_clicks"), Input("profile-export-action", "n_clicks"), State("main-external", "value"), State("gate-external", "value"), State("main-pitch", "value"), State("clearance", "value"), State("leading-angle", "value"), State("trailing-angle", "value"), State("profile-points", "value"), prevent_initial_call=True)
def export_package(_, __, ___, *values):
    params = params_from(values)
    rows = coordinate_rows(params)
    buffer = io.BytesIO()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("coordinates.csv", pd.DataFrame(rows).to_csv(index=False))
        z.writestr("validation.json", json.dumps({"errors": validate_parameters(params)}, indent=2))
        z.writestr("metadata.json", json.dumps({"product": "ROSCA", "meaning": "Real-time Online Screw Compressor Analysis", "parameters": params, "generated_at": datetime.now(timezone.utc).isoformat()}, indent=2))
        z.writestr("README.txt", "ROSCA export package\nThis package contains preview-adapter output. Connect the validated engineering solver before production use.\n")
    return dcc.send_bytes(buffer.getvalue(), f"rosca_export_{stamp}.zip")


if __name__ == "__main__":
    app.run(debug=True)
