import pyglet
from .base import Widget

class SpriteWidget(Widget):
    def __init__(
        self,
        image: pyglet.image.AbstractImage,
        x: float = 0,
        y: float = 0,
        width: float | None = None,
        height: float | None = None,
        batch: object | None = None,
        group: object | None = None,
    ) -> None:
        w = width or image.width
        h = height or image.height
        super().__init__(x, y, w, h, batch, group)
        self.is_fixed_size = True
        self.image = image
        self.sprite = pyglet.sprite.Sprite(image, x=x, y=y, batch=batch, group=group)
        if width and height:
            self.sprite.scale_x = width / image.width
            self.sprite.scale_y = height / image.height
        elif width:
            self.sprite.scale = width / image.width
        elif height:
            self.sprite.scale = height / image.height

    def layout(self) -> None:
        self.sprite.x = self.x
        self.sprite.y = self.y

    def delete(self) -> None:
        self.sprite.delete()
        super().delete()

    def shift(self, dx: float, dy: float) -> None:
        super().shift(dx, dy)
        self.sprite.x += dx
        self.sprite.y += dy
