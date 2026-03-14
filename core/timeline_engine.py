from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.scene_graph import SceneGraph


@dataclass(slots=True)
class AnimationTrack:
    node_name: str
    property_name: str
    start_time: float
    end_time: float
    start_value: float | list[float]
    end_value: float | list[float]

    def value_at(self, current_time: float) -> float | list[float] | None:
        if current_time < self.start_time:
            return None

        if current_time >= self.end_time:
            return self.end_value

        duration = self.end_time - self.start_time
        if duration <= 0:
            return self.end_value

        progress = (current_time - self.start_time) / duration
        return interpolate_value(self.start_value, self.end_value, progress)


class TimelineEngine:
    """Apply deterministic animation tracks onto a scene graph."""

    def __init__(self, scene_graph: SceneGraph, animations: list[dict[str, Any]] | None = None) -> None:
        self.scene_graph = scene_graph
        self.tracks = [self._build_track(animation) for animation in animations or []]

    def evaluate(self, current_time: float) -> None:
        self.scene_graph.reset_runtime_state()

        for track in self.tracks:
            value = track.value_at(current_time)
            if value is None:
                continue

            node = self.scene_graph.find_node(track.node_name)
            node.apply_property(track.property_name, value)

    def _build_track(self, animation: dict[str, Any]) -> AnimationTrack:
        node_name = str(animation["node"])
        property_name = str(animation["property"])
        start_time = float(animation.get("start_time", 0.0))
        end_time = float(animation["end_time"])

        if end_time < start_time:
            raise ValueError(
                f"Animation for '{node_name}' property '{property_name}' has end_time before start_time"
            )

        return AnimationTrack(
            node_name=node_name,
            property_name=property_name,
            start_time=start_time,
            end_time=end_time,
            start_value=normalize_value(animation["from"]),
            end_value=normalize_value(animation["to"]),
        )


def normalize_value(value: Any) -> float | list[float]:
    if isinstance(value, (int, float)):
        return float(value)

    if isinstance(value, list):
        return [float(item) for item in value]

    raise TypeError(f"Unsupported animation value: {value!r}")


def interpolate_value(
    start_value: float | list[float],
    end_value: float | list[float],
    progress: float,
) -> float | list[float]:
    clamped_progress = min(1.0, max(0.0, progress))

    if isinstance(start_value, list) and isinstance(end_value, list):
        if len(start_value) != len(end_value):
            raise ValueError("Animated list values must have matching lengths")

        return [
            start_item + (end_item - start_item) * clamped_progress
            for start_item, end_item in zip(start_value, end_value)
        ]

    if isinstance(start_value, float) and isinstance(end_value, float):
        return start_value + (end_value - start_value) * clamped_progress

    raise TypeError("Animated start/end values must both be floats or both be float lists")
