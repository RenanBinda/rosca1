# ROSCA Design System

## 1. Product principle

> **Engineering design is about making technical information easy to inspect, trust and act on.**

ROSCA should feel like an engineering instrument, not a generic dashboard. Visual hierarchy therefore favors:

- data density without visual noise;
- predictable spatial structure;
- strong numeric alignment;
- explicit units;
- visible system state;
- restrained color used for semantics;
- reversible actions;
- progressive disclosure for advanced controls.

## 2. Brand / product language

**ROSCA**

**Real-time Online Screw Compressor Analysis**

Recommended short labels:

- Profile
- Rotor
- Simulation
- Results
- Export

Avoid ambiguous labels such as “Home”, “Data”, “Run”, or “Output” when a domain-specific label is available.

## 3. Color tokens

### Core

| Token | Value | Use |
|---|---|---|
| `rosca.5` | `#42B7FF` | primary interaction / Main rotor |
| `rosca.6` | `#2196E0` | active/pressed |
| `info` | blue | informational feedback |
| `success` | teal | valid / completed |
| `warning` | yellow | caution / non-blocking issue |
| `danger` | red | blocking validation error |
| `gate` | `#FF5C70` | Gate rotor / comparison line |

### Semantic rule

Blue communicates interaction and primary analysis. Red is reserved for Gate in charts and for genuinely dangerous/error states in controls. Green/teal means valid or complete. Do not use color as the only status indicator; pair it with text/icon.

## 4. Typography

- Primary UI: Inter/system sans.
- Monospace: JetBrains Mono/system monospace for calculation logs and raw values.
- Page title: 28–32 px equivalent, weight 800.
- Section title: 13–15 px, weight 800.
- Field label: 12–13 px.
- Technical table: 12 px.
- Helper text: 11–12 px.

## 5. Spacing

Base spacing scale:

`xs 0.35rem` · `sm 0.55rem` · `md 0.8rem` · `lg 1.05rem` · `xl 1.35rem`

Use spacing to group information semantically. Do not create large decorative whitespace inside dense engineering forms.

## 6. Surfaces

### Dark mode

- Application background: near-black blue charcoal.
- Panels: dark slate.
- Secondary panels: slightly lighter slate.
- Borders: cool gray-blue.
- Primary text: near-white.
- Secondary text: desaturated blue-gray.

### Light mode

- Application background: cool gray-white.
- Panels: white.
- Secondary panels: very light gray-blue.
- Borders: neutral cool gray.
- Primary text: deep blue-charcoal.

## 7. Components

### Navigation

`AppShellNavbar` contains the global workflow. Each item has icon + label and an explicit active state.

### Header

The header always identifies the product and the current workspace context. Theme switching is global and persistent.

### Context sidebar

`AppShellAside` is reserved for high-value contextual information: center distance, clearance, system state and interaction guidance. It should not become a second parameter form.

### Numeric input

Every engineering input should expose:

- clear label;
- unit suffix;
- valid range where known;
- helper tooltip when domain knowledge is required;
- immediate error feedback;
- no unexplained abbreviations.

### Status badge

Statuses are short, explicit and semantic:

`Ready` · `Valid` · `Running` · `Completed` · `Warning` · `Action required`

### Plotly graph

The graph is an analytical workspace, not a decoration. Hover should expose exact coordinates, and zoom/pan state should persist across non-structural updates.

### AG Grid

Use AG Grid for coordinate/result datasets requiring sorting, filtering, pagination, selection or future editing. Column headers should include units.

## 8. Interaction states

Every interactive control should support:

1. Default
2. Hover
3. Focus
4. Pressed
5. Disabled
6. Loading
7. Valid
8. Invalid

### Validation hierarchy

- **Field error:** local problem, shown adjacent to input.
- **Panel error:** multiple related fields invalid.
- **Workflow blocking:** simulation button disabled or guarded until required conditions are met.
- **System error:** calculation/service problem, displayed in a persistent alert and calculation log.

## 9. Simulation behavior

When the user starts a simulation:

1. Freeze or clearly mark parameters that cannot change during calculation.
2. Show calculation stage.
3. Show progress.
4. Keep the current screen context visible.
5. Append meaningful calculation log events.
6. On completion, move the user to Results only if that behavior is explicitly approved; otherwise show a completion action.

The proposal specifically calls for skeletons and progress bars instead of generic “Updating” feedback. fileciteturn0file0L100-L108

## 10. Motion

- Default transition: 180–220 ms.
- Use ease-out for panels/navigation.
- Do not animate numeric data continuously unless the calculation itself is being streamed.
- Respect reduced-motion preferences.

## 11. Accessibility

Minimum UI requirements:

- keyboard-focus visibility;
- labels associated with inputs;
- icons accompanied by tooltip/accessible label when meaning is not obvious;
- no status communicated only by color;
- sufficient contrast in both themes;
- table headers with units;
- keyboard-accessible navigation and actions.

## 12. Responsive behavior

Desktop: three functional zones — navigation, analytical workspace, contextual aside.

Tablet: collapse contextual aside first.

Mobile: collapse navigation and contextual aside into drawers; prioritize Profile → Simulation → Results flow.

## 13. Component ownership

- `components/theme.py`: global visual tokens.
- `components/ui.py`: reusable UI primitives.
- `assets/rosca.css`: application-specific styling.
- `engine/`: engineering calculation adapter only.
- `app.py`: orchestration and callbacks.

This separation is intentional: UX changes should not require rewriting engineering calculations, and solver changes should not require redesigning the interaction layer.
