from __future__ import annotations

from dash import html
import dash_mantine_components as dmc
from dash_iconify import DashIconify

ROSCA_BLUE = "#0E68FF"
ROSCA_NAVY = "#0F172A"
ROSCA_SLATE = "#1E293B"
ROSCA_TEXT = "#CBD5E1"
ROSCA_GREEN = "#22C55E"


def mark(size: int = 34, *, compact: bool = False):
    """ROSCA proposal 3 mark: R + hexagonal engineering geometry."""
    return html.Div(
        html.Img(src="/assets/rosca-symbol.svg", style={"width": f"{size}px", "height": f"{size}px", "display": "block"}),
        className="rosca-brand-mark",
        title="ROSCA symbol",
        **({"data-compact": "true"} if compact else {}),
    )


def wordmark(size: str = "md", *, show_descriptor: bool = True):
    sizes = {"sm": (18, "xs"), "md": (25, "sm"), "lg": (34, "md")}
    title_size, descriptor_size = sizes.get(size, sizes["md"])
    children = [
        dmc.Text(
            "ROSCA",
            size="lg",
            fw=900,
            lh=1,
            style={"fontSize": f"{title_size}px", "fontFamily": "Montserrat, Inter, sans-serif", "letterSpacing": ".075em", "color": "var(--rosca-text)"},
        ),
    ]
    if show_descriptor:
        children.append(dmc.Text("ENGINEERING INTELLIGENCE", size=descriptor_size, fw=700, c="blue", style={"letterSpacing": ".11em", "fontFamily": "Inter, sans-serif"}))
    return dmc.Stack(children, gap=3)


def brand_lockup(size: int = 34, *, show_descriptor: bool = True):
    return dmc.Group([mark(size), wordmark("md", show_descriptor=show_descriptor)], gap="sm", wrap="nowrap")


def icon(name: str, width: int = 18):
    return DashIconify(icon=name, width=width)
