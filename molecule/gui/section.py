from pyglet.text import Label
from molecule import RenderingOrder
from .base import Widget

class SectionHeader(Widget):
    def __init__(self, text, x=0, y=0, width=200, height=30, batch=None, group=None):
        super().__init__(x, y, width, height, batch, group)
        self.text = text
        self._create_label()

    def _create_label(self):
        if self.batch:
            self.label = Label(
                self.text, x=self.x, y=self.y + self.height//2,
                batch=self.batch, group=RenderingOrder.gui,
                anchor_x='left', anchor_y='center',
                font_size=14, color=(0, 0, 0, 255), bold=True
            )
        else:
            self.label = None

    def delete(self):
        if self.label:
            self.label.delete()
        super().delete()
