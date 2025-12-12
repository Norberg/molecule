from .constants import GUI_PADDING

class Manager:
    def __init__(self, content, window, batch, group=None, anchor='bottom_left',
                 theme_obj=None, is_movable=False):
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
        self.window.push_handlers(self)

    def update_position(self):
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
        else:
            target_x = old_x
            target_y = old_y
        dx = target_x - old_x
        dy = target_y - old_y
        if dx == 0 and dy == 0:
            return
        self.content.shift(dx, dy)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.content and hasattr(self.content, 'on_mouse_scroll'):
            return self.content.on_mouse_scroll(x, y, scroll_x, scroll_y)
        return False

    def on_mouse_press(self, x, y, button, modifiers):
        if self.content and hasattr(self.content, 'on_mouse_press'):
            return self.content.on_mouse_press(x, y, button, modifiers)
        return False

    def on_mouse_release(self, x, y, button, modifiers):
        if self.content and hasattr(self.content, 'on_mouse_release'):
            return self.content.on_mouse_release(x, y, button, modifiers)
        return False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.content and hasattr(self.content, 'on_mouse_drag'):
            return self.content.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        return False

    def delete(self):
        self.window.remove_handlers(self)
        if self.content:
            self.content.delete()
