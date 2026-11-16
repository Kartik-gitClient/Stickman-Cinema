"""
Portrait Shorts & Reels Clipper Engine.
Transforms 16:9 landscape master videos into 9:16 vertical shorts for YouTube Shorts,
Instagram Reels, and TikTok with blurred ambient backgrounds, top hook headers,
part badges, and animated progress bars.
"""

import os
import subprocess
import math

DEFAULT_FONT = "C\\:/Windows/Fonts/arialbd.ttf"

def get_video_duration(video_path):
    if not os.path.exists(video_path):
        return 0.0
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        return float(res.stdout.strip())
    except:
        return 0.0

def sanitize_text(text):
    if not text:
        return ""
    return str(text).replace(":", r"\:").replace("%", r"\%").replace("'", "’")

def generate_portrait_short(
    input_video,
    output_video,
    start_time=0,
    duration=50.0,
    series_title="50 DAYS STICKMAN SURVIVAL",
    part_label="PART 1",
    cta_text="FULL 10-MIN EPISODE ON CHANNEL",
    font_path=DEFAULT_FONT
):
    """
    Renders a single 9:16 vertical short (1080x1920) from a section of a landscape master video.
    
    Layout:
      - Background: Blurred & darkened 1080x1920 copy of the video.
      - Center: 1080-wide landscape video with subtle border frame.
      - Top HUD: Part badge and series title.
      - Bottom HUD: Call-to-action text and progress bar.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_video)), exist_ok=True)
    
    clean_series = sanitize_text(series_title)
    clean_part = sanitize_text(part_label)
    clean_cta = sanitize_text(cta_text)
    
    filter_complex = (
        # 1. Split video into blurred background and crisp centered foreground
        f"[0:v]split=2[bg_in][fg_in];"
        f"[bg_in]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:5,eq=brightness=-0.25[bg];"
        f"[fg_in]scale=1080:-1[fg];"
        f"[bg][fg]overlay=0:(H-h)/2[base];"
        
        # 2. Top Header: Series Title & Part Pill Badge
        f"[base]drawtext=fontfile='{font_path}':text='[ {clean_part} ]':"
        f"fontcolor=0xFFD700:fontsize=38:x=(w-tw)/2:y=240:box=1:boxcolor=black@0.75:boxborderw=10,"
        f"drawtext=fontfile='{font_path}':text='{clean_series}':"
        f"fontcolor=white:fontsize=46:x=(w-tw)/2:y=320:box=1:boxcolor=black@0.75:boxborderw=10,"
        
        # 3. Bottom CTA & Safety Margin
        f"drawtext=fontfile='{font_path}':text='{clean_cta}':"
        f"fontcolor=white:fontsize=32:x=(w-tw)/2:y=h-260:box=1:boxcolor=black@0.75:boxborderw=10,"
        
        # 4. Animated Red/Yellow Progress Bar at Bottom (y=1910)
        f"drawbox=y=1910:x=0:w='1080*(t/{duration:.2f})':h=10:color=0xFFD700@0.9:t=fill"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_time),
        "-t", str(duration),
        "-i", input_video,
        "-filter_complex", filter_complex,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "192k", "-ar", "44100", "-ac", "2",
        output_video
    ]
    
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0 and os.path.exists(output_video) and os.path.getsize(output_video) > 50000:
        return output_video
    else:
        raise RuntimeError(f"FFmpeg Short generation failed:\n{res.stderr}")

def auto_slice_episode_into_shorts(
    input_video,
    output_dir,
    series_title="50 DAYS STICKMAN SURVIVAL",
    segment_length=50.0,
    start_part=1
):
    """
    Automatically splits an entire 8-10 minute landscape video into sequential 9:16 Shorts!
    """
    os.makedirs(output_dir, exist_ok=True)
    total_dur = get_video_duration(input_video)
    if total_dur <= 0:
        raise ValueError(f"Could not read duration of {input_video}")
        
    num_shorts = math.ceil(total_dur / segment_length)
    print(f"🎬 Clipping {total_dur:.1f}s episode into {num_shorts} portrait Shorts (~{segment_length:.0f}s each)...")
    
    generated = []
    current_time = 0.0
    part_num = start_part
    
    for i in range(num_shorts):
        dur = min(segment_length, total_dur - current_time)
        if dur < 10.0:  # Skip tiny leftovers under 10 seconds
            break
            
        part_tag = f"PART {part_num:02d}"
        out_path = os.path.join(output_dir, f"short_part_{part_num:02d}.mp4")
        
        print(f"   [Short {part_num:02d}/{num_shorts}] Generating {part_tag} ({current_time:.1f}s -> {current_time+dur:.1f}s)...")
        generate_portrait_short(
            input_video=input_video,
            output_video=out_path,
            start_time=current_time,
            duration=dur,
            series_title=series_title,
            part_label=part_tag,
            cta_text="WATCH FULL 10-MIN EPISODE ON CHANNEL"
        )
        
        generated.append(out_path)
        current_time += dur
        part_num += 1
        
    print(f"✓ All {len(generated)} portrait shorts generated successfully in {output_dir}!")
    return generated
