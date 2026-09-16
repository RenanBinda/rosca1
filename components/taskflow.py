from __future__ import annotations

import dash_mantine_components as dmc
from dash_iconify import DashIconify


# The vocabulary is intentionally task-oriented: users see what they can do,
# not internal implementation names. Icons use Tabler via Iconify.
ACTIONS = {
    "new": ("New project", "tabler:file-plus"),
    "open": ("Open project", "tabler:folder-open"),
    "save": ("Save project", "tabler:device-floppy"),
    "validate": ("Validate", "tabler:shield-check"),
    "simulate": ("Run simulation", "tabler:player-play"),
    "inspect": ("Inspect", "tabler:search"),
    "measure": ("Measure", "tabler:ruler-measure"),
    "compare": ("Compare", "tabler:git-compare"),
    "export": ("Export", "tabler:file-export"),
    "help": ("Help", "tabler:help-circle"),
}


def action_button(action: str, *, button_id: str | None = None, primary: bool = False):
    label, icon_name = ACTIONS[action]
    return dmc.Button(
        label,
        id=button_id,
        leftSection=DashIconify(icon=icon_name, width=16),
        variant="filled" if primary else "subtle",
        color="blue" if primary else "gray",
        size="sm",
        radius="sm",
    )


def task_step(number: int, title: str, description: str, state: str = "pending"):
    colors = {"done": "teal", "active": "blue", "blocked": "red", "pending": "gray"}
    icons = {"done": "tabler:check", "active": "tabler:arrow-right", "blocked": "tabler:lock", "pending": "tabler:circle"}
    return dmc.Group([
        dmc.ThemeIcon(DashIconify(icon=icons[state], width=14), color=colors[state], variant="light", size="sm"),
        dmc.Stack([
            dmc.Text(f"{number}. {title}", size="sm", fw=700),
            dmc.Text(description, size="xs", c="dimmed"),
        ], gap=1),
    ], align="flex-start", gap="sm")


def task_rail(active: int = 1):
    steps = [
        ("Define", "Set the rotor and operating parameters."),
        ("Validate", "Resolve blocking geometry and domain issues."),
        ("Simulate", "Run the analysis and follow its progress."),
        ("Inspect", "Explore geometry, metrics and critical points."),
        ("Deliver", "Compare, document and export the result."),
    ]
    content = []
    for i, (title, description) in enumerate(steps, 1):
        state = "active" if i == active else "done" if i < active else "pending"
        content.append(task_step(i, title, description, state))
    return dmc.Paper(dmc.Stack(content, gap="md"), withBorder=True, radius="md", p="md", className="task-rail")
