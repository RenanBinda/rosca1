# ROSCA v4 — Compatibility & Interaction Fix

## Corrigido

### DMC 2.8.0 — ActionIcon
- Replaced unsupported `aria_label` Python prop with `buttonProps={"aria-label": ...}`.
- This matches the component API exposed by Dash Mantine Components 2.8.0.

### Duplicate component IDs
- Removed the unused global `AppShellAside` that duplicated the `context-export` ID already present in the Profile context sidebar.
- The Profile page keeps the visual context sidebar from the approved HTML composition.
- This prevents ambiguous callback targets and makes export interactions deterministic.

### Navigation
- Compact mode: icon only.
- Hover tooltip: section label.
- Expanded mode: icon + label.
- Resize button persists state through `nav-expanded` local storage.

### Theme
- Header and navigation ColorSchemeToggle remain synchronized through Mantine's computed color scheme.
- CSS variables cover the complete application surface.
- Plotly and AG Grid receive the active scheme.

### Plotly
- Profile 2D graph is present in the initial layout and receives updates from the parameter callbacks.
- 3D preview remains available through the Profile tabs.

## Validation
- Python modules pass `py_compile`.
- The runtime environment used for packaging does not include Dash/DMC/AG Grid, so browser execution was not claimed as verified here.


## Plotly color compatibility patch
- Replaced the 8-digit hex `#60738655` used by Plotly `zerolinecolor` with the supported `rgba(96,115,134,0.33)` format.
- Checked the codebase for other 8-digit hex colors in Plotly configuration.
