# ROSCA UX Evolution

## Design principle

ROSCA now treats the engineering task as the primary navigation object. The user should always understand:

1. Where am I?
2. What am I configuring?
3. What is blocking me?
4. What is the next action?
5. What changed after I acted?
6. What can I inspect or deliver now?

## Autodesk/Fusion benchmark translated to ROSCA

Autodesk Fusion groups capabilities into purpose-driven workspaces and organizes commands into logical toolbar tabs. It also exposes contextual tools when the user enters a temporary task mode. ROSCA adopts the same interaction logic without copying Autodesk visual assets or proprietary UI: workspaces become **Define, Simulate, Inspect and Deliver**, and the action vocabulary is explicit and icon-led.

Official references used for this benchmark:
- Fusion interface overview: https://help.autodesk.com/view/fusion360/ENU/?contextId=LP-STEPS-P13N-SNP-GS-OTH-CRD-1
- Fusion workspaces: https://help.autodesk.com/cloudhelp/ENU/Fusion-GetStarted/files/GS-WORKSPACES.htm
- Fusion marking menu: https://help.autodesk.com/cloudhelp/ENU/Fusion-GetStarted/files/GUID-6514ABC1-CB75-4F0B-AB0E-316FAD36BA93.htm

## ROSCA interaction model

### Define
Set parameters, restore a preset, validate, and see field-level guidance.

### Simulate
Run a calculation only after blocking validation issues are resolved. Progress communicates stages instead of a generic spinner.

### Inspect
Switch between 2D profile, 3D rotor, clearance and deviation views. Hover is used as the first inspection gesture; measure and fit-view are persistent contextual tools.

### Deliver
Review result identity, validation state and coordinate data, then export a portable project package.

## Icon language

Icons are sourced through Tabler/Iconify and chosen by action semantics: create, open, save, validate, simulate, inspect, measure, compare, export and help. Labels remain available through tooltips, so icon-first navigation does not require memorizing symbols.

## Engineering integrity

The repository currently contains a **preview geometry adapter**, not a validated compressor engineering solver. The UX now makes that distinction explicit. No unsupported engineering relationship is invented by the validation layer.

The next engineering milestone is to replace `engine/profile.py::generate_profile_preview` with the validated production solver while preserving the interaction contract.
