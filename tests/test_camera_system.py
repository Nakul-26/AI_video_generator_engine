from __future__ import annotations

import unittest

from core.renderer import Renderer
from core.scene_graph import SceneGraph
from core.scene_node import SceneNode
from core.timeline_engine import TimelineEngine


class CameraSystemTests(unittest.TestCase):
    def test_camera_zoom_is_animatable(self) -> None:
        graph = SceneGraph()
        graph.add_node(SceneNode("camera", {"type": "camera", "zoom": 1.0}))

        timeline = TimelineEngine(
            graph,
            [
                {
                    "node": "camera",
                    "property": "zoom",
                    "start_time": 0,
                    "end_time": 2,
                    "from": 1,
                    "to": 2,
                }
            ],
        )

        timeline.evaluate(1.0)

        self.assertEqual(graph.find_node("camera").zoom, 1.5)

    def test_renderer_applies_camera_position_and_zoom(self) -> None:
        renderer = Renderer(width=64, height=64)
        graph = SceneGraph()
        camera = SceneNode("camera", {"type": "camera", "x": 5, "y": 5, "zoom": 2.0})
        box = SceneNode(
            "box",
            {
                "type": "rectangle",
                "x": 10,
                "y": 10,
                "width": 4,
                "height": 4,
                "color": [255, 0, 0],
            },
        )
        graph.add_node(camera)
        graph.add_node(box)

        frame = renderer.render_scene(graph.traverse(), camera=camera)

        self.assertTrue((frame[10, 10] == [255, 0, 0]).all())
        self.assertTrue((frame[17, 17] == [255, 0, 0]).all())
        self.assertTrue((frame[9, 9] == [0, 0, 0]).all())

    def test_renderer_uses_default_camera_when_none_is_provided(self) -> None:
        renderer = Renderer(width=32, height=32)
        graph = SceneGraph()
        box = SceneNode(
            "box",
            {
                "type": "rectangle",
                "x": 6,
                "y": 7,
                "width": 3,
                "height": 3,
                "color": [255, 0, 0],
            },
        )
        graph.add_node(box)

        frame = renderer.render_scene(graph.traverse())

        self.assertTrue((frame[7, 6] == [255, 0, 0]).all())


if __name__ == "__main__":
    unittest.main()
