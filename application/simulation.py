from __future__ import annotations

STAGES: tuple[tuple[str, int], ...] = (
    ("Preparing", 5),
    ("Validating parameters", 15),
    ("Generating geometry", 35),
    ("Calculating metrics", 60),
    ("Running validation", 78),
    ("Preparing results", 92),
    ("Completed", 100),
)


def stage_for_progress(progress: int) -> str:
    p = max(0, min(100, int(progress)))
    current = STAGES[0][0]
    for name, threshold in STAGES:
        if p >= threshold:
            current = name
    return current
