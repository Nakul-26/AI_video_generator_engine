from __future__ import annotations

from core.scene_node import SceneNode


class SceneGraph:
    """Tree structure for hierarchical scene composition."""

    def __init__(self) -> None:
        self.root = SceneNode("root", {"visible": False})

    def add_node(self, node: SceneNode, parent: SceneNode | None = None) -> None:
        target_parent = parent or self.root
        target_parent.add_child(node)

    def traverse(self, node: SceneNode | None = None) -> list[SceneNode]:
        current = node or self.root
        nodes = [current]

        for child in current.children:
            nodes.extend(self.traverse(child))

        return nodes
