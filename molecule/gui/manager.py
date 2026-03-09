from typing import Literal
from .constants import GUI_PADDING

class Manager:
    def __init__(
        self,
        content: object,
        window: object,
        batch: object,
        group: object | None = None,
        anchor: Literal['bottom_left', 'bottom_right', 'top_left', 'top_right', 'center'] | None = 'bottom_left',
        theme_obj: object | None = None,
        is_movable: bool = False,
        push_handlers: bool = True,
    ) -> None:
        self.content = content
        self.window = window
        self.batch = batch
        self.group = group
        self.anchor = anchor
        self.theme_obj = theme_obj
        self.is_movable = is_movable
        if hasattr(self.content, 'layout'):
            self.content.layout()
        self.update_position()
        if push_handlers:
            self.window.push_handlers(self)

    def update_position(self) -> None:
        window_width, window_height = self.window.get_size()
        old_x, old_y = self.content.x, self.content.y
        if self.anchor == 'bottom_left':
            target_x = GUI_PADDING
            target_y = GUI_PADDING
        elif self.anchor == 'bottom_right':
            target_x = window_width - self.content.width - GUI_PADDING
            target_y = GUI_PADDING
        elif self.anchor == 'top_right':
            target_x = window_width - self.content.width - GUI_PADDING
            target_y = window_height - self.content.height - GUI_PADDING
        elif self.anchor == 'top_left':
            target_x = GUI_PADDING
            target_y = window_height - self.content.height - GUI_PADDING
        elif self.anchor == 'center':
            target_x = (window_width - self.content.width) // 2
            target_y = (window_height - self.content.height) // 2
        else:
            target_x = old_x
            target_y = old_y
        dx = target_x - old_x
        dy = target_y - old_y
        if dx == 0 and dy == 0:
            return
        self.content.shift(dx, dy)

    def on_mouse_scroll(self, x: float, y: float, scroll_x: float, scroll_y: float) -> bool:
        if self.content and hasattr(self.content, 'on_mouse_scroll'):
            return self.content.on_mouse_scroll(x, y, scroll_x, scroll_y)
        return False

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if self.content and hasattr(self.content, 'on_mouse_press'):
            return self.content.on_mouse_press(x, y, button, modifiers)
        return False

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if self.content and hasattr(self.content, 'on_mouse_release'):
            return self.content.on_mouse_release(x, y, button, modifiers)
        return False

    def on_mouse_drag(
        self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int
    ) -> bool:
        if self.content and hasattr(self.content, 'on_mouse_drag'):
            return self.content.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        return False

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> bool:
        if self.content and hasattr(self.content, 'on_mouse_motion'):
            return self.content.on_mouse_motion(x, y, dx, dy)
        return False

    def on_key_press(self, symbol: int, modifiers: int) -> bool:
        if self.content and hasattr(self.content, 'on_key_press'):
            return self.content.on_key_press(symbol, modifiers)
        return False

    def delete(self) -> None:
        self.window.remove_handlers(self)
        if self.content:
            self.content.delete()
