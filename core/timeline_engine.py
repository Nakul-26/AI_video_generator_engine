from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.easing import EASING_FUNCTIONS
from core.scene_graph import SceneGraph


@dataclass(slots=True)
class AnimationTrack:
    node_name: str
    property_name: str
    start_time: float
    end_time: float
    delay: float
    start_value: float | list[float]
    end_value: float | list[float]
    easing_name: str
    loop: bool

    def value_at(self, current_time: float) -> float | list[float] | None:
        effective_start_time = self.start_time + self.delay
        effective_end_time = self.end_time + self.delay

        if current_time < effective_start_time:
            return None

        duration = effective_end_time - effective_start_time
        if duration <= 0:
            return self.end_value

        if self.loop:
            progress = ((current_time - effective_start_time) % duration) / duration
        else:
            if current_time >= effective_end_time:
                return self.end_value

            progress = (current_time - effective_start_time) / duration

        clamped_progress = min(1.0, max(0.0, progress))
        eased_progress = EASING_FUNCTIONS[self.easing_name](clamped_progress)
        return interpolate_value(self.start_value, self.end_value, eased_progress)


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
        delay = float(animation.get("delay", 0.0))
        easing_name = str(animation.get("easing", "linear"))
        loop = bool(animation.get("loop", False))

        if end_time < start_time:
            raise ValueError(
                f"Animation for '{node_name}' property '{property_name}' has end_time before start_time"
            )

        if delay < 0:
            raise ValueError(
                f"Animation for '{node_name}' property '{property_name}' has a negative delay"
            )

        if easing_name not in EASING_FUNCTIONS:
            raise ValueError(f"Invalid easing type: {easing_name}")

        return AnimationTrack(
            node_name=node_name,
            property_name=property_name,
            start_time=start_time,
            end_time=end_time,
            delay=delay,
            start_value=normalize_value(animation["from"]),
            end_value=normalize_value(animation["to"]),
            easing_name=easing_name,
            loop=loop,
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
    if isinstance(start_value, list) and isinstance(end_value, list):
        if len(start_value) != len(end_value):
            raise ValueError("Animated list values must have matching lengths")

        return [
            start_item + (end_item - start_item) * progress
            for start_item, end_item in zip(start_value, end_value)
        ]

    if isinstance(start_value, float) and isinstance(end_value, float):
        return start_value + (end_value - start_value) * progress

    raise TypeError("Animated start/end values must both be floats or both be float lists")
