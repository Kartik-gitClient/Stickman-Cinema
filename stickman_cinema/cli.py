"""
Stickman Cinema Command Line Interface (CLI).
Unified entrypoint for slicing, voice synthesis, Sarvam AI Hindi TTS,
Soundza SFX search & downloads, portrait shorts clipping, and pipeline execution.
"""

import argparse
import sys
import os
import glob
import json
from .slicer import slice_3x3_grid
from .voice_engine import VoiceEngine
from .sarvam_tts import SarvamVoiceEngine
from .soundza_sfx import SoundzaClient
from .shorts_clipper import generate_portrait_short, auto_slice_episode_into_shorts

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
    """Synthesizes English narration lines into per-shot audio wavs and subtitles."""
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

def cmd_hindi_voice(args):
    """Synthesizes Hindi narration lines using Sarvam AI API."""
    if not os.path.exists(args.lines_file):
        print(f"Error: Script file not found: {args.lines_file}", file=sys.stderr)
        sys.exit(1)
        
    with open(args.lines_file, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        
    engine = SarvamVoiceEngine(
        api_key=args.api_key,
        speaker=args.speaker,
        model=args.model,
        pace=args.pace
    )
    results = engine.synthesize_batch(lines, output_dir=args.out)
    print(f"✓ Hindi voice synthesis complete! {len(results)} files generated in {args.out}")

def cmd_clip(args):
    """Generates 9:16 portrait shorts from a 16:9 landscape video."""
    if args.auto:
        auto_slice_episode_into_shorts(
            input_video=args.input,
            output_dir=args.out_dir,
            series_title=args.title,
            segment_length=args.duration,
            start_part=args.start_part
        )
    else:
        out_file = args.out or os.path.join(args.out_dir or ".", "short.mp4")
        generate_portrait_short(
            input_video=args.input,
            output_video=out_file,
            start_time=args.start or 0.0,
            duration=args.duration or 50.0,
            series_title=args.title,
            part_label=args.part or "PART 1",
            cta_text=args.cta or "WATCH FULL 10-MIN EPISODE ON CHANNEL"
        )
        print(f"✓ Portrait short generated: {out_file}")

def cmd_sfx(args):
    """Soundza sound effects search and download."""
    client = SoundzaClient(api_key=args.api_key)
    if args.sfx_action == "search":
        print(f"🔍 Searching Soundza for: '{args.query}'...")
        sounds = client.search(args.query, per_page=args.limit)
        print(f"Found {len(sounds)} sounds:")
        for s in sounds:
            print(f"  • [{s.get('id')}] {s.get('title')} ({s.get('duration')}s) - {s.get('url')}")
    elif args.sfx_action == "download":
        out = args.out or f"{args.id}.wav"
        print(f"⬇️ Downloading Soundza ID: {args.id} -> {out}...")
        client.download_sound(args.id, out)
        print(f"✓ Saved to {out}")
    elif args.sfx_action == "kit":
        out_dir = args.out or "./assets/sfx"
        client.download_curated_survival_kit(out_dir)

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

    # Voice command (Kokoro)
    voice_parser = subparsers.add_parser("voice", help="Synthesize per-shot narration audio with Kokoro")
    voice_parser.add_argument("--lines-file", required=True, help="Text file with 1 line per shot")
    voice_parser.add_argument("--out", required=True, help="Output directory for audio wavs")
    voice_parser.add_argument("--sub", help="Optional path to output .ass subtitle file")
    voice_parser.add_argument("--voice", default="am_liam", help="Kokoro voice name (default: am_liam)")
    voice_parser.add_argument("--speed", type=float, default=0.98, help="Speech speed multiplier (default: 0.98)")
    voice_parser.add_argument("--model", help="Path to kokoro-v1.0.onnx")
    voice_parser.add_argument("--voices", help="Path to voices-v1.0.bin")

    # Hindi Voice command (Sarvam AI)
    hindi_parser = subparsers.add_parser("hindi-voice", help="Synthesize Hindi narration via Sarvam AI API")
    hindi_parser.add_argument("--lines-file", required=True, help="Text file with 1 Hindi sentence per line")
    hindi_parser.add_argument("--out", required=True, help="Output directory for audio wavs")
    hindi_parser.add_argument("--api-key", help="Sarvam AI API Key (or set SARVAM_API_KEY env var)")
    hindi_parser.add_argument("--speaker", default="shubh", help="Speaker voice ('shubh', 'arvind', 'amol', 'meera')")
    hindi_parser.add_argument("--model", default="bulbul:v1", help="Sarvam model ('bulbul:v1' or 'bulbul:v2')")
    hindi_parser.add_argument("--pace", type=float, default=1.0, help="Pace multiplier (default: 1.0)")

    # Clip command (Portrait Shorts / Reels)
    clip_parser = subparsers.add_parser("clip", help="Clip 16:9 landscape master into 9:16 portrait shorts")
    clip_parser.add_argument("--input", required=True, help="Path to input 16:9 master video")
    clip_parser.add_argument("--out", help="Output .mp4 path for a single short")
    clip_parser.add_argument("--out-dir", default="./shorts", help="Directory for auto-sliced shorts")
    clip_parser.add_argument("--auto", action="store_true", help="Auto-slice entire episode into sequential ~50s shorts")
    clip_parser.add_argument("--start", type=float, default=0.0, help="Start time in seconds for single short")
    clip_parser.add_argument("--duration", type=float, default=50.0, help="Duration in seconds (default: 50.0s)")
    clip_parser.add_argument("--title", default="50 DAYS STICKMAN SURVIVAL", help="Header series title")
    clip_parser.add_argument("--part", default="PART 1", help="Part label badge (e.g. 'PART 1')")
    clip_parser.add_argument("--start-part", type=int, default=1, help="Starting part number for auto-slice")
    clip_parser.add_argument("--cta", default="WATCH FULL 10-MIN EPISODE ON CHANNEL", help="Bottom CTA text")

    # SFX command (Soundza)
    sfx_parser = subparsers.add_parser("sfx", help="Search & download SFX from Soundza API")
    sfx_sub = sfx_parser.add_subparsers(dest="sfx_action", help="SFX action")
    
    # sfx search
    sfx_search = sfx_sub.add_parser("search", help="Search sounds")
    sfx_search.add_argument("--query", "-q", required=True, help="Search terms (e.g. 'whoosh', 'metal clang')")
    sfx_search.add_argument("--limit", type=int, default=5, help="Number of results")
    sfx_search.add_argument("--api-key", help="Soundza API Key (or set SOUNDZA_API_KEY env var)")

    # sfx download
    sfx_dl = sfx_sub.add_parser("download", help="Download sound by ID")
    sfx_dl.add_argument("--id", required=True, help="Soundza sound ID")
    sfx_dl.add_argument("--out", required=True, help="Output file path (.wav)")
    sfx_dl.add_argument("--api-key", help="Soundza API Key (or set SOUNDZA_API_KEY env var)")

    # sfx kit
    sfx_kit = sfx_sub.add_parser("kit", help="Download curated survival SFX kit")
    sfx_kit.add_argument("--out", default="./assets/sfx", help="Output directory")
    sfx_kit.add_argument("--api-key", help="Soundza API Key (or set SOUNDZA_API_KEY env var)")

    # Version
    subparsers.add_parser("version", help="Show version")

    args = parser.parse_args()
    if args.command == "slice":
        cmd_slice(args)
    elif args.command == "voice":
        cmd_voice(args)
    elif args.command == "hindi-voice":
        cmd_hindi_voice(args)
    elif args.command == "clip":
        cmd_clip(args)
    elif args.command == "sfx":
        cmd_sfx(args)
    elif args.command == "version":
        from . import __version__
        print(f"Stickman Cinema v{__version__}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
