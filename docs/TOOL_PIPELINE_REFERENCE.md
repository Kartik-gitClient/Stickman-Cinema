# 🛠️ Stickman Cinema: Tool & Pipeline Reference Manual

> **Scope**: Technical reference for developers, automation agents, and CLI users working with the Stickman Cinema video production engine.

---

## 🏗️ 1. Architecture Overview

Stickman Cinema is an end-to-end pipeline designed to transform Midjourney/Flux 3x3 production grids into high-retention, YouTube-optimized 1080p anime stickman videos.

```
+-------------------------------------------------------------------------------+
|                             Stickman Cinema Engine                            |
+--------------------+---------------------+--------------------+---------------+
| 1. Grid Slicing    | 2. Voice & Subs     | 3. Kinetic Camera  | 4. HUD / Pop  |
| (slicer.py)        | (voice_engine.py)   | (motion_engine.py) | (hud_engine)  |
| - 1.5% margin crop | - Kokoro ONNX       | - Slow Zoom-in     | - Day/Time    |
| - Lanczos resize   | - 1:1 duration lock | - Dolly Slides     | - Resources   |
| - 1920x1080 PNG    | - Single-line .ASS  | - Selective Shake  | - Achievement |
+--------------------+---------------------+--------------------+---------------+
                                      |
                                      v
              +-----------------------------------------------+
              | 5. Parallel Clip Encoding (pipeline.py)       |
              | - ThreadPoolExecutor (3x parallel)            |
              | - '-preset veryfast' (1.55x real-time speed)  |
              | - 'adelay=200|200,apad' (0% audio drift)      |
              +-----------------------------------------------+
                                      |
                                      v
              +-----------------------------------------------+
              | 6. Instant Stream Copy Concatenation          |
              | - 'ffmpeg -f concat -c copy' (2 seconds)      |
              | - 100% mathematical zero-drift master video   |
              +-----------------------------------------------+
```

---

## ⚡ 2. Core Python API

### 2.1 Slicing 3x3 Grids (`stickman_cinema.slicer`)
```python
from stickman_cinema.slicer import slice_3x3_grid

# Slices a 5504x3072 upscaled 3x3 grid into 9 standalone 1920x1080 PNG frames
panels = slice_3x3_grid(
    grid_path="path/to/grid01.jpg",
    output_dir="path/to/output_panels",
    start_index=1,        # Generates s001.png to s009.png
    margin_pct=0.015,     # 1.5% border inset crop
    target_res=(1920, 1080)
)
```

### 2.2 In-Memory Voice Synthesis (`stickman_cinema.voice_engine`)
```python
from stickman_cinema.voice_engine import VoiceEngine

engine = VoiceEngine()
narration_lines = [
    "Day One. 08:14 AM on the upper research catwalk.",
    "Leo calibrated the seismic seismograph under rising alarms."
]

# Synthesizes per-shot audio clamped between 3.0s and 4.8s
results = engine.synthesize_lines(
    lines=narration_lines,
    output_dir="path/to/audio",
    voice="am_liam",
    speed=0.98,
    min_dur=3.0,
    max_dur=4.8
)
# results is a list of tuples: [(audio_path, effective_duration), ...]
```

### 2.3 Camera Motion Engine (`stickman_cinema.motion_engine`)
```python
from stickman_cinema.motion_engine import build_motion_filter

# Builds smooth pan/zoom or impact shake filter
motion_vf = build_motion_filter(
    shot_index=0,
    frames=120,          # dur * 30
    motion_type="auto",  # cycles slow zoom, slide, linear zoom, pull-out
    is_impact=False      # True activates seismic impact shake
)
```

### 2.4 Dynamic HUD Filter Builder (`stickman_cinema.hud_engine`)
```python
from stickman_cinema.hud_engine import build_hud_filter

hud_vf = build_hud_filter(
    day_text="DAY 01 | 08:14 AM",
    status_text="CIVILIZATION: 100% | ASTEROID DETECTED",
    subtitle_text="Leo calibrated the seismic seismograph.",
    status_color="0x00FFCC",
    achievement_text="ACHIEVEMENT: ARCHIVE DEFENSES ARMED"
)
```

---

## 🖥️ 3. CLI Usage

The tool includes a standalone command-line interface:

```bash
# Slice a 3x3 grid
stickman-cinema slice --grid ./grid1.jpg --out ./sliced --start-index 1

# Synthesize narration lines & subtitles
stickman-cinema voice --lines-file ./script.txt --out ./audio --sub ./subtitles.ass --voice am_liam --speed 0.98

# Check CLI version
stickman-cinema version
```

---

## 🎯 4. Quality Contracts & Mandates

1. **Duration Limit**: Every single shot must be between **3.0s and 4.8s** (Never > 5.0s).
2. **Resolution & Aspect**: Strict 16:9 Landscape (`1920x1080 @ 30fps`). Never vertical 9:16 or pillarboxed.
3. **Audio-Visual Lock**: Always embed the narration audio directly into the clip using `-af "adelay=200|200,apad"` to ensure zero temporal drift.
4. **Subtitles**: Strictly 1 short line (5–8 words) per shot burned directly at the bottom.
5. **Camera Movement**: Smooth cinematic slides and slow zooms on 95%+ of shots. Shakiness is strictly reserved for high-impact explosions, shockwaves, or titan breaches.
