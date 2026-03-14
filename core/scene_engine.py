from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import cv2

from core.renderer import Renderer
from core.scene_graph import SceneGraph
from core.scene_node import SceneNode
from core.timeline_engine import TimelineEngine


class SceneEngine:
    """Load scene data and export it as a video."""

    def __init__(self, scene_file: str | Path) -> None:
        self.scene_file = Path(scene_file).resolve()
        with self.scene_file.open("r", encoding="utf-8") as handle:
            self.data = json.load(handle)

        self.fps = int(self.data["fps"])
        self.width = int(self.data["width"])
        self.height = int(self.data["height"])
        self.assets_dir = self.scene_file.parent.parent / "assets"
        self.renderer = Renderer(self.width, self.height, assets_dir=self.assets_dir)

    def generate_video(self, output_file: str | Path) -> Path:
        output_path = Path(output_file).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(str(output_path), fourcc, self.fps, (self.width, self.height))
        if not video.isOpened():
            raise RuntimeError(f"Failed to open video writer for {output_path}")

        try:
            for scene in self.data["scenes"]:
                frame_count = int(float(scene["duration"]) * self.fps)
                scene_graph = self.build_graph(scene.get("objects", []))
                timeline = TimelineEngine(scene_graph, scene.get("animations", []))
                nodes = scene_graph.traverse()
                for frame_index in range(frame_count):
                    current_time = frame_index / self.fps
                    timeline.evaluate(current_time)
                    frame = self.renderer.render_scene(nodes)
                    video.write(frame)
        finally:
            video.release()

        return output_path

    def build_graph(self, objects: list[dict[str, Any]]) -> SceneGraph:
        graph = SceneGraph()

        for index, obj in enumerate(objects):
            node = self._build_node(obj, fallback_name=f"node_{index}")
            graph.add_node(node)

        return graph

    def _build_node(self, obj: dict[str, Any], fallback_name: str) -> SceneNode:
        node = SceneNode(obj.get("name", fallback_name), obj)

        for child_index, child_obj in enumerate(obj.get("children", [])):
            child_node = self._build_node(
                child_obj,
                fallback_name=f"{node.name}_child_{child_index}",
            )
            node.add_child(child_node)

        return node
