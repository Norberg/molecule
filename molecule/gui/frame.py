from pyglet.shapes import Rectangle
from molecule import RenderingOrder
from .theme import theme
from .base import Widget, draw_nine_patch

class Frame(Widget):
    def __init__(self, x, y, width, height, batch=None, group=None,
                 background_color=None, border_color=None,
                 is_expandable=False, frame_type="frame"):
        super().__init__(x, y, width, height, batch, group)
        self.background_color = background_color or theme.get_color("gui_color")
        self.border_color = border_color or [100, 100, 100, 255]
        self.children = []
        self.is_expandable = is_expandable
        self.frame_type = frame_type
        self._create_background()

    def _create_background(self):
        if self.batch:
            frame_theme = theme.theme_data.get(self.frame_type, theme.theme_data.get("frame"))
            img = None
            frame = [8, 8, 8, 8]
            padding = [8, 8, 8, 8]
            if frame_theme and "image" in frame_theme:
                img_name = frame_theme["image"]["source"]
                img = theme.get_image(img_name)
                frame = frame_theme["image"].get("frame", frame)
                padding = frame_theme["image"].get("padding", padding)
            if img:
                self.bg_slices = draw_nine_patch(self.batch, RenderingOrder.gui_background, img, self.x, self.y, self.width, self.height, frame, padding)
                self.bg_sprite = None
                self.bg_rect = None
                self.border_rect = None
            else:
                self.bg_slices = []
                self.bg_sprite = None
                color = self.background_color[:3]
                opacity = self.background_color[3] if len(self.background_color) > 3 else 255
                self.bg_rect = Rectangle(
                    self.x, self.y, self.width, self.height,
                    color=color,
                    batch=self.batch, group=RenderingOrder.gui_background
                )
                self.bg_rect.opacity = opacity

                border_color = self.border_color[:3]
                border_opacity = self.border_color[3] if len(self.border_color) > 3 else 255
                self.border_rect = Rectangle(
                    self.x - 1, self.y - 1, self.width + 2, self.height + 2,
                    color=border_color,
                    batch=self.batch, group=RenderingOrder.gui_background
                )
                self.border_rect.opacity = border_opacity
        else:
            self.bg_slices = []
            self.bg_sprite = None
            self.bg_rect = None
            self.border_rect = None

    def add(self, child):
        self.children.append(child)
        child.parent = self

    def add_child(self, child):
        self.add(child)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not self.contains_point(x, y):
            return False
        for child in reversed(self.children):
            if child and hasattr(child, 'on_mouse_scroll'):
                if child.on_mouse_scroll(x, y, scroll_x, scroll_y):
                    return True
        return False

    def on_mouse_motion(self, x, y, dx, dy):
        for child in reversed(self.children):
            if child and hasattr(child, 'on_mouse_motion'):
                if child.on_mouse_motion(x, y, dx, dy):
                    return True
        return False

    def layout(self):
        if self.bg_rect is not None:
            self.bg_rect.x = self.x
            self.bg_rect.y = self.y
            self.bg_rect.width = self.width
            self.bg_rect.height = self.height
        if self.border_rect is not None:
            self.border_rect.x = self.x - 1
            self.border_rect.y = self.y - 1
            self.border_rect.width = self.width + 2
            self.border_rect.height = self.height + 2
        if self.bg_slices:
            self._create_background()
        pad_left, pad_right, pad_top, pad_bottom = self.get_padding()
        for child in self.children:
            if child is None:
                continue
            child.x = self.x + pad_left
            child.y = self.y + pad_bottom
            if not getattr(child, 'is_fixed_size', False):
                child.width = self.width - pad_left - pad_right
                child.height = self.height - pad_top - pad_bottom
            if hasattr(child, 'layout'):
                child.layout()

    def delete(self):
        for child in self.children:
            child.delete()
        self.children.clear()
        for s in self.bg_slices:
            s.delete()
        self.bg_slices = []
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.delete()
        if hasattr(self, 'bg_rect') and self.bg_rect is not None:
            self.bg_rect.delete()
        if hasattr(self, 'border_rect') and self.border_rect is not None:
            self.border_rect.delete()
        super().delete()

    def get_padding(self):
        frame_theme = theme.theme_data.get(self.frame_type, theme.theme_data.get("frame"))
        if frame_theme and "image" in frame_theme:
            return frame_theme["image"].get("padding", [8, 8, 8, 8])
        return [8, 8, 8, 8]

    def shift(self, dx, dy):
        self.x += dx
        self.y += dy
        if self.bg_rect is not None:
            self.bg_rect.x += dx
            self.bg_rect.y += dy
        if self.border_rect is not None:
            self.border_rect.x += dx
            self.border_rect.y += dy
        for s in self.bg_slices:
            s.x += dx
            s.y += dy
        for c in self.children:
            if c is None:
                continue
            if hasattr(c, 'shift'):
                c.shift(dx, dy)
            else:
                c.x += dx
                c.y += dy

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.contains_point(x, y):
            return False
        for child in reversed(self.children):
            if child and hasattr(child, 'on_mouse_press'):
                if child.on_mouse_press(x, y, button, modifiers):
                    return True
        return False

    def on_mouse_release(self, x, y, button, modifiers):
        for child in reversed(self.children):
            if child and hasattr(child, 'on_mouse_release'):
                if child.on_mouse_release(x, y, button, modifiers):
                    return True
        return False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.contains_point(x, y):
            return False
        for child in reversed(self.children):
            if child and hasattr(child, 'on_mouse_drag'):
                if child.on_mouse_drag(x, y, dx, dy, buttons, modifiers):
                    return True
        return False
