from __future__ import annotations

from pyglet.shapes import Rectangle
from molecule import RenderingOrder
from .base import Widget, draw_nine_patch
from .scissor_group import ScissorGroup
from .theme import theme

class Scrollable(Widget):
    @staticmethod
    def _get_theme_dict(value: object) -> dict[str, object]:
        return value if isinstance(value, dict) else {}

    def __init__(
        self,
        content: Widget | None,
        x: float = 0,
        y: float = 0,
        width: float = 200,
        height: float = 100,
        batch: object | None = None,
        group: object | None = None,
        height_limit: float | None = None,
    ) -> None:
        super().__init__(x, y, width, height, batch, group)
        self.content = content
        self.height_limit = height_limit or height
        self.scroll_offset = 0.0
        self.scrollbar_width = 16
        self.scissor_group: ScissorGroup | None
        if self.batch:
            self.scissor_group = ScissorGroup(x, y, width, height, parent=group)
        else:
            self.scissor_group = None
        self._setup_scrolling()
        self.scrollbar_bg_items = []
        self.scrollbar_handle_items = []

    def _setup_scrolling(self) -> None:
        if self.content:
            if self.scissor_group:
                self.content.group = self.scissor_group
                if hasattr(self.content, '_create_label'):
                    if hasattr(self.content, 'label') and self.content.label:
                        self.content.label.delete()
                    self.content._create_label()
            self.content.x = self.x
            self.content.y = self.y + self.height - self.content.height + self.scroll_offset
            self.content.width = self.width - self.scrollbar_width

    def on_mouse_scroll(
        self, x: float, y: float, scroll_x: float, scroll_y: float
    ) -> bool:
        if not self.contains_point(x, y):
            return False
        content_height = self.content.height if self.content else 0
        view_height = self.height
        if content_height <= view_height:
            return False
        max_scroll = content_height - view_height
        scroll_speed = 20
        self.scroll_offset -= scroll_y * scroll_speed
        if self.scroll_offset < 0:
            self.scroll_offset = 0
        if self.scroll_offset > max_scroll:
            self.scroll_offset = max_scroll
        self._update_positions()
        return True

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not self.contains_point(x, y):
            return False
        if self.content and hasattr(self.content, 'on_mouse_press'):
            return self.content.on_mouse_press(x, y, button, modifiers)
        return False

    def on_mouse_release(
        self, x: float, y: float, button: int, modifiers: int
    ) -> bool:
        if self.content and hasattr(self.content, 'on_mouse_release'):
            return self.content.on_mouse_release(x, y, button, modifiers)
        return False

    def on_mouse_drag(
        self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int
    ) -> bool:
        if not self.contains_point(x, y):
            return False
        if self.content and hasattr(self.content, 'on_mouse_drag'):
            return self.content.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        return False

    def _create_scrollbar_part(
        self, part_name: str, x: float, y: float, width: float, height: float
    ) -> list[object]:
        if not self.batch:
            return []
        items = []
        sb_theme = self._get_theme_dict(theme.theme_data.get("vscrollbar", {}))
        part_theme = self._get_theme_dict(sb_theme.get(part_name))
        img_conf = self._get_theme_dict(part_theme.get("image"))
        if img_conf:
            source = img_conf.get("source")
            img = theme.get_image(source if isinstance(source, str) else "")
            if img:
                region_rect = img_conf.get("region")
                if isinstance(region_rect, (list, tuple)):
                    img = img.get_region(*region_rect)
                frame = img_conf.get("frame", [0, 0, 0, 0])
                if not isinstance(frame, list):
                    frame = [0, 0, 0, 0]
                padding = img_conf.get("padding", [0, 0, 0, 0])
                if not isinstance(padding, list):
                    padding = [0, 0, 0, 0]
                items = draw_nine_patch(self.batch, self.group, img, x, y, width, height, frame, padding)
                return items
        color = (200, 200, 200, 255) if part_name == "bar" else (100, 100, 100, 255)
        rect = Rectangle(x, y, width, height, color=color, batch=self.batch, group=self.group)
        return [rect]

    def _update_positions(self) -> None:
        if self.content:
            self.content.width = self.width - self.scrollbar_width
            self.content.y = self.y + self.height - self.content.height + self.scroll_offset
            self.content.x = self.x
            if hasattr(self.content, 'layout'):
                self.content.layout()
            if self.scissor_group:
                self.scissor_group.x = int(self.x)
                self.scissor_group.y = int(self.y)
                self.scissor_group.width = int(self.width)
                self.scissor_group.height = int(self.height)
            for item in self.scrollbar_bg_items:
                item.delete()
            self.scrollbar_bg_items = []
            for item in self.scrollbar_handle_items:
                item.delete()
            self.scrollbar_handle_items = []
            should_show_scrollbar = self.content.height > self.height
            if should_show_scrollbar:
                self.scrollbar_bg_items = self._create_scrollbar_part("bar",
                    self.x + self.width - self.scrollbar_width, self.y,
                    self.scrollbar_width, self.height)
                ratio = self.height / self.content.height
                handle_height = max(20, self.height * ratio)
                max_scroll = self.content.height - self.height
                scroll_ratio = self.scroll_offset / max_scroll if max_scroll > 0 else 0
                track_height = self.height
                scrollable_track = track_height - handle_height
                handle_y = self.y + self.height - handle_height - (scrollable_track * scroll_ratio)
                self.scrollbar_handle_items = self._create_scrollbar_part("knob",
                    self.x + self.width - self.scrollbar_width, handle_y,
                    self.scrollbar_width, handle_height)

    def layout(self) -> None:
        self._update_positions()

    def shift(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy
        self._update_positions()

    def delete(self) -> None:
        if self.content:
            self.content.delete()
        for item in self.scrollbar_bg_items:
            item.delete()
        for item in self.scrollbar_handle_items:
            item.delete()
        super().delete()
