from .base import Widget
import pyglet

class SpriteWidget(Widget):
    def __init__(self, image, x=0, y=0, width=None, height=None, batch=None, group=None):
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

    def layout(self):
        self.sprite.x = self.x
        self.sprite.y = self.y

    def delete(self):
        self.sprite.delete()
        super().delete()

    def shift(self, dx, dy):
        super().shift(dx, dy)
        self.sprite.x += dx
        self.sprite.y += dy
