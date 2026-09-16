from __future__ import annotations

import io
import math
import zipfile
from typing import Any

import dash
import dash_ag_grid as dag
import dash_mantine_components as dmc
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, State, dcc, html, no_update
from dash_iconify import DashIconify

from components import dmc_compat  # noqa: F401
from application.services import calculate_preview, validate_project
from components.brand import ROSCA_BLUE, ROSCA_GREEN, ROSCA_NAVY, ROSCA_SLATE, brand_lockup, mark
from components.design_system_page import design_system_page
from components.identity_page import identity_page
from components.taskflow import action_button, task_rail
from components.theme import FIGURE_DARK, FIGURE_LIGHT, ROSCA_THEME
from engine.models import RotorParameters

app = dash.Dash(__name__, title="ROSCA — Engineering Intelligence", suppress_callback_exceptions=True)
server = app.server
DEFAULTS = RotorParameters()
FIELDS = ["main_external", "gate_external", "main_pitch", "clearance", "leading_angle", "trailing_angle", "points"]


def icon(name: str, width: int = 18):
    return DashIconify(icon=name, width=width)


def field(label: str, id_: str, value: float, suffix: str, min_=None, max_=None, step=.1):
    return dmc.Stack([dmc.Text(label, size="xs", fw=650, c="dimmed"), dmc.NumberInput(id=id_, value=value, suffix=suffix, min=min_, max=max_, step=step, decimalScale=3, size="sm")], gap=4)


def read_params(values):
    return RotorParameters(main_external=float(values[0] or 0), gate_external=float(values[1] or 0), main_pitch=float(values[2] or 0), clearance=float(values[3] or 0), leading_angle=float(values[4] or 0), trailing_angle=float(values[5] or 0), points=int(values[6] or 0))


def make_2d(data, mode="profile", scheme="dark"):
    fig = go.Figure()
    for label, x, y, color in [("MAIN", data["main_x"], data["main_y"], ROSCA_BLUE), ("GATE", data["gate_x"], data["gate_y"], "#64748B")]:
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=label, line={"color": color, "width": 2.5}, hovertemplate=f"{label}<br>X=%{{x:.3f}} mm<br>Y=%{{y:.3f}} mm<extra></extra>"))
    if mode == "clearance":
        fig.add_annotation(x=.02, y=.97, xref="paper", yref="paper", text="CLEARANCE INSPECTION", showarrow=False, font={"size":11})
    elif mode == "deviation":
        fig.add_annotation(x=.02, y=.97, xref="paper", yref="paper", text="DEVIATION · PREVIEW DATA", showarrow=False, font={"size":11})
    fig.update_layout(template=FIGURE_DARK if scheme == "dark" else FIGURE_LIGHT, margin={"l":15,"r":15,"t":15,"b":15}, hovermode="closest", uirevision="rosca", xaxis={"title":"X (mm)","showgrid":True}, yaxis={"title":"Y (mm)","showgrid":True,"scaleanchor":"x","scaleratio":1}, legend={"orientation":"h","y":1.02,"x":0})
    return fig


def make_3d(data, scheme="dark"):
    fig = go.Figure(); n=min(len(data["main_x"]),220); zs=np.linspace(0,120,30)
    for label,xs,ys,phase,color in [("MAIN",data["main_x"][:n],data["main_y"][:n],0,ROSCA_BLUE),("GATE",data["gate_x"][:n],data["gate_y"][:n],math.pi,"#64748B")]:
        xx=[]; yy=[]; zz=[]
        for z in zs:
            c,s=math.cos(phase+.012*z),math.sin(phase+.012*z); xx.append(np.asarray(xs)*c-np.asarray(ys)*s); yy.append(np.asarray(xs)*s+np.asarray(ys)*c); zz.append(np.full(n,z))
        fig.add_trace(go.Surface(x=xx,y=yy,z=zz,name=label,showscale=False,opacity=.78,colorscale=[[0,color],[1,color]]))
    fig.update_layout(template=FIGURE_DARK if scheme=="dark" else FIGURE_LIGHT,margin={"l":0,"r":0,"t":0,"b":0},scene={"aspectmode":"data","xaxis_title":"X (mm)","yaxis_title":"Y (mm)","zaxis_title":"Z (mm)"})
    return fig


def coordinate_rows(data):
    rows=[]
    for rotor,xs,ys in [("MAIN",data["main_x"],data["main_y"]),("GATE",data["gate_x"],data["gate_y"])]:
        for i,(x,y) in enumerate(zip(xs[:120],ys[:120]),1): rows.append({"Rotor":rotor,"Point":i,"X (mm)":round(float(x),4),"Y (mm)":round(float(y),4),"Radius (mm)":round(float(math.hypot(x,y)),4),"Status":"PREVIEW"})
    return rows


def nav_link(label, icon_name, href, active=False):
    return dcc.Link(dmc.Tooltip(dmc.ActionIcon(icon(icon_name,20), size="lg", variant="light" if active else "subtle", color="blue" if active else "gray"), label=label, position="right"), href=href, refresh=False, className="rosca-nav-link")


def workspace_page():
    return dmc.Grid([
        dmc.GridCol(dmc.Stack([task_rail(1), dmc.Paper([
            dmc.Group([dmc.Stack([dmc.Text("DEFINE",size="xs",fw=900,c="blue",style={"letterSpacing":".16em"}),dmc.Title("Design intent",order=3)],gap=2),dmc.Badge("PREVIEW SOLVER",color="yellow",variant="light")],justify="space-between"),
            dmc.Text("Set the geometry, validate the design space and run the analysis from one focused workspace.",size="sm",c="dimmed",mt="xs"),dmc.Divider(my="md"),
            dmc.Select(id="preset",label="Design preset",data=["SRM-A","SRM-B","Custom"],value="SRM-A",leftSection=icon("tabler:template")),
            dmc.SimpleGrid([field("Main external Ø","main-external",DEFAULTS.main_external," mm",0),field("Gate external Ø","gate-external",DEFAULTS.gate_external," mm",0),field("Main pitch Ø","main-pitch",DEFAULTS.main_pitch," mm",0),field("Profile points","points",DEFAULTS.points," points",20,1000,10)],cols=2,spacing="sm"),
            dmc.SimpleGrid([field("Clearance","clearance",DEFAULTS.clearance," mm",0,step=.01),field("Leading angle α1","leading-angle",DEFAULTS.leading_angle," °",0,step=.5),field("Trailing angle α2","trailing-angle",DEFAULTS.trailing_angle," °",0,step=.5)],cols=3,spacing="sm"),
            dmc.Group([action_button("validate",button_id="validate",primary=False),action_button("simulate",button_id="simulate",primary=True)],gap="xs",mt="md"),
            dmc.Alert(id="validation",title="READY",children="Parameters will be checked before simulation.",color="blue",variant="light",icon=icon("tabler:info-circle"),mt="sm"),
        ],withBorder=True,p="md",radius="md")],gap="md"),span={"base":12,"lg":3}),
        dmc.GridCol(dmc.Stack([
            dmc.Group([dmc.Stack([dmc.Text("ENGINEERING WORKSPACE",size="xs",fw=900,c="blue",style={"letterSpacing":".16em"}),dmc.Title("Design analysis",order=2)],gap=2),dmc.Group([dmc.Badge(id="stage-badge",children="READY",color="gray"),dmc.Text(id="result-id",size="xs",c="dimmed")],gap="xs")],justify="space-between"),
            dmc.Paper([dmc.Group([dmc.Group([dmc.ThemeIcon(icon("tabler:zoom-in"),color="blue",variant="light"),dmc.Text("INSPECT",fw=800,size="sm")],gap="xs"),dmc.SegmentedControl(id="analysis-mode",data=[{"label":"Profile","value":"profile"},{"label":"Clearance","value":"clearance"},{"label":"Deviation","value":"deviation"}],value="profile",size="xs")],justify="space-between")],withBorder=True,p="xs",radius="sm",className="analysis-toolbar"),
            dmc.Tabs(id="workspace-tabs",value="profile",children=dmc.TabsList([dmc.TabsTab("Profile",value="profile"),dmc.TabsTab("Rotor 3D",value="3d"),dmc.TabsTab("Results",value="results")])),
            dmc.Box(id="workspace",className="workspace-surface"),
            dmc.Group([dmc.Progress(id="progress",value=0,size="sm",striped=True,style={"flex":1}),dmc.Text(id="progress-label",children="0% · READY",size="xs",c="dimmed")],gap="sm"),
            dmc.Alert(id="interaction-hint",title="NEXT BEST ACTION",children="Set your parameters, validate them, then run the simulation.",color="blue",variant="light",icon=icon("tabler:arrow-right")),
        ],gap="md"),span={"base":12,"lg":9}),
    ],gutter="md")


def shell():
    return dmc.AppShell([
        dmc.AppShellHeader(dmc.Group([brand_lockup(38),dmc.Group([dmc.Badge("ENGINEERING INTELLIGENCE",color="blue",variant="light"),action_button("open",button_id="open"),action_button("save",button_id="save"),dmc.ColorSchemeToggle(button="light")],gap="xs")],h="100%",px="lg",justify="space-between"),withBorder=True),
        dmc.AppShellNavbar(p="md",w=78,children=dmc.Stack([nav_link("Workspace","tabler:hexagon-3d","/",True),nav_link("Visual identity","tabler:brand-abstract","/identity"),nav_link("Developer Design System","tabler:code","/design-system"),dmc.Divider(my="sm",w=40),nav_link("Help","tabler:help-circle","/identity")],align="center")),
        dmc.AppShellMain(dmc.Container([dcc.Location(id="url"),dcc.Download(id="download-identity-file"),dmc.Box(id="page-content")],fluid=True,p="lg")),
    ],header={"height":72},navbar={"width":78,"breakpoint":"sm"},padding=0)

app.layout=dmc.MantineProvider(theme=ROSCA_THEME,children=shell())


@app.callback(Output("page-content","children"),Input("url","pathname"))
def route(pathname):
    if pathname == "/identity": return identity_page()
    if pathname == "/design-system": return design_system_page()
    return workspace_page()


@app.callback(Output("validation","children"),Output("validation","title"),Output("validation","color"),Input("validate","n_clicks"),[State(f"{x}","value") for x in ["main-external","gate-external","main-pitch","clearance","leading-angle","trailing-angle","points"]],prevent_initial_call=True)
def validate_click(_, *values):
    report=validate_project(read_params(values))
    if report.errors:
        first=report.errors[0]; return f"{first.message} {first.action}","ACTION REQUIRED","red"
    if report.warnings: return "Parameters are safe for the preview adapter. Review before engineering release.","REVIEW BEFORE RELEASE","yellow"
    return "All known preview constraints are satisfied.","READY","green"


@app.callback(Output("workspace","children"),Output("progress","value"),Output("progress-label","children"),Output("stage-badge","children"),Output("stage-badge","color"),Output("result-id","children"),Output("interaction-hint","children"),Input("simulate","n_clicks"),Input("workspace-tabs","value"),Input("analysis-mode","value"),[State(f"{x}","value") for x in ["main-external","gate-external","main-pitch","clearance","leading-angle","trailing-angle","points"]],prevent_initial_call=False)
def workspace_update(simulate_clicks,tab,mode,*values):
    params=read_params(values); report=validate_project(params); result_id=""; progress=0; stage="READY"; color="gray"; hint="Set your parameters, validate them, then run the simulation."
    if report.errors: data={"main_x":[],"main_y":[],"gate_x":[],"gate_y":[]}
    else:
        result_id,data,result_report=calculate_preview(params)
        if simulate_clicks: progress=100; stage="COMPLETED"; color="green"; hint="Analysis is ready. Inspect the result, then deliver the project package."
    if not data["main_x"]: body=dmc.Alert("Resolve the blocking validation issues to generate geometry.",color="red",variant="light")
    elif tab=="3d": body=dcc.Graph(id="rotor-3d",figure=make_3d(data),config={"displaylogo":False,"responsive":True,"scrollZoom":True},style={"height":"600px"})
    elif tab=="results": body=dmc.Stack([dmc.Group([dmc.Title("Results",order=3),dmc.Badge("PREVIEW",color="yellow",variant="light")],justify="space-between"),dmc.SimpleGrid([dmc.Paper([dmc.Text("RESULT ID",size="xs",c="dimmed"),dmc.Text(result_id,fw=800)],withBorder=True,p="md"),dmc.Paper([dmc.Text("VALIDATION",size="xs",c="dimmed"),dmc.Text("PASS" if report.valid else "BLOCKED",fw=800)],withBorder=True,p="md")],cols=2),dag.AgGrid(rowData=coordinate_rows(data),columnDefs=[{"field":k} for k in ["Rotor","Point","X (mm)","Y (mm)","Radius (mm)","Status"]],defaultColDef={"sortable":True,"filter":True,"resizable":True},dashGridOptions={"pagination":True,"paginationPageSize":14},style={"height":"420px"})],gap="md")
    else: body=dcc.Graph(id="profile-graph",figure=make_2d(data,mode=mode or "profile"),config={"displaylogo":False,"responsive":True,"scrollZoom":True},style={"height":"600px"})
    return body,progress,f"{progress}% · {stage}",stage,color,result_id,hint


@app.callback(Output("download-identity-file","data"),Input("download-identity","n_clicks"),prevent_initial_call=True)
def download_identity(_):
    payload=io.BytesIO()
    with zipfile.ZipFile(payload,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("ROSCA-Visual-Identity/README.md", "# ROSCA Visual Identity\n\nProposta 3 — Robusta, Industrial, Tecnológica.\n\n## Cores\n- ROSCA Blue #0E68FF\n- Deep Navy #0F172A\n- Industrial Slate #1E293B\n- Technical Mist #CBD5E1\n- Signal Green #22C55E\n\n## Tipografia\nMontserrat — marca e títulos.\nInter — interface e dados.\n\n## Ícones\nTabler via Iconify.\n")
        z.write("assets/rosca-symbol.svg","ROSCA-Visual-Identity/rosca-symbol.svg")
        z.writestr("ROSCA-Visual-Identity/tokens.css", ":root { --rosca-blue:#0E68FF; --rosca-navy:#0F172A; --rosca-slate:#1E293B; --rosca-text:#CBD5E1; --rosca-green:#22C55E; }\n")
    payload.seek(0)
    return dcc.send_bytes(payload.read(),"rosca-visual-identity.zip")


if __name__ == "__main__":
    app.run(debug=True)
