from __future__ import annotations

from dash import dcc, html
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from components.brand import ROSCA_BLUE, ROSCA_GREEN, ROSCA_NAVY, ROSCA_SLATE, ROSCA_TEXT, brand_lockup, mark


def code_block(text: str):
    return dmc.Paper(dmc.Code(text, block=True, style={"whiteSpace": "pre-wrap", "fontSize": "12px", "lineHeight": 1.6}), withBorder=True, p="md", radius="sm", className="ds-code")


def token(name: str, value: str, description: str):
    return dmc.Group([
        dmc.Stack([dmc.Text(name, fw=800, size="sm"), dmc.Text(description, size="xs", c="dimmed")], gap=2),
        dmc.Code(value),
    ], justify="space-between", wrap="nowrap")


def component_card(icon: str, title: str, description: str, example):
    return dmc.Paper([
        dmc.Group([dmc.ThemeIcon(DashIconify(icon=icon, width=18), color="blue", variant="light"), dmc.Text(title, fw=800)], gap="sm"),
        dmc.Text(description, size="sm", c="dimmed", mt="xs"),
        dmc.Box(example, mt="md", className="ds-component-demo"),
    ], withBorder=True, p="md", radius="md")


def design_system_page():
    return dmc.Stack([
        dmc.Group([
            dmc.Stack([
                dmc.Text("DEVELOPER DOCUMENTATION", size="xs", fw=900, c="blue", style={"letterSpacing": ".18em"}),
                dmc.Title("ROSCA Design System", order=1),
                dmc.Text("Implementation guide for the ROSCA Engineering Intelligence interface.", size="md", c="dimmed"),
            ], gap=3),
            dcc.Link(dmc.Button("← Visual identity", leftSection=DashIconify(icon="tabler:arrow-left", width=16), variant="subtle", color="gray"), href="/identity", refresh=False),
        ], justify="space-between", align="flex-start"),

        dmc.Grid([
            dmc.GridCol(dmc.Stack([
                dmc.Paper([
                    dmc.Text("01 · FOUNDATION", size="xs", fw=900, c="blue", style={"letterSpacing": ".14em"}),
                    dmc.Title("Brand tokens", order=3, mt="xs"),
                    dmc.Stack([
                        token("--rosca-blue", ROSCA_BLUE, "Primary action, focus and interactive emphasis"),
                        token("--rosca-navy", ROSCA_NAVY, "Application shell and dark foundation"),
                        token("--rosca-slate", ROSCA_SLATE, "Cards, panels and elevated surfaces"),
                        token("--rosca-text", ROSCA_TEXT, "Primary technical text on dark surfaces"),
                        token("--rosca-green", ROSCA_GREEN, "Success, validation and completed state"),
                    ], gap="sm", mt="md"),
                ], withBorder=True, p="lg", radius="md"),
                dmc.Paper([
                    dmc.Text("Spacing & shape", size="xs", fw=900, c="blue", style={"letterSpacing": ".14em"}),
                    dmc.Title("Compact engineering UI", order=3, mt="xs"),
                    dmc.Text("Use restrained radii, compact controls and generous separation between task groups. Avoid decorative gradients, oversized cards and visual noise.", size="sm", c="dimmed", mt="xs"),
                    code_block('radius: 8–12px\ncontrol-height: 34–40px\nsection-gap: 16–24px\ncard-padding: 16–24px\nfocus-ring: 2px ROSCA Blue'),
                ], withBorder=True, p="lg", radius="md"),
            ], gap="md"), span={"base":12,"lg":5}),

            dmc.GridCol(dmc.Stack([
                dmc.Paper([
                    dmc.Text("02 · TYPOGRAPHY", size="xs", fw=900, c="blue", style={"letterSpacing": ".14em"}),
                    dmc.Title("Montserrat + Inter", order=3, mt="xs"),
                    dmc.Group([dmc.Stack([dmc.Text("Montserrat", size="28px", fw=800), dmc.Text("Brand / display / headings", size="xs", c="dimmed")], gap=2), dmc.Stack([dmc.Text("Inter", size="24px", fw=600), dmc.Text("UI / data / body copy", size="xs", c="dimmed")], gap=2)], mt="md", grow=True),
                    dmc.Text("Aa 0123456789  Ø  α1  α2  mm  %  →", ff="monospace", c="blue", mt="lg"),
                ], withBorder=True, p="lg", radius="md"),
                dmc.Paper([
                    dmc.Text("03 · ICONOGRAPHY", size="xs", fw=900, c="blue", style={"letterSpacing": ".14em"}),
                    dmc.Title("Tabler / Iconify", order=3, mt="xs"),
                    dmc.Text("Use line icons with consistent visual weight. Icons describe actions and states; they never replace an accessible text label when the action is ambiguous.", size="sm", c="dimmed", mt="xs"),
                    dmc.SimpleGrid([
                        dmc.Stack([dmc.ThemeIcon(DashIconify(icon="tabler:adjustments"), color="blue", variant="light", size="lg"), dmc.Text("Define", size="xs", fw=700)], gap=4),
                        dmc.Stack([dmc.ThemeIcon(DashIconify(icon="tabler:shield-check"), color="green", variant="light", size="lg"), dmc.Text("Validate", size="xs", fw=700)], gap=4),
                        dmc.Stack([dmc.ThemeIcon(DashIconify(icon="tabler:player-play"), color="blue", variant="light", size="lg"), dmc.Text("Simulate", size="xs", fw=700)], gap=4),
                        dmc.Stack([dmc.ThemeIcon(DashIconify(icon="tabler:search"), color="blue", variant="light", size="lg"), dmc.Text("Inspect", size="xs", fw=700)], gap=4),
                        dmc.Stack([dmc.ThemeIcon(DashIconify(icon="tabler:ruler-measure"), color="blue", variant="light", size="lg"), dmc.Text("Measure", size="xs", fw=700)], gap=4),
                        dmc.Stack([dmc.ThemeIcon(DashIconify(icon="tabler:file-export"), color="green", variant="light", size="lg"), dmc.Text("Export", size="xs", fw=700)], gap=4),
                    ], cols=6, mt="md"),
                    code_block('from dash_iconify import DashIconify\nDashIconify(icon="tabler:player-play", width=18)'),
                ], withBorder=True, p="lg", radius="md"),
            ], gap="md"), span={"base":12,"lg":7}),
        ], gutter="md"),

        dmc.Paper([
            dmc.Text("04 · COMPONENTS", size="xs", fw=900, c="blue", style={"letterSpacing": ".14em"}),
            dmc.Title("Interaction patterns", order=3, mt="xs"),
            dmc.Text("These patterns form the visual grammar of the engineering workspace.", size="sm", c="dimmed"),
            dmc.SimpleGrid([
                component_card("tabler:player-play", "Primary action", "Use for the next task in the workflow.", dmc.Button("Run simulation", leftSection=DashIconify(icon="tabler:player-play", width=16), color="blue", size="sm")),
                component_card("tabler:shield-check", "Validated state", "Use green only for a confirmed successful state.", dmc.Badge("Validated", color="green", variant="light")),
                component_card("tabler:alert-triangle", "Attention state", "Amber signals review without blocking the flow.", dmc.Alert("Review before release", color="yellow", variant="light")),
                component_card("tabler:lock", "Blocking state", "Red means the user must resolve an issue before proceeding.", dmc.Alert("Action required", color="red", variant="light")),
            ], cols={"base":1,"sm":2,"lg":4}, mt="md"),
        ], withBorder=True, p="lg", radius="md"),

        dmc.Grid([
            dmc.GridCol(dmc.Paper([
                dmc.Text("05 · LAYOUT", size="xs", fw=900, c="blue", style={"letterSpacing": ".14em"}),
                dmc.Title("Task-centered shell", order=3, mt="xs"),
                dmc.Text("The navigation hierarchy is fixed: product identity → task rail → parameter context → analysis workspace → delivery.", size="sm", c="dimmed", mt="xs"),
                code_block('AppShell\n├─ Header: brand + project actions\n├─ Navbar: task navigation\n└─ Main\n   ├─ Task rail\n   ├─ Parameter panel\n   └─ Analysis workspace'),
            ], withBorder=True, p="lg", radius="md"), span={"base":12,"md":6}),
            dmc.GridCol(dmc.Paper([
                dmc.Text("06 · ACCESSIBILITY", size="xs", fw=900, c="blue", style={"letterSpacing": ".14em"}),
                dmc.Title("Engineering UI that remains usable", order=3, mt="xs"),
                dmc.List([
                    dmc.ListItem("Never rely on color alone to communicate status."),
                    dmc.ListItem("Keep keyboard focus visible on interactive controls."),
                    dmc.ListItem("Use labels and tooltips for icon-only navigation."),
                    dmc.ListItem("Respect prefers-reduced-motion."),
                    dmc.ListItem("Maintain readable contrast on navy/slate surfaces."),
                ], size="sm", mt="md"),
            ], withBorder=True, p="lg", radius="md"), span={"base":12,"md":6}),
        ], gutter="md"),

        dmc.Paper([
            dmc.Group([brand_lockup(42, show_descriptor=False), dmc.Badge("Implementation reference", color="blue", variant="light")], justify="space-between"),
            dmc.Text("The design system is the source of truth for new ROSCA screens. New components should reuse these tokens, icon vocabulary and interaction states before introducing new visual patterns.", size="sm", c="dimmed", mt="md"),
        ], withBorder=True, p="lg", radius="md", className="ds-footer"),
    ], gap="md", className="design-system-page")
