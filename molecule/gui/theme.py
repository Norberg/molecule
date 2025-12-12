import json
import os
import pyglet

class Theme:
    def __init__(self, theme_path="molecule/theme/theme.json"):
        self.theme_path = theme_path
        self.theme_data = self._load_theme()
        self.images = {}
        self._load_images()

    def _load_theme(self):
        try:
            with open(self.theme_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load theme: {e}")
            return {
                "font": "Arial",
                "font_size": 12,
                "text_color": [0, 0, 0, 255],
                "gui_color": [255, 255, 255, 255]
            }

    def _load_images(self):
        theme_dir = os.path.dirname(self.theme_path)
        image_files = [
            "button.png", "button-down.png", "button-highlight.png",
            "panel.png", "green_panel.png", "titlepanel.png",
            "green-button-up.png", "red-button-down.png",
            "vscrollbar.png", "hscrollbar.png"
        ]
        for img_file in image_files:
            try:
                img_path = os.path.join(theme_dir, img_file)
                if os.path.exists(img_path):
                    self.images[img_file] = pyglet.image.load(img_path)
                else:
                    print(f"Theme image not found: {img_path}")
            except Exception as e:
                print(f"Failed to load theme image {img_file}: {e}")

    def get_image(self, image_name):
        return self.images.get(image_name)

    def get_color(self, color_name):
        return self.theme_data.get(color_name, [0, 0, 0, 255])

# Global theme instance
theme = Theme()
