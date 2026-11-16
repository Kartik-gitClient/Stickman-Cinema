"""
Stickman Cinema - Autonomous 2D Stickman Video Generation & Pipeline Engine.
Fast 5x Parallel Rendering, 0% Audio-Visual Drift, 2.5D Smooth Motion,
Dynamic HUD, Sarvam AI Hindi Voice Engine, & 9:16 Portrait Shorts Clipper.
"""

__version__ = "1.1.0"
__author__ = "Stickman Cinema Team"

from .slicer import slice_3x3_grid
from .voice_engine import VoiceEngine
from .sarvam_tts import SarvamVoiceEngine
from .motion_engine import build_motion_filter
from .hud_engine import build_hud_filter
from .pipeline import render_clip, assemble_master_video
from .shorts_clipper import generate_portrait_short, auto_slice_episode_into_shorts
