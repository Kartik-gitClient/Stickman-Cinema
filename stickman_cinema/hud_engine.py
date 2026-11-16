"""
Dynamic HUD & Achievement Overlay Engine.
Builds FFmpeg drawtext filter chains with strict ASCII/typographic sanitation.
"""

DEFAULT_FONT = "C\\:/Windows/Fonts/arialbd.ttf"

def sanitize_ffmpeg_text(text):
    """
    Sanitizes strings for FFmpeg drawtext:
    - Escapes colons and percent signs.
    - Replaces ASCII apostrophe with Unicode typographic apostrophe to prevent quote syntax breakage.
    """
    if not text:
        return ""
    return str(text).replace(":", r"\:").replace("%", r"\%").replace("'", "’")

def build_hud_filter(day_text, status_text, subtitle_text, status_color="0x00FFCC", achievement_text=None, font_path=DEFAULT_FONT):
    """
    Builds the complete drawtext filter chain for HUD, subtitle, and achievement popup.
    
    Returns:
        str: FFmpeg filter chain fragment.
    """
    clean_day = sanitize_ffmpeg_text(day_text)
    clean_status = sanitize_ffmpeg_text(status_text)
    clean_sub = sanitize_ffmpeg_text(subtitle_text)
    
    filters = []
    
    # Top-Left Day/Time Box
    if clean_day:
        filters.append(
            f"drawtext=fontfile='{font_path}':text='{clean_day}':fontcolor=white:fontsize=24:"
            f"x=45:y=35:box=1:boxcolor=black@0.65:boxborderw=8"
        )
        
    # Top-Right Status / Resource Box
    if clean_status:
        filters.append(
            f"drawtext=fontfile='{font_path}':text='{clean_status}':fontcolor={status_color}:fontsize=22:"
            f"x=w-tw-45:y=35:box=1:boxcolor=black@0.65:boxborderw=8"
        )
        
    # Bottom Single-Line Subtitle
    if clean_sub:
        filters.append(
            f"drawtext=fontfile='{font_path}':text='{clean_sub}':fontcolor=white:fontsize=28:"
            f"x=(w-tw)/2:y=h-95:box=1:boxcolor=black@0.65:boxborderw=8"
        )
        
    # Gold Achievement Popup (right side, below HUD)
    if achievement_text:
        clean_ach = sanitize_ffmpeg_text(achievement_text)
        filters.append(
            f"drawtext=fontfile='{font_path}':text='* {clean_ach} *':fontcolor=0xFFD700:fontsize=22:"
            f"x=w-tw-45:y=80:box=1:boxcolor=black@0.85:boxborderw=8:enable='between(t,0.6,3.6)'"
        )
        
    return ",".join(filters)
