from pyglet.shapes import Rectangle
from pyglet.text import HTMLLabel
from molecule import RenderingOrder
from .base import Widget, draw_nine_patch
from .theme import theme

class Button(Widget):
    def __init__(self, text, x, y, width, height, batch=None, group=None,
                 on_click=None, background_color=None, button_type="button"):
        super().__init__(x, y, width, height, batch, group)
        self.text = text
        self.on_click = on_click
        self.background_color = background_color or [150, 150, 150, 255]
        self.button_type = button_type
        self.pressed = False
        self._create_button()

    def _create_button(self):
        if not self.batch:
            self.bg_slices = []
            self.bg_sprite = None
            self.bg_rect = None
            self.label = None
            return
        btn_theme = theme.theme_data.get(self.button_type, theme.theme_data.get("button")) or {}
        self._up_conf = (btn_theme.get("up") or {}).get("image")
        self._down_conf = (btn_theme.get("down") or {}).get("image")
        self._up_text_color = (btn_theme.get("up") or {}).get("text_color", [0,0,0,255])
        self._down_text_color = (btn_theme.get("down") or {}).get("text_color", self._up_text_color)

        def build_slices(conf):
            if not conf:
                return None
            img = theme.get_image(conf.get("source", ""))
            if not img:
                return None
            frame = conf.get("frame", [6,6,6,6])
            padding = conf.get("padding", [8,8,8,8])
            slices = draw_nine_patch(self.batch, RenderingOrder.gui_background, img, self.x, self.y, self.width, self.height, frame, padding)
            return {'slices': slices, 'frame': frame, 'padding': padding}

        self._up_slices = build_slices(self._up_conf)
        self._down_slices = build_slices(self._down_conf)

        self.bg_rect = None
        if not self._up_slices:
            self.bg_rect = Rectangle(
                self.x, self.y, self.width, self.height,
                color=self.background_color,
                batch=self.batch, group=RenderingOrder.gui_background
            )
        if self._down_slices:
            for s in self._down_slices['slices']:
                s.visible = False
        self.label = HTMLLabel(
            self.text, x=self.x + self.width//2, y=self.y + self.height//2,
            batch=self.batch, group=RenderingOrder.gui,
            anchor_x='center', anchor_y='center'
        )

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.contains_point(x, y):
            return False
        self.pressed = True
        if self._down_slices:
            if self._up_slices:
                for s in self._up_slices['slices']:
                    s.visible = False
            for s in self._down_slices['slices']:
                s.visible = True
            if self.label:
                self.label.color = tuple(self._down_text_color)
        elif self.bg_rect is not None:
            if not hasattr(self, '_orig_color'):
                self._orig_color = tuple(self.bg_rect.color)
            r,g,b = self._orig_color
            self.bg_rect.color = (max(0,int(r*0.7)), max(0,int(g*0.7)), max(0,int(b*0.7)))
        return True

    def on_mouse_release(self, x, y, button, modifiers):
        was_pressed = self.pressed
        self.pressed = False
        if self._down_slices and self._up_slices:
            for s in self._down_slices['slices']:
                s.visible = False
            for s in self._up_slices['slices']:
                s.visible = True
            if self.label:
                self.label.color = tuple(self._up_text_color)
        elif self.bg_rect is not None and hasattr(self, '_orig_color'):
            self.bg_rect.color = self._orig_color
        if was_pressed and self.contains_point(x, y) and self.on_click:
            self.on_click(self)

    def delete(self):
        if self.label:
            self.label.delete()
        for s in self.bg_slices if hasattr(self, 'bg_slices') and self.bg_slices else []:
            s.delete()
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.delete()
        if hasattr(self, 'bg_rect') and self.bg_rect is not None:
            self.bg_rect.delete()
        super().delete()

    def get_padding(self):
        btn_theme = theme.theme_data.get(self.button_type, theme.theme_data.get("button"))
        if btn_theme and "up" in btn_theme and "image" in btn_theme["up"]:
            return btn_theme["up"]["image"].get("padding", [8, 8, 8, 8])
        return [8, 8, 8, 8]

    def shift(self, dx, dy):
        self.x += dx
        self.y += dy
        if self.label:
            self.label.x += dx
            self.label.y += dy
        def shift_slices(conf):
            if not conf:
                return
            for s in conf['slices']:
                s.x += dx
                s.y += dy
        shift_slices(self._up_slices)
        shift_slices(self._down_slices)
        if self.bg_rect is not None:
            self.bg_rect.x += dx
            self.bg_rect.y += dy

    def layout(self):
        self._create_button()

class OneTimeButton(Button):
    def __init__(self, text, x=0, y=0, width=100, height=30, batch=None, group=None,
                 on_click=None, background_color=None):
        super().__init__(text, x, y, width, height, batch, group, on_click, background_color, "molecule-button")
        self.is_pressed = False

    def on_mouse_release(self, x, y, button, modifiers):
        if self.pressed and self.contains_point(x, y):
            self.is_pressed = True
            if self.on_click:
                self.on_click(self)
        self.pressed = False
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            normal_img = theme.get_image("green-button-up.png")
            if normal_img:
                self.bg_sprite.image = normal_img

    def change_state(self):
        self.is_pressed = not self.is_pressed

    def get_path(self):
        path = ["molecule-button"]
        if self.is_pressed:
            path.append('down')
        else:
            path.append('up')
        return path
