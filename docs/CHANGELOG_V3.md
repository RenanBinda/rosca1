# ROSCA UI v3 — correction and alignment pass

## Main defects corrected

1. **Left navigation clipping**
   - Default state is icon-only.
   - Hovering an item displays its label in a tooltip.
   - Expand/compact control changes AppShell navbar width from 72px to 218px.
   - Expanded state shows icon + label.
   - Expanded state is persisted in local storage.

2. **Global light/dark mode**
   - Uses DMC `ColorSchemeToggle`.
   - Custom CSS is keyed to Mantine's `data-mantine-color-scheme` attribute.
   - Plotly templates and AG Grid theme follow the active scheme.

3. **Profile chart missing**
   - Profile now reproduces the HTML composition: parameters | Plotly workspace | contextual properties.
   - 2D PROFILE is the default view.
   - 3D ROTOR can be switched without leaving Profile.

4. **Navigation pages not loading**
   - Profile, Rotor, Simulation, Results and Export are all instantiated in the shell and switched through a single navigation state.
   - The shell remains stable while page content changes.

5. **Interactions**
   - Restore defaults.
   - Real-time validation.
   - Profile 2D/3D switch.
   - Rotor 2D/3D switch.
   - Simulation progress.
   - Export from the Export page, Profile action and Context Sidebar.
   - Ctrl+Enter simulation shortcut.

## Reference hierarchy

The visual hierarchy follows the supplied HTML prototype first, then the uploaded investment proposal. The external reference `https://rosca-app.com/` is recorded as a contextual product reference; the live page was reachable during review but its visual payload was not available to the text crawler.
