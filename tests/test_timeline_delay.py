from __future__ import annotations

import unittest

from core.scene_graph import SceneGraph
from core.scene_node import SceneNode
from core.timeline_engine import TimelineEngine


class TimelineDelayTests(unittest.TestCase):
    def _build_graph(self) -> SceneGraph:
        graph = SceneGraph()
        graph.add_node(SceneNode("title", {"type": "text", "opacity": 0}))
        graph.add_node(SceneNode("circle", {"type": "circle", "x": 0, "y": 90}))
        return graph

    def test_delay_keeps_animation_idle_until_effective_start(self) -> None:
        graph = self._build_graph()
        timeline = TimelineEngine(
            graph,
            [
                {
                    "node": "title",
                    "property": "opacity",
                    "start_time": 0,
                    "end_time": 1,
                    "delay": 0.5,
                    "from": 0,
                    "to": 1,
                }
            ],
        )

        timeline.evaluate(0.49)

        self.assertEqual(graph.find_node("title").opacity, 0.0)

    def test_delay_starts_interpolation_after_effective_start(self) -> None:
        graph = self._build_graph()
        timeline = TimelineEngine(
            graph,
            [
                {
                    "node": "circle",
                    "property": "position",
                    "start_time": 0,
                    "end_time": 2,
                    "delay": 1.0,
                    "from": [0, 90],
                    "to": [240, 90],
                }
            ],
        )

        timeline.evaluate(1.5)

        self.assertEqual(graph.find_node("circle").position, [60.0, 90.0])

    def test_delay_reaches_end_value_after_effective_end(self) -> None:
        graph = self._build_graph()
        timeline = TimelineEngine(
            graph,
            [
                {
                    "node": "title",
                    "property": "opacity",
                    "start_time": 0,
                    "end_time": 1.5,
                    "delay": 0.25,
                    "from": 0,
                    "to": 1,
                }
            ],
        )

        timeline.evaluate(1.75)

        self.assertEqual(graph.find_node("title").opacity, 1.0)

    def test_negative_delay_is_rejected(self) -> None:
        graph = self._build_graph()

        with self.assertRaisesRegex(ValueError, "negative delay"):
            TimelineEngine(
                graph,
                [
                    {
                        "node": "title",
                        "property": "opacity",
                        "start_time": 0,
                        "end_time": 1,
                        "delay": -0.1,
                        "from": 0,
                        "to": 1,
                    }
                ],
            )


if __name__ == "__main__":
    unittest.main()
