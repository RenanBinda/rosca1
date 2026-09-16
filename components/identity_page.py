from __future__ import annotations

from dash import html
import dash_mantine_components as dmc
from dash_iconify import DashIconify

from components.brand import ROSCA_BLUE, ROSCA_GREEN, ROSCA_NAVY, ROSCA_SLATE, ROSCA_TEXT, brand_lockup, mark


PALETTE = [
    ("ROSCA Blue", ROSCA_BLUE, "#0E68FF", "Primary action / focus"),
    ("Deep Navy", ROSCA_NAVY, "#0F172A", "Brand foundation / dark UI"),
    ("Industrial Slate", ROSCA_SLATE, "#1E293B", "Panels / surfaces"),
    ("Technical Mist", ROSCA_TEXT, "#CBD5E1", "Text / secondary information"),
    ("Signal Green", ROSCA_GREEN, "#22C55E", "Success / validated state"),
]


def swatch(name: str, color: str, hex_value: str, use: str):
    return dmc.Paper(
        dmc.Stack([
            html.Div(style={"height": "72px", "borderRadius": "8px", "background": color, "border": "1px solid rgba(255,255,255,.12)"}),
            dmc.Text(name, fw=800, size="sm"),
            dmc.Text(hex_value, ff="monospace", size="xs", c="blue"),
            dmc.Text(use, size="xs", c="dimmed"),
        ], gap=4),
        withBorder=True, p="sm", radius="md", className="identity-swatch",
    )


def identity_page():
    return dmc.Stack([
        dmc.Group([
            dmc.Stack([
                dmc.Text("BRAND SYSTEM", size="xs", fw=900, c="blue", style={"letterSpacing": ".18em"}),
                dmc.Title("ROSCA visual identity", order=1),
                dmc.Text("Proposta 3 · Robusta · Industrial · Tecnológica", size="md", c="dimmed"),
            ], gap=3),
            dmc.Badge("Engineering Intelligence", color="blue", variant="light", size="lg"),
        ], justify="space-between", align="flex-start"),

        dmc.Grid([
            dmc.GridCol(dmc.Paper([
                dmc.Text("Símbolo", size="xs", fw=800, c="dimmed", tt="uppercase"),
                dmc.Center(mark(180), style={"minHeight": "230px"}),
                dmc.Text("R + geometria hexagonal", fw=800, ta="center"),
                dmc.Text("A forma combina a inicial de ROSCA com uma moldura geométrica que remete a peças, seção, precisão e ambiente industrial.", size="sm", c="dimmed", ta="center"),
            ], withBorder=True, p="xl", radius="md"), span={"base":12,"md":5}),
            dmc.GridCol(dmc.Paper([
                dmc.Text("Wordmark", size="xs", fw=800, c="dimmed", tt="uppercase"),
                dmc.Center(brand_lockup(72), style={"minHeight": "230px"}),
                dmc.Divider(my="md"),
                dmc.Text("ROSCA", fw=900, size="xl", style={"letterSpacing": ".075em"}),
                dmc.Text("ENGINEERING INTELLIGENCE", fw=700, size="sm", c="blue", style={"letterSpacing": ".11em"}),
                dmc.Text("Assinatura verbal para posicionar o produto como uma camada de inteligência aplicada à engenharia.", size="sm", c="dimmed"),
            ], withBorder=True, p="xl", radius="md"), span={"base":12,"md":7}),
        ], gutter="md"),

        dmc.Stack([
            dmc.Group([dmc.Title("Paleta cromática", order=2), dmc.Text("Contraste técnico com sinalização funcional", size="sm", c="dimmed")], justify="space-between"),
            dmc.SimpleGrid([swatch(*item) for item in PALETTE], cols={"base":1,"xs":2,"lg":5}, spacing="sm"),
        ], gap="sm"),

        dmc.Grid([
            dmc.GridCol(dmc.Paper([
                dmc.Group([DashIconify(icon="tabler:typography", width=20), dmc.Title("Tipografia", order=3)], gap="xs"),
                dmc.Text("Montserrat", size="32px", fw=800, mt="md", style={"letterSpacing": ".01em"}),
                dmc.Text("Display, títulos e marca", size="sm", c="dimmed"),
                dmc.Divider(my="md"),
                dmc.Text("Inter", size="26px", fw=600),
                dmc.Text("Interface, dados, controles e textos longos", size="sm", c="dimmed"),
                dmc.Text("Aa  0123456789  →  %  Ø  α", ff="monospace", mt="md", c="blue"),
            ], withBorder=True, p="lg", radius="md"), span={"base":12,"md":6}),
            dmc.GridCol(dmc.Paper([
                dmc.Group([DashIconify(icon="tabler:shape", width=20), dmc.Title("Linguagem visual", order=3)], gap="xs"),
                dmc.SimpleGrid([
                    dmc.Stack([dmc.ThemeIcon(DashIconify(icon="tabler:hexagon-3d"), size="xl", color="blue", variant="light"), dmc.Text("Geométrica", fw=700, size="sm"), dmc.Text("Formas precisas e modulares", size="xs", c="dimmed")], gap=4),
                    dmc.Stack([dmc.ThemeIcon(DashIconify(icon="tabler:activity"), size="xl", color="teal", variant="light"), dmc.Text("Analítica", fw=700, size="sm"), dmc.Text("Dados e estados legíveis", size="xs", c="dimmed")], gap=4),
                    dmc.Stack([dmc.ThemeIcon(DashIconify(icon="tabler:settings"), size="xl", color="blue", variant="light"), dmc.Text("Industrial", fw=700, size="sm"), dmc.Text("Robustez sem excesso visual", size="xs", c="dimmed")], gap=4),
                ], cols=3, mt="md"),
            ], withBorder=True, p="lg", radius="md"), span={"base":12,"md":6}),
        ], gutter="md"),

        dmc.Paper([
            dmc.Group([dmc.Title("Aplicação na interface", order=2), dmc.Badge("ROSCA UI", color="blue", variant="filled")], justify="space-between"),
            dmc.SimpleGrid([
                dmc.Stack([dmc.Text("01", c="blue", fw=900), dmc.Text("Navegação", fw=800), dmc.Text("Azul técnico para ações e foco; navy/slate para estrutura e profundidade.", size="sm", c="dimmed")], gap=4),
                dmc.Stack([dmc.Text("02", c="blue", fw=900), dmc.Text("Análise", fw=800), dmc.Text("Superfícies escuras, linhas geométricas e informação numérica em primeiro plano.", size="sm", c="dimmed")], gap=4),
                dmc.Stack([dmc.Text("03", c="green", fw=900), dmc.Text("Estados", fw=800), dmc.Text("Verde sinaliza validação e conclusão; vermelho e âmbar ficam reservados a problemas e atenção.", size="sm", c="dimmed")], gap=4),
                dmc.Stack([dmc.Text("04", c="blue", fw=900), dmc.Text("Interação", fw=800), dmc.Text("Ícones lineares e controles compactos reforçam o fluxo task-centered.", size="sm", c="dimmed")], gap=4),
            ], cols={"base":1,"sm":2,"lg":4}, mt="md"),
        ], withBorder=True, p="lg", radius="md"),

        dmc.Alert(
            "A proposta 3 passa a ser o sistema visual principal do produto: símbolo, wordmark, cor, tipografia, ícones, estados e superfícies seguem a mesma linguagem industrial-tecnológica.",
            title="Diretriz de marca",
            color="blue",
            variant="light",
            icon=DashIconify(icon="tabler:brand-asana", width=20),
        ),
    ], gap="lg", className="identity-page")
