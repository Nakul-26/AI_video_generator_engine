# AI Video Generator Engine

A small Python-based scene engine that renders JSON-defined scenes into an MP4 video using OpenCV.

## Implemented Features

- JSON-driven scene configuration
- Multi-scene video rendering pipeline
- MP4 export with configurable `fps`, `width`, and `height`
- Scene graph with parent-child node hierarchy
- Inherited transforms across nested nodes
- Timeline-based animation tracks with linear interpolation
- Built-in easing modes for smoother animation timing
- Per-track animation delay for simple staggered sequencing
- Per-track animation looping for continuous motion
- Supported animated properties:
  - `position`
  - `scale`
  - `rotation`
  - `opacity`
- Supported easing types:
  - `linear`
  - `ease_in`
  - `ease_out`
  - `ease_in_out`
- Supported renderable object types:
  - `text`
  - `circle`
  - `rectangle`
  - `image`
- Layer-based draw ordering
- Node visibility and opacity handling
- Rotation-aware compositing
- Relative asset loading from the `assets/` directory
- Image caching during rendering
- Basic validation for duplicate node names, missing nodes, and invalid animation ranges

## Project Structure

```text
ai_video_generator/
|-- assets/
|-- core/
|   |-- renderer.py
|   |-- scene_engine.py
|   |-- scene_graph.py
|   |-- scene_node.py
|   `-- timeline_engine.py
|-- output/
|-- scenes/
|   `-- example_scene.json
|-- scripts/
|   `-- generate_video.py
|-- requirements.txt
`-- README.md
```

## Requirements

- Python 3.10+
- `numpy`
- `opencv-python`

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the sample generator script:

```bash
python scripts/generate_video.py
```

This reads [scenes/example_scene.json](D:/nakul/ai_video_generator/scenes/example_scene.json) and writes the rendered output to `output/video.mp4`.

## Scene File Format

Top-level fields:

- `fps`: output frame rate
- `width`: output width in pixels
- `height`: output height in pixels
- `scenes`: list of scenes to render in sequence

Each scene supports:

- `duration`: scene length in seconds
- `objects`: top-level scene nodes
- `animations`: timeline animation tracks

### Object Fields

Common node fields:

- `name`: unique node name
- `type`: one of `text`, `circle`, `rectangle`, `image`
- `x`, `y`: local position
- `scale`: scalar or `[x, y]`
- `rotation`: degrees
- `opacity`: `0.0` to `1.0`
- `layer`: draw order
- `visible`: `true` or `false`
- `children`: nested child nodes

Type-specific fields:

- `text`: `value`, `font_scale`, `thickness`, `color`
- `circle`: `radius`, `thickness`, `color`
- `rectangle`: `width`, `height`, `thickness`, `color`
- `image`: `path`, optional `width`, optional `height`

### Animation Fields

Each animation track includes:

- `node`: target node name
- `property`: `position`, `scale`, `rotation`, or `opacity`
- `start_time`: animation start time in seconds
- `end_time`: animation end time in seconds
- `delay`: optional start offset in seconds, defaults to `0`
- `from`: starting value
- `to`: ending value
- `easing`: optional timing function, defaults to `linear`
- `loop`: optional boolean, defaults to `false`; when `true`, repeats indefinitely after the effective start time

## Example Capabilities

The sample scene currently demonstrates:

- group-level movement through a parent node
- text fade-in using eased opacity animation
- delayed circle position animation with easing
- delayed rectangle rotation animation with easing
- looped animation tracks for continuous motion
- multi-scene sequencing in one output video

## Current Limitations

Not implemented yet:

- audio support
- easing curves beyond the built-in presets
- camera system
- transitions between scenes
- CLI arguments for choosing input/output paths
- automated tests
- richer documentation and examples

## Notes

- Assets are resolved relative to the project `assets/` directory when image paths are not absolute.
- Rendering uses OpenCV's `mp4v` codec through `cv2.VideoWriter`.
