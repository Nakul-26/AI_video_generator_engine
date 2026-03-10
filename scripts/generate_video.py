from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.scene_engine import SceneEngine


def main() -> None:
    scene_file = PROJECT_ROOT / "scenes" / "example_scene.json"
    output_file = PROJECT_ROOT / "output" / "video.mp4"

    engine = SceneEngine(scene_file)
    generated_file = engine.generate_video(output_file)
    print(f"Video generated: {generated_file}")


if __name__ == "__main__":
    main()
