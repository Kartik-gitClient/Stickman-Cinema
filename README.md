# 🎬 Stickman Cinema

> **Autonomous 2D Stickman Video Generation & Pipeline Engine**  
> An industrial-grade toolchain for building high-retention, YouTube-optimized 1080p anime stickman survival epics with 0% audio-visual drift, 5x parallel rendering, and cinematic 2.5D camera motion.

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-6.0%2B-green.svg)](https://ffmpeg.org)
[![TTS](https://img.shields.io/badge/TTS-Kokoro--ONNX-purple.svg)](https://github.com/hexgrad/kokoro)
[![Upscaler](https://img.shields.io/badge/Upscaler-Real--ESRGAN%20Vulkan-red.svg)](https://github.com/xinntao/Real-ESRGAN)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Key Features

* **⚡ 5x Real-Time Parallel Rendering**: Bakes audio, dynamic HUDs, 1-line subtitles, and 2.5D camera motion directly into individual shots using `ThreadPoolExecutor` and `-preset veryfast` (encoding 126 shots in ~90 seconds).
* **🎙️ Zero Temporal Drift Architecture**: Direct shot-by-shot narration embedding (`adelay=200|200,apad`) and duration locking (`max(3.0, min(dur+0.25, 4.8))`). Assembled into the final master in **2 seconds flat** via `ffmpeg -f concat -c copy` without re-encoding.
* **🗣️ Fast In-Memory Kokoro TTS**: Uses local ONNX models for crisp, punchy narration (`am_liam` @ 0.98 speed) with in-memory batch caching.
* **🎥 2.5D Kinetic Camera Engine**: Silky smooth slides (horizontal dolly pans) and slow zooms by default, with **selective seismic impact shakiness** strictly reserved for explosions, shockwaves, and breach beats.
* **🕹️ Dynamic HUD & Gold Achievement System**: Top-left Day/Time pill box (frame-accurate to spoken text), top-right Resource/Threat monitor, and timed gold achievement popups (`between(t, 0.6, 3.6)`).
* **🔪 Lanczos 3x3 Grid Slicer**: Automatically crops 1.5% border margins to strip black dividing borders and resamples cells to crisp 1920x1080 16:9 panels using Lanczos filtering.

---

## 🏗️ Architecture & Pipeline

```mermaid
flowchart TD
    A["Raw Midjourney/Flux 3x3 Production Grids (16:9)"] --> B["Real-ESRGAN Vulkan 2X Upscaling (5504x3072)"]
    B --> C["Lanczos 3x3 Slicer (1.5% Inset Crop ➔ 1920x1080 PNGs)"]
    D["Shot-by-Shot Narration Script (1 Line per Shot)"] --> E["Kokoro ONNX In-Memory Synthesizer ('am_liam')"]
    C --> F["Parallel Clip Renderer (3x Workers, -preset veryfast)"]
    E --> F
    F --> G["All-in-One MP4 Clips with Embedded Audio, Motion & HUD"]
    G --> H["Instant Stream Copy Assembly ('ffmpeg -f concat -c copy')"]
    H --> I["Master 1080p Video (0% Drift, 2 Seconds Assembly)"]
```

---

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Kartik-gitClient/Stickman-Cinema.git
cd Stickman-Cinema
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
pip install -e .
```

### 3. System Requirements
* **FFmpeg**: Must be installed and accessible in your system `PATH` (`ffmpeg` and `ffprobe`).
* **Real-ESRGAN Vulkan** (Optional for upscaling): Download portable executable from [Real-ESRGAN Releases](https://github.com/xinntao/Real-ESRGAN/releases) into `tools/realesrgan/`.
* **Kokoro ONNX Models**: Placed in `~/.cache/hyperframes/tts/models/` (`kokoro-v1.0.onnx`, `voices-v1.0.bin`).

---

## 💻 CLI Usage

The tool provides a unified command line interface (`stickman-cinema`):

### 1. Slice a 3x3 Production Grid
Extracts 9 standalone 1920x1080 panels with border margin removal:
```bash
stickman-cinema slice \
  --grid ./assets/grid01_2x.jpg \
  --out ./output/panels \
  --start-index 1 \
  --margin 0.015
```

### 2. Synthesize Shot Narration & Subtitles
Generates per-shot WAV audio clamped between 3.0s and 4.8s, plus single-line `.ass` subtitles:
```bash
stickman-cinema voice \
  --lines-file ./script.txt \
  --out ./output/audio \
  --sub ./output/subtitles.ass \
  --voice am_liam \
  --speed 0.98
```

### 3. Synthesize Hindi Voiceover (Sarvam AI)
Synthesizes Hindi narration sentences with Sarvam AI's Bulbul engine:
```bash
stickman-cinema hindi-voice \
  --lines-file ./hindi_script.txt \
  --out ./output/audio_hindi \
  --api-key "YOUR_SARVAM_API_KEY" \
  --speaker shubh
```

### 4. Clip Landscape Master into 9:16 Portrait Shorts (Reels / TikTok)
Automatically converts a 16:9 widescreen master into high-retention 9:16 vertical shorts with blurred ambient background, series header, part badge, and progress bar:
```bash
# Auto-slice an entire 8-10 minute episode into sequential ~50s Shorts:
stickman-cinema clip \
  --input ./renders/master_ep01.mp4 \
  --out-dir ./shorts_ep01 \
  --auto \
  --title "50 DAYS STICKMAN SURVIVAL" \
  --duration 50.0

# Or clip a single custom short:
stickman-cinema clip \
  --input ./renders/master_ep01.mp4 \
  --out ./shorts_ep01/short_part1.mp4 \
  --start 0.0 \
  --duration 45.0 \
  --title "50 DAYS STICKMAN SURVIVAL" \
  --part "PART 1"
```

### 5. Check CLI Version
```bash
stickman-cinema version
```

---

## 🐍 Programmatic Python API

You can import and use modular components directly in Python:

```python
from stickman_cinema.slicer import slice_3x3_grid
from stickman_cinema.voice_engine import VoiceEngine
from stickman_cinema.motion_engine import build_motion_filter
from stickman_cinema.hud_engine import build_hud_filter

# 1. Slice 3x3 Grid
panels = slice_3x3_grid("grid01_2x.jpg", "./panels", start_index=1)

# 2. Synthesize Per-Shot Narration
engine = VoiceEngine()
lines = [
    "Day One. 08:14 AM on the upper research catwalk.",
    "Leo calibrated the seismic seismograph under rising alarms."
]
audio_results = engine.synthesize_lines(lines, output_dir="./audio", voice="am_liam")

# 3. Build Motion & HUD Filters
frames = int(round(audio_results[0][1] * 30))
motion_vf = build_motion_filter(shot_index=0, frames=frames, motion_type="auto")
hud_vf = build_hud_filter(
    day_text="DAY 01 | 08:14 AM",
    status_text="CIVILIZATION: 100% | ASTEROID DETECTED",
    subtitle_text=lines[0],
    status_color="0x00FFCC",
    achievement_text="ACHIEVEMENT: SEISMIC REDOUBT SECURED"
)
```

---

## 📐 Golden Production Standards

* **Strict 16:9 Landscape**: `1920x1080 @ 30 FPS`. Never vertical (9:16) or letterboxed.
* **Rapid Cut Ceiling**: Every shot cuts between **3.0s and 4.8s** (NO SHOT may ever exceed 5.0s).
* **Single-Line Subtitles**: Strictly **5 to 8 words per cut**, centered at bottom (`MarginV=75`).
* **Camera Movement Standard**: Smooth cinematic slides (horizontal dolly pans) and slow zooms on 95%+ of shots. Shakiness is strictly reserved for high-impact explosions and titan breaches.
* **Problem ➔ Solution Engine**: Every episode must cycle through:
  $$\text{Problem/Crisis} \longrightarrow \text{Stakes \& Clock} \longrightarrow \text{Science Formula} \longrightarrow \text{Action Lock-in} \longrightarrow \text{Payoff}$$

---

## 📂 Project Organization

```text
Stickman-Cinema/
├── .gitignore                      # Strictly excludes all media, MP4s, WAVs, and projects
├── README.md                       # Complete documentation and examples
├── requirements.txt                # Python package dependencies
├── setup.py                        # Pip package & CLI entrypoints
├── docs/                           # WORKFLOW & TOOL DOCUMENTATION ONLY
│   ├── CINEMA_WORKFLOW_SPEC.md
│   └── TOOL_PIPELINE_REFERENCE.md
├── stickman_cinema/                # Python Core Engine
│   ├── __init__.py
│   ├── cli.py                      # Unified CLI entrypoint
│   ├── slicer.py                   # Lanczos 3x3 grid slicer
│   ├── voice_engine.py             # Kokoro TTS in-memory synthesizer
│   ├── motion_engine.py            # 2.5D camera motion & shake generator
│   ├── hud_engine.py               # Frame-accurate HUD & achievement builder
│   └── pipeline.py                 # Parallel clip renderer & stream copy concat
└── scripts/                        # Utility and example runners
    └── run_example.py
```

> **Note**: All series episodes, story scripts, audio WAVs, raw scenes, and rendered MP4 masters are organized under local `/projects/` directories (which are excluded from version control to keep this repository lightweight and focused strictly on the production tool).

---

## 📄 License

MIT License. Designed and maintained for autonomous 2D stickman cinema generation.
