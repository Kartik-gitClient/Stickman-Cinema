"""
Lanczos 3x3 Grid Slicer Module.
Extracts 9 individual 1080p landscape panels from a 3x3 production grid.
"""

import os
from PIL import Image

def slice_3x3_grid(grid_path, output_dir, start_index=1, margin_pct=0.015, target_res=(1920, 1080)):
    """
    Slices a 3x3 grid image into 9 sequential 16:9 frames.
    
    Args:
        grid_path (str): Path to input 3x3 grid image (preferably upscaled 5504x3072).
        output_dir (str): Directory where sliced panels are written.
        start_index (int): 1-based start index for shot filenames (e.g. 1 -> s001.png).
        margin_pct (float): Fraction to crop from inner edges to remove grid borders.
        target_res (tuple): Output (width, height) resolution, default (1920, 1080).
        
    Returns:
        list[str]: Absolute paths to the 9 generated PNG files.
    """
    os.makedirs(output_dir, exist_ok=True)
    im = Image.open(grid_path)
    w, h = im.size
    
    col_w = w / 3.0
    row_h = h / 3.0
    
    outputs = []
    idx = start_index
    
    for r in range(3):
        for c in range(3):
            left = c * col_w
            top = r * row_h
            right = (c + 1) * col_w
            bottom = (r + 1) * row_h
            
            # Apply border inset crop
            crop_w = right - left
            crop_h = bottom - top
            inset_x = crop_w * margin_pct
            inset_y = crop_h * margin_pct
            
            crop_box = (
                int(left + inset_x),
                int(top + inset_y),
                int(right - inset_x),
                int(bottom - inset_y)
            )
            
            panel = im.crop(crop_box)
            panel_resized = panel.resize(target_res, Image.Resampling.LANCZOS)
            
            out_name = f"s{idx:03d}.png"
            out_path = os.path.join(output_dir, out_name)
            panel_resized.save(out_path, format="PNG")
            outputs.append(out_path)
            idx += 1
            
    return outputs
