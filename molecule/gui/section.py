from typing import Any
from pyglet.text import Label
from molecule import RenderingOrder
from .base import Widget

class SectionHeader(Widget):
    def __init__(self, text: Any, x: Any=0, y: Any=0, width: Any=200, height: Any=30, batch: Any=None, group: Any=None) -> None:
        super().__init__(x, y, width, height, batch, group)
        self.text = text
        self._create_label()

    def _create_label(self) -> None:
        if self.batch:
            self.label = Label(
                self.text, x=self.x, y=self.y + self.height//2,
                batch=self.batch, group=RenderingOrder.gui,
                anchor_x='left', anchor_y='center',
                font_size=14, color=(0, 0, 0, 255), bold=True
            )
        else:
            self.label = None

    def delete(self) -> None:
        if self.label:
            self.label.delete()
        super().delete()
