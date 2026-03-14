from __future__ import annotations

from typing import Callable
import pyglet
from pyglet.shapes import Rectangle
from pyglet.text import HTMLLabel
from molecule import RenderingOrder
from .base import Widget, draw_nine_patch
from .theme import theme

class Button(Widget):
    def __init__(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        height: float,
        batch: pyglet.graphics.Batch | None = None,
        group: pyglet.graphics.Group | None = None,
        on_click: Callable[[Button], None] | None = None,
        background_color: list[int] | None = None,
        button_type: str = "button",
    ) -> None:
        super().__init__(x, y, width, height, batch, group)
        self.text = text
        self.on_click = on_click
        self.background_color = background_color or [150, 150, 150, 255]
        self.button_type = button_type
        self.pressed = False
        self.bg_slices: list[pyglet.sprite.Sprite] = []
        self.bg_sprite: pyglet.sprite.Sprite | None = None
        self.bg_rect: Rectangle | None = None
        self.label: HTMLLabel | None = None
        self._orig_color: tuple[int, int, int] | None = None
        self._create_button()

    @staticmethod
    def _get_theme_dict(value: object) -> dict[str, object]:
        return value if isinstance(value, dict) else {}

    def _create_button(self) -> None:
        if not self.batch:
            self.bg_slices = []
            self.bg_sprite = None
            self.bg_rect = None
            self.label = None
            return
        btn_theme = self._get_theme_dict(
            theme.theme_data.get(self.button_type, theme.theme_data.get("button"))
        )
        up_theme = self._get_theme_dict(btn_theme.get("up"))
        down_theme = self._get_theme_dict(btn_theme.get("down"))
        self._up_conf = self._get_theme_dict(up_theme.get("image")) or None
        self._down_conf = self._get_theme_dict(down_theme.get("image")) or None
        up_text_color = up_theme.get("text_color", [0, 0, 0, 255])
        self._up_text_color = (
            up_text_color if isinstance(up_text_color, list) else [0, 0, 0, 255]
        )
        down_text_color = down_theme.get("text_color", self._up_text_color)
        self._down_text_color = (
            down_text_color if isinstance(down_text_color, list) else self._up_text_color
        )

        def build_slices(conf: dict[str, object] | None) -> dict[str, object] | None:
            if not conf:
                return None
            source = conf.get("source")
            img = theme.get_image(source if isinstance(source, str) else "")
            if not img:
                return None
            frame = conf.get("frame", [6,6,6,6])
            if not isinstance(frame, list):
                frame = [6,6,6,6]
            padding = conf.get("padding", [8,8,8,8])
            if not isinstance(padding, list):
                padding = [8,8,8,8]
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

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
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
            if self._orig_color is None:
                self._orig_color = tuple(self.bg_rect.color)
            r, g, b = self._orig_color
            self.bg_rect.color = (max(0,int(r*0.7)), max(0,int(g*0.7)), max(0,int(b*0.7)))
        return True

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        was_pressed = self.pressed
        self.pressed = False
        if self._down_slices and self._up_slices:
            for s in self._down_slices['slices']:
                s.visible = False
            for s in self._up_slices['slices']:
                s.visible = True
            if self.label:
                self.label.color = tuple(self._up_text_color)
        elif self.bg_rect is not None and self._orig_color is not None:
            self.bg_rect.color = self._orig_color
        if was_pressed and self.contains_point(x, y) and self.on_click:
            self.on_click(self)

    def delete(self) -> None:
        if self.label:
            self.label.delete()
        for s in self.bg_slices:
            s.delete()
        if self.bg_sprite:
            self.bg_sprite.delete()
        if self.bg_rect is not None:
            self.bg_rect.delete()
        super().delete()

    def get_padding(self) -> list[int]:
        btn_theme = self._get_theme_dict(
            theme.theme_data.get(self.button_type, theme.theme_data.get("button"))
        )
        up_theme = self._get_theme_dict(btn_theme.get("up"))
        image_theme = self._get_theme_dict(up_theme.get("image"))
        if image_theme:
            padding = image_theme.get("padding", [8, 8, 8, 8])
            if isinstance(padding, list):
                return padding
        return [8, 8, 8, 8]

    def shift(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy
        if self.label:
            self.label.x += dx
            self.label.y += dy
        def shift_slices(conf: dict[str, object] | None) -> None:
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

    def layout(self) -> None:
        self._create_button()

class OneTimeButton(Button):
    def __init__(
        self,
        text: str,
        x: float = 0,
        y: float = 0,
        width: float = 100,
        height: float = 30,
        batch: pyglet.graphics.Batch | None = None,
        group: pyglet.graphics.Group | None = None,
        on_click: Callable[[Button], None] | None = None,
        background_color: list[int] | None = None,
    ) -> None:
        super().__init__(text, x, y, width, height, batch, group, on_click, background_color, "molecule-button")
        self.is_pressed = False

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> None:
        if self.pressed and self.contains_point(x, y):
            self.is_pressed = True
            if self.on_click:
                self.on_click(self)
        self.pressed = False
        if self.bg_sprite:
            normal_img = theme.get_image("green-button-up.png")
            if normal_img:
                self.bg_sprite.image = normal_img

    def change_state(self) -> None:
        self.is_pressed = not self.is_pressed

    def get_path(self) -> list[str]:
        path = ["molecule-button"]
        if self.is_pressed:
            path.append('down')
        else:
            path.append('up')
        return path
