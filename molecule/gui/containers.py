from .base import Widget

class Container(Widget):
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        batch: object | None = None,
        group: object | None = None,
    ) -> None:
        super().__init__(x, y, width, height, batch, group)
        self.children: list[Widget] = []
        self.align = 'left'

    def add(self, widget: Widget, do_layout: bool = True) -> None:
        if widget:
            widget.parent = self
            self.children.append(widget)
            if do_layout:
                self.layout()

    def remove(self, widget: Widget) -> None:
        if widget in self.children:
            self.children.remove(widget)
            widget.delete()
            self.layout()

    def delete(self) -> None:
        for child in list(self.children):
            if child:
                child.delete()
        self.children = []
        super().delete()

    def _layout_children(self) -> None:
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

    def layout(self) -> None:
        self._layout_children()
        for child in self.children:
            child.layout()

    def shift(self, dx: float, dy: float) -> None:
        super().shift(dx, dy)
        for child in self.children:
            if child:
                child.shift(dx, dy)

    def on_mouse_scroll(
        self, x: float, y: float, scroll_x: float, scroll_y: float
    ) -> bool:
        if not self.contains_point(x, y):
            return False
        for child in reversed(self.children):
            if child and child.on_mouse_scroll(x, y, scroll_x, scroll_y):
                return True
        return False

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float) -> bool:
        for child in reversed(self.children):
            if child and child.on_mouse_motion(x, y, dx, dy):
                return True
        return False

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int) -> bool:
        if not self.contains_point(x, y):
            return False
        for child in reversed(self.children):
            if child and child.on_mouse_press(x, y, button, modifiers):
                return True
        return False

    def on_mouse_release(
        self, x: float, y: float, button: int, modifiers: int
    ) -> bool:
        for child in reversed(self.children):
            if child and child.on_mouse_release(x, y, button, modifiers):
                return True
        return False

    def on_mouse_drag(
        self, x: float, y: float, dx: float, dy: float, buttons: int, modifiers: int
    ) -> bool:
        if not self.contains_point(x, y):
            return False
        for child in reversed(self.children):
            if child and child.on_mouse_drag(x, y, dx, dy, buttons, modifiers):
                return True
        return False

class VerticalContainer(Container):
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        batch: object | None = None,
        group: object | None = None,
        spacing: float = 0,
    ) -> None:
        super().__init__(x, y, width, height, batch, group)
        self.spacing = spacing

    def _layout_children(self) -> None:
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
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        batch: object | None = None,
        group: object | None = None,
        spacing: float = 0,
    ) -> None:
        super().__init__(x, y, width, height, batch, group)
        self.spacing = spacing

    def _layout_children(self) -> None:
        pad_left, pad_right, pad_top, pad_bottom = self.get_padding()
        current_x = self.x + pad_left
        for child in self.children:
            if child is None:
                continue
            child.x = current_x
            child.y = self.y + pad_bottom
            child.height = self.height - pad_top - pad_bottom
            current_x += child.width + self.spacing

class AbsoluteContainer(Container):
    """A container that does not enforce width/height on its children during layout."""
    def _layout_children(self) -> None:
        # Simply don't do anything to children coordinates or sizes
        return None
