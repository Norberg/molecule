from typing import Any
from molecule import RenderingOrder
from .base import Widget
from .section import SectionHeader

class FoldingSection(Widget):
    def __init__(self, title: Any, content: Any, x: Any=0, y: Any=0, width: Any=200, height: Any=100,
                 batch: Any=None, group: Any=None, is_open: Any=True) -> None:
        super().__init__(x, y, width, height, batch, group)
        self.title = title
        self.content = content
        self.is_open = is_open
        self.header: SectionHeader | None = None
        self._create_widgets()

    def _create_widgets(self) -> None:
        if self.batch:
            self.header = SectionHeader(self.title, self.x, self.y + self.height - 30,
                                       self.width, 30, self.batch, RenderingOrder.gui)
            if self.is_open and self.content:
                self.content.x = self.x
                self.content.y = self.y
                self.content.width = self.width
                self.content.height = self.height - 30
        else:
            self.header = None

    def delete(self) -> None:
        if self.header:
            self.header.delete()
        if self.content:
            self.content.delete()
        super().delete()
