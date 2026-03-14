from typing import Sequence

import pyglet


class Widget:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        batch: object | None = None,
        group: object | None = None,
    ) -> None:
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.batch = batch
        self.group = group
        self.visible = True

    def contains_point(self, x: float, y: float) -> bool:
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)

    def delete(self) -> None:
        pass

    def shift(self, dx: float, dy: float) -> None:
        self.x += dx
        self.y += dy

    def on_mouse_scroll(
        self, x: float, y: float, scroll_x: float, scroll_y: float
    ) -> bool:
        return False

def draw_nine_patch(
    batch: object | None,
    group: object | None,
    img: pyglet.image.AbstractImage,
    x: float,
    y: float,
    width: float,
    height: float,
    frame: Sequence[int],
    padding: Sequence[int],
) -> list[pyglet.sprite.Sprite]:
    left, top, right, bottom = frame
    img_w, img_h = img.width, img.height

    center_w = img_w - left - right
    center_h = img_h - top - bottom

    parts = []
    parts.append(('bl', 0, 0, left, bottom, x, y, left, bottom))
    parts.append(('br', img_w - right, 0, right, bottom, x + width - right, y, right, bottom))
    parts.append(('tl', 0, img_h - top, left, top, x, y + height - top, left, top))
    parts.append(('tr', img_w - right, img_h - top, right, top, x + width - right, y + height - top, right, top))
    parts.append(('b', left, 0, center_w, bottom, x + left, y, width - left - right, bottom))
    parts.append(('t', left, img_h - top, center_w, top, x + left, y + height - top, width - left - right, top))
    parts.append(('l', 0, bottom, left, center_h, x, y + bottom, left, height - top - bottom))
    parts.append(('r', img_w - right, bottom, right, center_h, x + width - right, y + bottom, right, height - top - bottom))
    parts.append(('c', left, bottom, center_w, center_h, x + left, y + bottom, width - left - right, height - top - bottom))

    sprites = []
    for (name, sx, sy, sw, sh, dx, dy, dw, dh) in parts:
        if sw <= 0 or sh <= 0 or dw <= 0 or dh <= 0:
            continue
        region = img.get_region(sx, sy, sw, sh)
        sprite = pyglet.sprite.Sprite(region, x=dx, y=dy, batch=batch, group=group)
        if dw != sw:
            sprite.scale_x = dw / sw
        if dh != sh:
            sprite.scale_y = dh / sh
        sprites.append(sprite)
    return sprites
