from __future__ import annotations


class TimelineEngine:
    """Placeholder for future event and animation scheduling."""

    def __init__(self) -> None:
        self.events: list[dict] = []

    def add_event(self, event: dict) -> None:
        self.events.append(event)
