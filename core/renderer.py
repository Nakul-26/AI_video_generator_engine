from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np

from core.scene_node import SceneNode


class Renderer:
    """Render a single frame from scene graph nodes."""

    def __init__(self, width: int, height: int, assets_dir: str | Path | None = None) -> None:
        self.width = width
        self.height = height
        self.assets_dir = Path(assets_dir) if assets_dir else None
        self._image_cache: dict[Path, np.ndarray] = {}

    def render_scene(self, nodes: list[SceneNode]) -> np.ndarray:
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        drawable_nodes = [
            node for node in nodes if node.visible and node.node_type is not None
        ]
        sorted_nodes = sorted(drawable_nodes, key=lambda node: node.layer)

        for node in sorted_nodes:
            obj_type = node.node_type

            if obj_type == "text":
                self._draw_text(frame, node)
            elif obj_type == "circle":
                self._draw_circle(frame, node)
            elif obj_type == "rectangle":
                self._draw_rectangle(frame, node)
            elif obj_type == "image":
                self._draw_image(frame, node)
            else:
                raise ValueError(f"Unsupported object type: {obj_type}")

        return frame

    def _draw_text(self, frame: np.ndarray, node: SceneNode) -> None:
        obj = node.data
        color = tuple(obj.get("color", [255, 255, 255]))
        world_position = node.get_world_position()
        world_scale = node.get_world_scale()
        scale = float(obj.get("font_scale", 1.0)) * world_scale[0]
        thickness = max(1, int(obj.get("thickness", 2)))
        cv2.putText(
            frame,
            obj["value"],
            (int(world_position[0]), int(world_position[1])),
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            color,
            thickness,
            cv2.LINE_AA,
        )

    def _draw_circle(self, frame: np.ndarray, node: SceneNode) -> None:
        obj = node.data
        color = tuple(obj.get("color", [0, 255, 0]))
        thickness = int(obj.get("thickness", -1))
        world_position = node.get_world_position()
        world_scale = node.get_world_scale()
        radius = max(1, int(float(obj["radius"]) * world_scale[0]))
        cv2.circle(
            frame,
            (int(world_position[0]), int(world_position[1])),
            radius,
            color,
            thickness,
        )

    def _draw_rectangle(self, frame: np.ndarray, node: SceneNode) -> None:
        obj = node.data
        color = tuple(obj.get("color", [255, 0, 0]))
        thickness = int(obj.get("thickness", -1))
        world_position = node.get_world_position()
        world_scale = node.get_world_scale()
        x = int(world_position[0])
        y = int(world_position[1])
        width = max(1, int(float(obj["width"]) * world_scale[0]))
        height = max(1, int(float(obj["height"]) * world_scale[1]))
        cv2.rectangle(frame, (x, y), (x + width, y + height), color, thickness)

    def _draw_image(self, frame: np.ndarray, node: SceneNode) -> None:
        obj = node.data
        image = self._load_image(obj["path"])
        world_position = node.get_world_position()
        world_scale = node.get_world_scale()
        x = int(world_position[0])
        y = int(world_position[1])

        if "width" in obj and "height" in obj:
            target_width = max(1, int(float(obj["width"]) * world_scale[0]))
            target_height = max(1, int(float(obj["height"]) * world_scale[1]))
            image = cv2.resize(image, (target_width, target_height))
        elif world_scale != [1.0, 1.0]:
            target_width = max(1, int(image.shape[1] * world_scale[0]))
            target_height = max(1, int(image.shape[0] * world_scale[1]))
            image = cv2.resize(image, (target_width, target_height))

        img_h, img_w = image.shape[:2]
        x_end = min(x + img_w, self.width)
        y_end = min(y + img_h, self.height)

        if x >= self.width or y >= self.height or x_end <= 0 or y_end <= 0:
            return

        src_x = max(0, -x)
        src_y = max(0, -y)
        dst_x = max(0, x)
        dst_y = max(0, y)

        cropped = image[src_y : src_y + (y_end - dst_y), src_x : src_x + (x_end - dst_x)]
        frame[dst_y:y_end, dst_x:x_end] = cropped

    def _load_image(self, image_path: str) -> np.ndarray:
        path = Path(image_path)
        if not path.is_absolute() and self.assets_dir:
            path = self.assets_dir / path

        path = path.resolve()
        if path not in self._image_cache:
            image = cv2.imread(str(path))
            if image is None:
                raise FileNotFoundError(f"Unable to load image asset: {path}")
            self._image_cache[path] = image
        return self._image_cache[path]
