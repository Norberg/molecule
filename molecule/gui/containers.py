from .base import Widget

class Container(Widget):
    def __init__(self, x, y, width, height, batch=None, group=None):
        super().__init__(x, y, width, height, batch, group)
        self.children = []
        self.align = 'left'

    def add(self, widget):
        if widget:
            widget.parent = self
        self.children.append(widget)
        self.layout()

    def remove(self, widget):
        if widget in self.children:
            self.children.remove(widget)
            widget.delete()
            self.layout()

    def _layout_children(self):
        pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
        if hasattr(self, 'get_padding'):
            pad_left, pad_right, pad_top, pad_bottom = self.get_padding()
        current_y = self.y + self.height - pad_top
        for child in self.children:
            if child is None:
                continue
            child.x = self.x + pad_left
            child.width = self.width - pad_left - pad_right
            child.y = current_y - child.height
            current_y -= child.height
            if self.align == 'center':
                child.x = self.x + (self.width - child.width) // 2
            elif self.align == 'right':
                child.x = self.x + self.width - child.width
            else:
                child.x = self.x

    def layout(self):
        self._layout_children()
        for child in self.children:
            if hasattr(child, 'layout'):
                child.layout()

    def shift(self, dx, dy):
        super().shift(dx, dy)
        for child in self.children:
            if child:
                if hasattr(child, 'shift'):
                    child.shift(dx, dy)
                else:
                    child.x += dx
                    child.y += dy

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not self.contains_point(x, y):
            return False
        for child in reversed(self.children):
            if child and hasattr(child, 'on_mouse_scroll'):
                if child.on_mouse_scroll(x, y, scroll_x, scroll_y):
                    return True
        return False

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
            if child and child.contains_point(x, y) and hasattr(child, 'on_mouse_release'):
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

class VerticalContainer(Container):
    def __init__(self, x, y, width, height, batch=None, group=None, spacing=0):
        super().__init__(x, y, width, height, batch, group)
        self.spacing = spacing

    def _layout_children(self):
        pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
        if hasattr(self, 'get_padding'):
            pad_left, pad_right, pad_top, pad_bottom = self.get_padding()
        spacing = self.spacing
        current_y = self.y + self.height - pad_top
        for i, child in enumerate(self.children):
            if child is None:
                continue
            child.x = self.x + pad_left
            child.width = self.width - pad_left - pad_right
            child.y = current_y - child.height
            current_y -= child.height
            if i < len(self.children) - 1:
                current_y -= spacing
            if self.align == 'center':
                child.x = self.x + (self.width - child.width) // 2
            elif self.align == 'right':
                child.x = self.x + self.width - child.width
            else:
                child.x = self.x

class HorizontalContainer(Container):
    def __init__(self, x, y, width, height, batch=None, group=None, spacing=0):
        super().__init__(x, y, width, height, batch, group)
        self.spacing = spacing

    def _layout_children(self):
        pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
        if hasattr(self, 'get_padding'):
            pad_left, pad_right, pad_top, pad_bottom = self.get_padding()
        current_x = self.x + pad_left
        for child in self.children:
            if child is None:
                continue
            child.x = current_x
            child.y = self.y + pad_bottom
            child.height = self.height - pad_top - pad_bottom
            current_x += child.width + self.spacing
