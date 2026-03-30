from __future__ import annotations

import unittest

from core.scene_graph import SceneGraph
from core.scene_node import SceneNode
from core.timeline_engine import TimelineEngine


class TimelineLoopTests(unittest.TestCase):
    def _build_graph(self) -> SceneGraph:
        graph = SceneGraph()
        graph.add_node(SceneNode("fan", {"type": "rectangle", "rotation": 0}))
        graph.add_node(SceneNode("orb", {"type": "circle", "x": 0, "y": 90}))
        return graph

    def test_loop_keeps_repeating_after_original_end_time(self) -> None:
        graph = self._build_graph()
        timeline = TimelineEngine(
            graph,
            [
                {
                    "node": "fan",
                    "property": "rotation",
                    "start_time": 0,
                    "end_time": 4,
                    "from": 0,
                    "to": 360,
                    "loop": True,
                    "easing": "linear",
                }
            ],
        )

        timeline.evaluate(5.5)

        self.assertEqual(graph.find_node("fan").rotation, 135.0)

    def test_loop_respects_delay_before_first_cycle(self) -> None:
        graph = self._build_graph()
        timeline = TimelineEngine(
            graph,
            [
                {
                    "node": "orb",
                    "property": "position",
                    "start_time": 0,
                    "end_time": 2,
                    "delay": 1.0,
                    "from": [0, 90],
                    "to": [240, 90],
                    "loop": True,
                }
            ],
        )

        timeline.evaluate(0.75)
        self.assertEqual(graph.find_node("orb").position, [0.0, 90.0])

        timeline.evaluate(3.5)
        self.assertEqual(graph.find_node("orb").position, [60.0, 90.0])

    def test_non_looping_tracks_still_end_on_final_value(self) -> None:
        graph = self._build_graph()
        timeline = TimelineEngine(
            graph,
            [
                {
                    "node": "fan",
                    "property": "rotation",
                    "start_time": 0,
                    "end_time": 2,
                    "from": 0,
                    "to": 180,
                }
            ],
        )

        timeline.evaluate(3.0)

        self.assertEqual(graph.find_node("fan").rotation, 180.0)

    def test_repeat_replays_for_a_fixed_number_of_cycles(self) -> None:
        graph = self._build_graph()
        timeline = TimelineEngine(
            graph,
            [
                {
                    "node": "fan",
                    "property": "rotation",
                    "start_time": 0,
                    "end_time": 1,
                    "from": 0,
                    "to": 90,
                    "repeat": 3,
                }
            ],
        )

        timeline.evaluate(1.5)
        self.assertEqual(graph.find_node("fan").rotation, 45.0)

        timeline.evaluate(3.0)
        self.assertEqual(graph.find_node("fan").rotation, 90.0)

    def test_repeat_respects_delay_before_first_cycle(self) -> None:
        graph = self._build_graph()
        timeline = TimelineEngine(
            graph,
            [
                {
                    "node": "orb",
                    "property": "position",
                    "start_time": 0,
                    "end_time": 2,
                    "delay": 1.0,
                    "from": [0, 90],
                    "to": [240, 90],
                    "repeat": 2,
                }
            ],
        )

        timeline.evaluate(0.75)
        self.assertEqual(graph.find_node("orb").position, [0.0, 90.0])

        timeline.evaluate(2.5)
        self.assertEqual(graph.find_node("orb").position, [180.0, 90.0])

        timeline.evaluate(5.0)
        self.assertEqual(graph.find_node("orb").position, [240.0, 90.0])

    def test_repeat_must_be_positive(self) -> None:
        graph = self._build_graph()

        with self.assertRaisesRegex(ValueError, "repeat >= 1"):
            TimelineEngine(
                graph,
                [
                    {
                        "node": "fan",
                        "property": "rotation",
                        "start_time": 0,
                        "end_time": 1,
                        "from": 0,
                        "to": 90,
                        "repeat": 0,
                    }
                ],
            )


if __name__ == "__main__":
    unittest.main()
