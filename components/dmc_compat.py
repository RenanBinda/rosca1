"""Compatibility helpers for the ROSCA UI against dash-mantine-components 2.8.

The evolution UI was written against a ColorSchemeToggle API that accepted a
legacy ``button`` argument. DMC 2.8 exposes the toggle as an icon/button itself
and no longer accepts that argument. MantineProvider also should not be forced
to one scheme when the UI offers a color-scheme toggle.

Keep this shim small and isolated so the application code can use the intended
interaction model without depending on version-specific constructor details.
"""

from __future__ import annotations

import dash_mantine_components as dmc


_OriginalColorSchemeToggle = dmc.ColorSchemeToggle


class ColorSchemeToggleCompat(_OriginalColorSchemeToggle):
    def __init__(self, *args, **kwargs):
        # DMC <= 2.7 examples used ``button`` as an implementation detail.
        # DMC 2.8 rejects it, while the component itself is already interactive.
        kwargs.pop("button", None)
        kwargs.setdefault("lightIcon", "☀")
        kwargs.setdefault("darkIcon", "☾")
        super().__init__(*args, **kwargs)


dmc.ColorSchemeToggle = ColorSchemeToggleCompat


_OriginalMantineProvider = dmc.MantineProvider


class MantineProviderCompat(_OriginalMantineProvider):
    def __init__(self, *args, **kwargs):
        # Do not lock the application to dark mode: the header toggle must be
        # able to switch between light and dark schemes.
        kwargs.pop("forceColorScheme", None)
        super().__init__(*args, **kwargs)


dmc.MantineProvider = MantineProviderCompat
