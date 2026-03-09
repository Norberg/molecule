from typing import Any
from .base import Widget
import pyglet

class SpriteWidget(Widget):
    def __init__(self, image: Any, x: Any=0, y: Any=0, width: Any=None, height: Any=None, batch: Any=None, group: Any=None) -> None:
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

    def shift(self, dx: Any, dy: Any) -> None:
        super().shift(dx, dy)
        self.sprite.x += dx
        self.sprite.y += dy
