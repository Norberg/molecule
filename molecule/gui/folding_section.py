import pyglet
from molecule import RenderingOrder
from .base import Widget
from .section import SectionHeader

class FoldingSection(Widget):
    def __init__(
        self,
        title: str,
        content: Widget | None,
        x: float = 0,
        y: float = 0,
        width: float = 200,
        height: float = 100,
        batch: pyglet.graphics.Batch | None = None,
        group: pyglet.graphics.Group | None = None,
        is_open: bool = True,
    ) -> None:
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
