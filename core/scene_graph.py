from __future__ import annotations

from core.scene_node import SceneNode


class SceneGraph:
    """Tree structure for hierarchical scene composition."""

    def __init__(self) -> None:
        self.root = SceneNode("root", {"visible": False})
        self.nodes_by_name: dict[str, SceneNode] = {self.root.name: self.root}

    def add_node(self, node: SceneNode, parent: SceneNode | None = None) -> None:
        target_parent = parent or self.root
        target_parent.add_child(node)
        self._index_node(node)

    def traverse(self, node: SceneNode | None = None) -> list[SceneNode]:
        current = node or self.root
        nodes = [current]

        for child in current.children:
            nodes.extend(self.traverse(child))

        return nodes

    def find_node(self, name: str) -> SceneNode:
        try:
            return self.nodes_by_name[name]
        except KeyError as exc:
            raise KeyError(f"Scene node '{name}' was not found") from exc

    def get_node(self, name: str) -> SceneNode | None:
        return self.nodes_by_name.get(name)

    def reset_runtime_state(self) -> None:
        self.root.reset_runtime_state()

    def _index_node(self, node: SceneNode) -> None:
        if node.name in self.nodes_by_name:
            raise ValueError(f"Duplicate scene node name: {node.name}")

        self.nodes_by_name[node.name] = node
        for child in node.children:
            self._index_node(child)
