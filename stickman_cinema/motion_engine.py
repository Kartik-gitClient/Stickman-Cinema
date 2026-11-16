"""
2.5D Camera Motion & Kinetic Effects Engine.
Produces smooth cinematic slides, slow zooms, and selective impact shakiness.
"""

def build_motion_filter(shot_index, frames, motion_type="auto", is_impact=False):
    """
    Builds FFmpeg zoompan filter string for 1080p 30fps video.
    
    Args:
        shot_index (int): 0-based shot index (used to cycle auto motions).
        frames (int): Total frames in the shot (dur * 30).
        motion_type (str): 'auto', 'zoom_in', 'slide_right', 'zoom_out', 'impact_shake'.
        is_impact (bool): If True, overrides to high-impact seismic camera vibration.
        
    Returns:
        str: FFmpeg filter string for scaling and zoompan motion.
    """
    if is_impact or motion_type == "impact_shake":
        # Subtle, high-frequency camera vibration for explosions / impacts
        return (
            f"scale=2112:1188,zoompan=z=1.08:"
            f"x='(iw-iw/zoom)/2+sin(on*2.5)*7':y='(ih-ih/zoom)/2+cos(on*3.1)*5':"
            f"d={frames}:s=1920x1080:fps=30"
        )

    mode = shot_index % 4 if motion_type == "auto" else motion_type
    
    if mode == 0 or mode == "zoom_in_slow":
        # Smooth Slow Zoom-In (Center focus)
        return f"scale=2112:1188,zoompan=z='min(zoom+0.0008,1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps=30"
    elif mode == 1 or mode == "slide_right":
        # Smooth Horizontal Slide / Dolly Pan
        return f"scale=2112:1188,zoompan=z=1.05:x='min((iw-iw/zoom)*(on/({frames})),iw-iw/zoom)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps=30"
    elif mode == 2 or mode == "zoom_in_dynamic":
        # Smooth Linear Zoom-In
        return f"scale=2112:1188,zoompan=z='min(1.0+0.0015*on,1.10)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps=30"
    else:
        # Smooth Slow Pull-Out / Zoom-Out
        return f"scale=2112:1188,zoompan=z='max(1.08-0.0008*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1920x1080:fps=30"
