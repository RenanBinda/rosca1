# ROSCA UX implementation map

| HTML reference | Dash implementation |
|---|---|
| Compact left rail | `dmc.AppShellNavbar` 72px |
| Hover label | `dmc.Tooltip` around every navigation item |
| Expand / compact | `nav-resize` + AppShell `navbar.width` callback |
| Profile settings | `profile_parameters_panel()` |
| Main workspace | `workspace_card()` + Plotly |
| 2D profile | `make_figure_2d()` |
| 3D rotor | `make_figure_3d()` |
| Bottom coordinates | Dash AG Grid |
| Context sidebar | `context_sidebar()` |
| Light / dark | DMC `ColorSchemeToggle` + theme-aware CSS + Plotly/AG Grid callback |
| Simulation | `simulation_screen()` + timer callback |
| Results | `results_screen()` + AG Grid |
| Export | `export_screen()` + ZIP callback |

## Reference limitation

`https://rosca-app.com/` was supplied as an external reference. Its page was reachable during review, but its visual/content payload was not exposed to the text crawler. The supplied HTML prototype and the uploaded investment proposal therefore remain the grounded design references for this implementation.
