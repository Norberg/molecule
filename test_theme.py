#!/usr/bin/env python3

import sys
import os
sys.path.append('.')

from molecule.CustomGUI import theme

print("Testing theme loading...")
print(f"Theme path: {theme.theme_path}")
print(f"Available images: {list(theme.images.keys())}")

# Test specific images
test_images = ["panel.png", "button.png", "green-button-up.png"]
for img_name in test_images:
    img = theme.get_image(img_name)
    if img:
        print(f"✓ {img_name}: {img.width}x{img.height}")
    else:
        print(f"✗ {img_name}: Not found")

print("\nTheme data keys:", list(theme.theme_data.keys())) 