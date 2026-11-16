"""
Stickman Cinema Command Line Interface (CLI).
Unified entrypoint for slicing, voice synthesis, motion generation, and master rendering.
"""

import argparse
import sys
import os
import glob
from .slicer import slice_3x3_grid
from .voice_engine import VoiceEngine
from .pipeline import render_clip, assemble_master_video
import concurrent.futures

def cmd_slice(args):
    """Slices a 3x3 grid into 9 individual 1080p frames."""
    print(f"🔪 Slicing grid: {args.grid}")
    panels = slice_3x3_grid(
        grid_path=args.grid,
        output_dir=args.out,
        start_index=args.start_index,
        margin_pct=args.margin
    )
    print(f"✓ Generated {len(panels)} panels in {args.out}")

def cmd_voice(args):
    """Synthesizes narration lines into per-shot audio wavs and subtitles."""
    if not os.path.exists(args.lines_file):
        print(f"Error: Script file not found: {args.lines_file}", file=sys.stderr)
        sys.exit(1)
        
    with open(args.lines_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        
    print(f"🎙️ Synthesizing {len(lines)} narration lines with voice '{args.voice}'...")
    engine = VoiceEngine(model_path=args.model, voices_path=args.voices)
    results = engine.synthesize_lines(lines, output_dir=args.out, voice=args.voice, speed=args.speed)
    
    durations = [r[1] for r in results]
    total_sec = sum(durations)
    print(f"✓ Audio ready! Total runtime: {total_sec:.1f}s ({total_sec/60:.2f} mins)")
    
    if args.sub:
        engine.generate_single_line_ass(lines, durations, output_file=args.sub)
        print(f"✓ Subtitles written to: {args.sub}")

def main():
    parser = argparse.ArgumentParser(
        prog="stickman-cinema",
        description="Autonomous 2D Stickman Video Generation & Pipeline Engine"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Slice command
    slice_parser = subparsers.add_parser("slice", help="Slice 3x3 grid into 9 panels")
    slice_parser.add_argument("--grid", required=True, help="Path to 3x3 grid image")
    slice_parser.add_argument("--out", required=True, help="Output directory for panels")
    slice_parser.add_argument("--start-index", type=int, default=1, help="Start panel index (e.g. 1)")
    slice_parser.add_argument("--margin", type=float, default=0.015, help="Border margin crop percentage")

    # Voice command
    voice_parser = subparsers.add_parser("voice", help="Synthesize per-shot narration audio")
    voice_parser.add_argument("--lines-file", required=True, help="Text file with 1 line per shot")
    voice_parser.add_argument("--out", required=True, help="Output directory for audio wavs")
    voice_parser.add_argument("--sub", help="Optional path to output .ass subtitle file")
    voice_parser.add_argument("--voice", default="am_liam", help="Kokoro voice name (default: am_liam)")
    voice_parser.add_argument("--speed", type=float, default=0.98, help="Speech speed multiplier (default: 0.98)")
    voice_parser.add_argument("--model", help="Path to kokoro-v1.0.onnx")
    voice_parser.add_argument("--voices", help="Path to voices-v1.0.bin")

    # Version
    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()
    if args.command == "slice":
        cmd_slice(args)
    elif args.command == "voice":
        cmd_voice(args)
    elif args.command == "version":
        from . import __version__
        print(f"Stickman Cinema v{__version__}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
