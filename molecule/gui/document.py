from pyglet.text import Label, HTMLLabel
from molecule import RenderingOrder
from .base import Widget
from .theme import theme

class Document(Widget):
    def __init__(
        self,
        text: str,
        x: float,
        y: float,
        width: float,
        height: float | None = None,
        batch: object | None = None,
        group: object | None = None,
        font_size: int = 12,
        color: tuple[int, int, int, int] | list[int] | None = None,
        multiline: bool = True,
        is_fixed_size: bool = False,
        autosize_height: bool = False,
    ) -> None:
        super().__init__(x, y, width, height or 100, batch, group)
        self.text = text
        self.font_size = font_size
        self.color = color or theme.get_color("text_color")
        self.multiline = multiline
        self.is_fixed_size = is_fixed_size
        self.autosize_height = autosize_height
        self._create_label()

    def _create_label(self) -> None:
        pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
        x = self.x + pad_left
        y = self.y + self.height - pad_top
        width = self.width - pad_left - pad_right
        height = self.height - pad_top - pad_bottom
        if self.batch:
            group = self.group or RenderingOrder.gui
            if isinstance(self.text, str) and '<' in self.text and '>' in self.text:
                self.label = HTMLLabel(
                    self.text, x=x, y=y,
                    width=width, height=height,
                    batch=self.batch, group=group,
                    anchor_x='left', anchor_y='top',
                    multiline=self.multiline
                )
            else:
                self.label = Label(
                    self.text, x=x, y=y,
                    width=width, height=height,
                    batch=self.batch, group=group,
                    anchor_x='left', anchor_y='top',
                    font_size=self.font_size, color=self.color,
                    multiline=self.multiline
                )
            if self.autosize_height:
                self.height = self.label.content_height + pad_top + pad_bottom
                y = self.y + self.height - pad_top
                self.label.y = y
                self.label.height = self.height - pad_top - pad_bottom
        else:
            self.label = None

    def set_text(self, text: str) -> None:
        self.text = text
        if self.label:
            self.label.delete()
        self._create_label()

    def delete(self) -> None:
        if self.label:
            self.label.delete()
        super().delete()

    def shift(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy
        if self.label:
            self.label.x += dx
            self.label.y += dy

    def layout(self) -> None:
        if self.label:
            pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
            x = self.x + pad_left
            y = self.y + self.height - pad_top
            width = self.width - pad_left - pad_right
            height = self.height - pad_top - pad_bottom
            self.label.x = x
            self.label.y = y
            self.label.width = width
            self.label.height = height
