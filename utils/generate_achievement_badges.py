#!/usr/bin/env python3
"""
Script to generate achievement badge PNGs.
Creates temporary composite SVGs (badge + icon) and exports them to PNG.
Composite SVGs are not saved, only used during generation.
"""

import os
import tempfile
from xml.etree import ElementTree as ET

# Achievement types
ACHIEVEMENTS = [
    "molecule_discover",
    "reaction_discover", 
    "reactionist",
    "molecule_maker",
    "level_crusher"
]

LEVELS = ["bronze", "silver", "gold"]
SVG_DIR = "img/achievements/svg"
OUTPUT_DIR = "img/achievements"

# Badge border colors to use for icons (for better contrast against the shiny background)
LEVEL_COLORS = {
    "bronze": "#5a3a1a",
    "silver": "#606060",
    "gold": "#8b6508"
}

def create_composite_svg(achievement_key, level):
    """Create a temporary composite SVG by embedding icon into badge."""
    
    # Load badge SVG
    badge_path = f"{SVG_DIR}/badge_{level}.svg"
    badge_tree = ET.parse(badge_path)
    badge_root = badge_tree.getroot()
    
    # Load icon SVG
    icon_path = f"{SVG_DIR}/icon_{achievement_key}.svg"
    icon_tree = ET.parse(icon_path)
    icon_root = icon_tree.getroot()
    
    # Determine icon color based on level
    icon_color = LEVEL_COLORS.get(level, "white")
    
    # Helper to recursively recolor elements
    def recolor_element(element, color):
        # Update fill if it's white/light
        if element.get('fill') in ['white', '#ffffff', '#fff']:
            element.set('fill', color)
        # Update stroke if it's white/light
        if element.get('stroke') in ['white', '#ffffff', '#fff']:
            element.set('stroke', color)
            
        for child in element:
            recolor_element(child, color)

    # Recolor the icon root and all children
    recolor_element(icon_root, icon_color)
    
    # Get the icon's content (everything inside the svg tag)
    # We'll wrap it in a group and transform it to center on the badge
    icon_group = ET.Element('{http://www.w3.org/2000/svg}g')
    
    # The badge is 200x200, we want the icon centered and scaled to ~50%
    # Icon is 100x100, so we scale to 100 (50% of 200) and center it at (100, 100)
    # Transform: translate to center (50, 50 to move from 0,0 to center of icon)
    # then translate to badge center (100, 100)
    icon_group.set('transform', 'translate(50, 50)')
    
    # Copy all children from icon root to the group
    for child in icon_root:
        icon_group.append(child)
    
    # Add the icon group to the badge
    badge_root.append(icon_group)
    
    # Create a temporary file for the composite SVG
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.svg', delete=False)
    temp_path = temp_file.name
    
    # Write the composite SVG to the temporary file
    badge_tree.write(temp_path, encoding='unicode', xml_declaration=True)
    temp_file.close()
    
    return temp_path

def convert_svg_to_png(svg_path, png_path):
    """Convert SVG to PNG using inkscape."""
    import subprocess
    cmd = [
        "inkscape",
        "--export-type=png",
        "--export-width=200",
        "--export-height=200",
        svg_path,
        "-o", png_path
    ]
    subprocess.run(cmd, capture_output=True)

def main():
    """Generate all achievement badge PNGs using temporary composite SVGs."""
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_files = []
    
    for achievement_key in ACHIEVEMENTS:
        for level in LEVELS:
            # Create temporary composite SVG
            temp_svg_path = create_composite_svg(achievement_key, level)
            temp_files.append(temp_svg_path)
            
            # Convert to PNG for use in the game
            png_path = f"{OUTPUT_DIR}/{achievement_key}_{level}.png"
            convert_svg_to_png(temp_svg_path, png_path)
            print(f"Generated: {png_path}")
    
    # Clean up temporary SVG files
    for temp_file in temp_files:
        os.unlink(temp_file)
    
    print(f"\nGenerated {len(ACHIEVEMENTS) * len(LEVELS)} achievement badge PNGs!")

if __name__ == "__main__":
    main()
