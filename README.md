# ROSCA — Dash / Mantine / Plotly / AG Grid

ROSCA = **Real-time Online Screw Compressor Analysis**.

This revision deliberately aligns the Python/Dash interface with the supplied HTML prototype: 72px compact navigation rail, tooltip labels, optional expanded navigation, 310px parameter panel, Plotly workspace, bottom result tabs and 340px contextual sidebar.

## Main corrections

- Profile now contains the Plotly 2D profile in the primary workspace.
- 2D/3D Plotly views are available from Profile and Rotor.
- Left navigation starts icon-only; labels appear in tooltips and the rail can be expanded.
- Navigation width is persisted locally.
- Light/dark mode is handled by DMC `ColorSchemeToggle` and CSS keyed to `data-mantine-color-scheme`, including Plotly and AG Grid theme updates.
- Profile, Rotor, Simulation, Results and Export screens are wired through the same application shell.
- AG Grid is used for coordinate/result data.
- Simulation has progress states and a calculation log.
- Export creates a ZIP package.

## Engineering note

The supplied investment proposal defines the UX/UI and frontend implementation, including Plotly Dash, AppShell, custom parameter validation, AG Grid, Plotly interaction, contextual sidebars, transitions, loading/progress feedback and dark/light design system. It does not provide the validated compressor equations. Therefore `engine/profile.py` remains a clearly identified preview adapter and must be replaced by the validated ROSCA engineering solver before production engineering use.

## Run

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# macOS/Linux
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
