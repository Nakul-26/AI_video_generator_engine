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
            node
            for node in nodes
            if node.visible and node.node_type is not None and node.get_world_opacity() > 0
        ]
        sorted_nodes = sorted(drawable_nodes, key=lambda node: node.layer)

        for node in sorted_nodes:
            obj_type = node.node_type

            if obj_type == "text":
                overlay, mask = self._draw_text(node)
            elif obj_type == "circle":
                overlay, mask = self._draw_circle(node)
            elif obj_type == "rectangle":
                overlay, mask = self._draw_rectangle(node)
            elif obj_type == "image":
                overlay, mask = self._draw_image(node)
            else:
                raise ValueError(f"Unsupported object type: {obj_type}")

            self._composite_node(frame, overlay, mask, node)

        return frame

    def _draw_text(self, node: SceneNode) -> tuple[np.ndarray, np.ndarray]:
        overlay = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        mask = np.zeros((self.height, self.width), dtype=np.uint8)
        obj = node.data
        color = tuple(obj.get("color", [255, 255, 255]))
        world_position = node.get_world_position()
        world_scale = node.get_world_scale()
        scale = float(obj.get("font_scale", 1.0)) * world_scale[0]
        thickness = max(1, int(obj.get("thickness", 2)))
        cv2.putText(
            overlay,
            obj["value"],
            (int(world_position[0]), int(world_position[1])),
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            color,
            thickness,
            cv2.LINE_AA,
        )
        cv2.putText(
            mask,
            obj["value"],
            (int(world_position[0]), int(world_position[1])),
            cv2.FONT_HERSHEY_SIMPLEX,
            scale,
            255,
            thickness,
            cv2.LINE_AA,
        )
        return overlay, mask

    def _draw_circle(self, node: SceneNode) -> tuple[np.ndarray, np.ndarray]:
        overlay = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        mask = np.zeros((self.height, self.width), dtype=np.uint8)
        obj = node.data
        color = tuple(obj.get("color", [0, 255, 0]))
        thickness = int(obj.get("thickness", -1))
        world_position = node.get_world_position()
        world_scale = node.get_world_scale()
        radius = max(1, int(float(obj["radius"]) * world_scale[0]))
        cv2.circle(
            overlay,
            (int(world_position[0]), int(world_position[1])),
            radius,
            color,
            thickness,
        )
        cv2.circle(
            mask,
            (int(world_position[0]), int(world_position[1])),
            radius,
            255,
            thickness,
        )
        return overlay, mask

    def _draw_rectangle(self, node: SceneNode) -> tuple[np.ndarray, np.ndarray]:
        overlay = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        mask = np.zeros((self.height, self.width), dtype=np.uint8)
        obj = node.data
        color = tuple(obj.get("color", [255, 0, 0]))
        thickness = int(obj.get("thickness", -1))
        world_position = node.get_world_position()
        world_scale = node.get_world_scale()
        x = int(world_position[0])
        y = int(world_position[1])
        width = max(1, int(float(obj["width"]) * world_scale[0]))
        height = max(1, int(float(obj["height"]) * world_scale[1]))
        cv2.rectangle(overlay, (x, y), (x + width, y + height), color, thickness)
        cv2.rectangle(mask, (x, y), (x + width, y + height), 255, thickness)
        return overlay, mask

    def _draw_image(self, node: SceneNode) -> tuple[np.ndarray, np.ndarray]:
        overlay = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        mask = np.zeros((self.height, self.width), dtype=np.uint8)
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
            return overlay, mask

        src_x = max(0, -x)
        src_y = max(0, -y)
        dst_x = max(0, x)
        dst_y = max(0, y)

        cropped = image[src_y : src_y + (y_end - dst_y), src_x : src_x + (x_end - dst_x)]
        overlay[dst_y:y_end, dst_x:x_end] = cropped
        mask[dst_y:y_end, dst_x:x_end] = 255
        return overlay, mask

    def _composite_node(
        self,
        frame: np.ndarray,
        overlay: np.ndarray,
        mask: np.ndarray,
        node: SceneNode,
    ) -> None:
        rotated_overlay, rotated_mask = self._apply_rotation(overlay, mask, node)
        alpha = (rotated_mask.astype(np.float32) / 255.0) * node.get_world_opacity()
        if not np.any(alpha):
            return

        alpha = alpha[..., np.newaxis]
        blended = (
            frame.astype(np.float32) * (1.0 - alpha)
            + rotated_overlay.astype(np.float32) * alpha
        )
        frame[:] = blended.astype(np.uint8)

    def _apply_rotation(
        self,
        overlay: np.ndarray,
        mask: np.ndarray,
        node: SceneNode,
    ) -> tuple[np.ndarray, np.ndarray]:
        rotation = node.get_world_rotation()
        if rotation == 0:
            return overlay, mask

        center = self._rotation_center(node)
        matrix = cv2.getRotationMatrix2D(center, rotation, 1.0)
        rotated_overlay = cv2.warpAffine(
            overlay,
            matrix,
            (self.width, self.height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0),
        )
        rotated_mask = cv2.warpAffine(
            mask,
            matrix,
            (self.width, self.height),
            flags=cv2.INTER_LINEAR,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=0,
        )
        return rotated_overlay, rotated_mask

    def _rotation_center(self, node: SceneNode) -> tuple[float, float]:
        world_position = node.get_world_position()
        world_scale = node.get_world_scale()
        obj = node.data

        if node.node_type == "rectangle":
            width = float(obj["width"]) * world_scale[0]
            height = float(obj["height"]) * world_scale[1]
            return (world_position[0] + width / 2.0, world_position[1] + height / 2.0)

        if node.node_type == "image":
            if "width" in obj and "height" in obj:
                width = float(obj["width"]) * world_scale[0]
                height = float(obj["height"]) * world_scale[1]
            else:
                image = self._load_image(obj["path"])
                width = image.shape[1] * world_scale[0]
                height = image.shape[0] * world_scale[1]
            return (world_position[0] + width / 2.0, world_position[1] + height / 2.0)

        return (world_position[0], world_position[1])

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
