"""Golden Rain visual effect for PbI2(s) precipitation.

Creates a short‑lived particle emitter that spawns yellow flakes which
fall and fade out, simulating the classic bright crystalline "golden rain".

Kept intentionally lightweight (no new dependencies). Uses pyglet.shapes.
"""

import random
import pyglet
from pyglet import shapes
from molecule import RenderingOrder
from molecule.emitters.Emitters import register_emitter


class GoldenRainParticle:
    def __init__(self, batch, x, y, group):
        ox = random.uniform(-15, 15)
        oy = random.uniform(-10, 10)
        self.x = x + ox
        self.y = y + oy
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-380, -300)
        self.life = random.uniform(3.6, 5.2)
        self.age = 0.0
        radius = random.uniform(3.0, 6.0)
        base_colors = [
            (250, 210, 60),
            (255, 200, 40),
            (240, 190, 30),
            (255, 215, 80),
        ]
        color = random.choice(base_colors)
        self.shape = shapes.Circle(self.x, self.y, radius, color=color, batch=batch, group=group)
        self.shape.opacity = 255

    def update(self, dt):
        self.age += dt
        if self.age >= self.life:
            return False
        # Integrate simple motion
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Gentle gravity acceleration
        self.vy -= 80 * dt
        # Fade out towards end of life
        fade_progress = self.age / self.life
        self.shape.x = self.x
        self.shape.y = self.y
        self.shape.opacity = int(255 * (1.0 - fade_progress))
        return True

    def delete(self):
        if self.shape:
            self.shape.delete()
        self.shape = None


@register_emitter("golden_rain", auto_spawn=True)
class GoldenRainEmitter:
    def __init__(self, batch, position, particle_count=15):
        # Use a higher layer so particles are visible above beakers/effects
        group = RenderingOrder.charge  # above elements & background
        self.particles = [GoldenRainParticle(batch, position[0], position[1], group) for _ in range(particle_count)]
        self._dead = False

    def update(self, dt):
        if self._dead:
            return False
        alive = []
        for p in self.particles:
            if p.update(dt):
                alive.append(p)
            else:
                p.delete()
        self.particles = alive
        if not self.particles:
            self._dead = True
        return not self._dead

    def delete(self):
        for p in self.particles:
            p.delete()
        self.particles = []
        self._dead = True
