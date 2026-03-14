from __future__ import annotations

from typing import Any


class SceneNode:
    """A node in the scene graph with local and inherited transform state."""

    def __init__(self, name: str, data: dict[str, Any] | None = None) -> None:
        self.name = name
        self.data = data or {}
        self.children: list[SceneNode] = []
        self.parent: SceneNode | None = None

        self.node_type = self.data.get("type")
        self.base_position = [
            float(self.data.get("x", 0)),
            float(self.data.get("y", 0)),
        ]
        self.base_scale = self._normalize_pair(self.data.get("scale", [1, 1]), default=1.0)
        self.base_rotation = float(self.data.get("rotation", 0))
        self.base_opacity = self._normalize_scalar(self.data.get("opacity", 1.0), default=1.0)
        self.layer = int(self.data.get("layer", 0))
        self.visible = bool(self.data.get("visible", True))
        self.position = list(self.base_position)
        self.scale = list(self.base_scale)
        self.rotation = self.base_rotation
        self.opacity = self.base_opacity

    def add_child(self, node: SceneNode) -> None:
        node.parent = self
        self.children.append(node)

    def reset_runtime_state(self) -> None:
        self.position = list(self.base_position)
        self.scale = list(self.base_scale)
        self.rotation = self.base_rotation
        self.opacity = self.base_opacity

        for child in self.children:
            child.reset_runtime_state()

    def apply_property(self, property_name: str, value: Any) -> None:
        if property_name == "position":
            self.position = self._normalize_pair(value, default=0.0)
            return

        if property_name == "scale":
            self.scale = self._normalize_pair(value, default=1.0)
            return

        if property_name == "rotation":
            self.rotation = self._normalize_scalar(value, default=0.0)
            return

        if property_name == "opacity":
            self.opacity = min(1.0, max(0.0, self._normalize_scalar(value, default=1.0)))
            return

        raise ValueError(f"Unsupported animated property: {property_name}")

    def get_world_position(self) -> list[float]:
        if self.parent is None:
            return list(self.position)

        parent_position = self.parent.get_world_position()
        return [
            parent_position[0] + self.position[0],
            parent_position[1] + self.position[1],
        ]

    def get_world_scale(self) -> list[float]:
        if self.parent is None:
            return list(self.scale)

        parent_scale = self.parent.get_world_scale()
        return [
            parent_scale[0] * self.scale[0],
            parent_scale[1] * self.scale[1],
        ]

    def get_world_rotation(self) -> float:
        if self.parent is None:
            return self.rotation
        return self.parent.get_world_rotation() + self.rotation

    def get_world_opacity(self) -> float:
        if self.parent is None:
            return self.opacity
        return self.parent.get_world_opacity() * self.opacity

    @staticmethod
    def _normalize_pair(value: Any, default: float) -> list[float]:
        if isinstance(value, (int, float)):
            return [float(value), float(value)]

        if isinstance(value, list) and len(value) == 2:
            return [float(value[0]), float(value[1])]

        return [default, default]

    @staticmethod
    def _normalize_scalar(value: Any, default: float) -> float:
        if isinstance(value, (int, float)):
            return float(value)

        return default
