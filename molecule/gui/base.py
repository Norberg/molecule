class Widget:
    def __init__(self, x, y, width, height, batch=None, group=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.batch = batch
        self.group = group
        self.visible = True

    def contains_point(self, x, y):
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)

    def delete(self):
        pass

    def shift(self, dx, dy):
        self.x += dx
        self.y += dy

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        return False

# Shared GUI helpers
import pyglet

def draw_nine_patch(batch, group, img, x, y, width, height, frame, padding):
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
