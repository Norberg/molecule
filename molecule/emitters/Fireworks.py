"""Fireworks particle emitter.

Spawns an ascending rocket that explodes into colorful particles.
Color can be overridden via 'color' (#RRGGBB) parameter; otherwise random hue.
Lightweight pyglet implementation.
"""
import random, math
import pyglet
from pyglet import shapes
from molecule import RenderingOrder
from molecule.emitters.Emitters import register_emitter

def _parse_hex(color_hex):
    if not color_hex:
        return None
    color_hex = color_hex.strip().lstrip('#')
    if len(color_hex) != 6:
        raise ValueError(f"Invalid color hex '{color_hex}'")
    r = int(color_hex[0:2], 16)
    g = int(color_hex[2:4], 16)
    b = int(color_hex[4:6], 16)
    return (r, g, b)


class _ExplosionParticle:
    """Primary explosion fragment.

    scale: allows shrinking (radius & lifetime) for small explosions.
    scale=0.5 -> ~50% radius, 50% lifetime (after size-based adjustment).
    """
    def __init__(self, batch, x, y, base_color, group, scale=1.0):
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(140 * 0.4286, 380 * 0.4286)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.x = x
        self.y = y
        self.life = random.uniform(1.2 * 1.4, 2.4 * 1.4)
        self.age = 0.0
        if base_color is None:
            base_color = (
                random.randint(120, 255),
                random.randint(120, 255),
                random.randint(120, 255)
            )
        # Random slight hue shift per particle
        def shift(c):
            return max(0, min(255, int(c + random.uniform(-40, 40))))
        color = tuple(shift(c) for c in base_color)
        base_radius = random.uniform(2.0, 6.0)
        radius = base_radius * scale
        self.shape = shapes.Circle(self.x, self.y, radius, color=color, batch=batch, group=group)
        self.radius = radius
        size_life_scale = 0.55 + (radius/6.0)*0.45  # radius=2 -> ~0.7, radius=6 -> 1.0
        self.life *= size_life_scale
        if scale != 1.0:
            # Additional explicit lifetime scaling to ensure ~50% shorter overall when requested
            self.life *= scale
        # Cache for later (avoid depending on shape internals for glitter spawn)
        self.batch = batch
        self.group = group
        self.color = color
        self.shape.opacity = 255
    # no glitter sink

    def update(self, dt):
        self.age += dt
        if self.age >= self.life:
            return False
        # Motion with drag + gravity
        drag = 0.92
        self.vx *= drag ** dt
        self.vy *= drag ** dt
        self.vy -= 110 * dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        # Prevent visually static tiny particles: if speed very low add jitter + accelerate fade
        speed_mag = (self.vx * self.vx + self.vy * self.vy) ** 0.5
        if speed_mag < 10:
            # slight random drift so they don't look frozen
            self.x += random.uniform(-18, 18) * dt
            self.y += random.uniform(-18, 18) * dt
            # age faster so they fade out sooner
            self.age += dt * 0.6
            # Extra accelerated fade for very tiny slow particles
            if self.radius < 3.0:
                self.age += dt * 0.6
        # If nearly stopped and very small, force quick termination window
        if self.radius < 3.0 and speed_mag < 8 and self.life - self.age > 0.25:
            self.life = self.age + 0.25
        self.shape.x = self.x
        self.shape.y = self.y
        # Color/opacity fade + slight twinkle
        fade = 1.0 - (self.age / self.life)
        twinkle = 0.85 + 0.15 * math.sin(self.age * 40 + id(self) % 10)
        self.shape.opacity = int(255 * fade * twinkle)
        return True

    def delete(self):
        if self.shape:
            self.shape.delete()
        self.shape = None


# Glitter particle class removed


class _SmokeParticle:
    """Soft expanding smoke puff used in trail and post‑explosion."""
    def __init__(self, batch, x, y, group):
        self.x = x; self.y = y
        self.life = random.uniform(0.4, 0.8)
        self.age = 0.0
        self.radius = random.uniform(2, 4)
        gray = random.randint(60, 110)
        self.shape = shapes.Circle(self.x, self.y, self.radius, color=(gray, gray, gray), batch=batch, group=group)
        self.shape.opacity = 140

    def update(self, dt):
        self.age += dt
        if self.age >= self.life:
            return False
        self.shape.radius = self.radius * (1.0 + 0.8 * (self.age / self.life))
        self.shape.y = self.y + 12 * (self.age / self.life)
        fade = 1.0 - (self.age / self.life)
        self.shape.opacity = int(140 * fade * 0.9)
        return True

    def delete(self):
        if self.shape:
            self.shape.delete()
        self.shape = None

class _EmberParticle:
    """Short-lived warm ember drifting downward after explosion."""
    def __init__(self, batch, x, y, group):
        angle = random.uniform(0, 2*math.pi)
        speed = random.uniform(30, 90)
        self.vx = math.cos(angle) * speed * 0.55  # slightly flattened radial
        self.vy = math.sin(angle) * speed * 0.85
        # Bias upwards slightly so they look like ejecta then fall
        self.vy += 60
        self.x = x
        self.y = y
        self.life = random.uniform(0.7, 1.3)
        self.age = 0.0
        # Warm ember color with slight variance
        base = random.choice([(255,160,60),(255,140,40),(255,180,80)])
        jitter = lambda c: max(0, min(255, c + random.randint(-25,25)))
        color = (jitter(base[0]), jitter(base[1]), jitter(base[2]))
        self.shape = shapes.Circle(self.x, self.y, random.uniform(1.6, 2.6), color=color, batch=batch, group=group)
        self.shape.opacity = 240

    def update(self, dt):
        self.age += dt
        if self.age >= self.life:
            return False
        # Gravity + mild drag
        self.vy -= 180 * dt
        self.vx *= (0.96 ** dt)
        self.vy *= (0.96 ** dt)
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.shape.x = self.x
        self.shape.y = self.y
        # Fade + cooling (reduce green/blue slightly over time)
        fade = 1.0 - (self.age / self.life)
        self.shape.opacity = int(240 * fade)
        if int(self.age * 20) % 4 == 0:  # subtle flicker
            r,g,b = self.shape.color
            self.shape.color = (r, max(0, int(g*0.97)), max(0, int(b*0.94)))
        return True

    def delete(self):
        if self.shape:
            self.shape.delete()
        self.shape = None
        
@register_emitter("fireworks", auto_spawn=False)
class FireworksEmitter:
    # Controlled exclusively by the Fireworks effect; do not auto-spawn on product creation.
    def __init__(self, batch, position, color=None, consume_callback=None, molecule=None):
        self.batch = batch
        self.group = RenderingOrder.charge
        self.x, self.y = position
        self.stage = 'rocket'
        # Target delta height (short, quick arc)
        self.rocket_height = random.uniform(400, 540)
        self.rocket_speed = random.uniform(240, 320)
        self.start_y = self.y
        self.target_y = self.start_y + self.rocket_height
        # Rocket visuals: body + nose + stripe + fins + flickering flame
        self.rocket_body = shapes.Rectangle(self.x-3.5, self.y, 7, 26, color=(235,235,240), batch=batch, group=self.group)
        # Subtle mid stripe (paint band)
        self.rocket_stripe = shapes.Rectangle(self.x-3.5, self.y+10, 7, 4, color=(190,0,0), batch=batch, group=self.group)
        # Nose cone (slightly taller)
        self.rocket_nose = shapes.Triangle(
            self.x-3.5, self.y+26,
            self.x+3.5, self.y+26,
            self.x, self.y+36,
            color=(255,90,60), batch=batch, group=self.group)
        # Initial flame + inner core (created / replaced every frame)
        self.rocket_flame = shapes.Triangle(
            self.x-4.5, self.y,
            self.x+4.5, self.y,
            self.x, self.y-12,
            color=(255,180,60), batch=batch, group=self.group)
        self.rocket_flame_core = shapes.Triangle(
            self.x-2.2, self.y,
            self.x+2.2, self.y,
            self.x, self.y-7,
            color=(255,240,200), batch=batch, group=self.group)
        # Fins (will be re-created on update for easy reposition)
        self.rocket_fin_left = shapes.Triangle(
            self.x-3.5, self.y+4,
            self.x-3.5, self.y-2,
            self.x-8.0, self.y+1,
            color=(200,200,210), batch=batch, group=self.group)
        self.rocket_fin_right = shapes.Triangle(
            self.x+3.5, self.y+4,
            self.x+3.5, self.y-2,
            self.x+8.0, self.y+1,
            color=(200,200,210), batch=batch, group=self.group)
        self.rocket_shapes = [
            self.rocket_body,
            self.rocket_stripe,
            self.rocket_nose,
            self.rocket_flame,
            self.rocket_flame_core,
            self.rocket_fin_left,
            self.rocket_fin_right,
        ]
        self.particles = []
        self._dead = False
        self.base_color = _parse_hex(color)
        # If no explicit color provided (molecule lacks emitterColor), we'll do a small classic explosion
        self._small_explosion = self.base_color is None
        self.consume_callback = consume_callback
        self.molecule = molecule
        # Flash effect created at explosion
        self.flash_shape = None
        self.flash_life = 0.25
        self.flash_age = 0.0
        # Shockwave ring
        self.shockwave = None
        self.shockwave_age = 0.0
        self.shockwave_life = 0.6
        # Trail (list of (shape, age, life))
        self.trail = []
        self._trail_spawn_acc = 0.0
        self.elapsed = 0.0  # total life (rocket phase)
        self.smoke_particles = []
        self.ember_particles = []

    def _start_explosion(self):
        cx = self.x
        cy = self.y
        if self.rocket_shapes:
            for s in self.rocket_shapes:
                s.delete()
            self.rocket_shapes = None
        self.stage = 'explosion'
        # Consume molecule now so disappearance coincides with explosion flash
        if self.consume_callback and self.molecule:
            self.consume_callback(self.molecule)
            self.molecule = None
        if self._small_explosion:
            # Classic small orange/yellow pop
            if self.base_color is None:
                self.base_color = random.choice([(255,180,60),(255,160,50),(255,200,90)])
            count = random.randint(20, 30)
            for _ in range(count):
                self.particles.append(_ExplosionParticle(self.batch, cx, cy, self.base_color, self.group, scale=0.5))
            # Few smoke puffs
            for _ in range(4):
                self.smoke_particles.append(_SmokeParticle(self.batch, cx + random.uniform(-8,8), cy + random.uniform(-8,8), self.group))
            # No ember secondary + no shockwave for small pop
            self.flash_shape = shapes.Circle(cx, cy, int(18 * 0.2), color=(255,255,255), batch=self.batch, group=self.group)
            self.flash_shape.opacity = 220
            self.shockwave = None
        else:
            # Larger, brighter explosion (colorful)
            count = random.randint(int(150 * 1.4), int(220 * 1.4))
            for _ in range(count):
                self.particles.append(_ExplosionParticle(self.batch, cx, cy, self.base_color, self.group))
            # Spawn initial smoke burst
            for _ in range(14):
                self.smoke_particles.append(_SmokeParticle(self.batch, cx + random.uniform(-12 * 0.6,12 * 0.6), cy + random.uniform(-12 * 0.6,12 * 0.6), self.group))
            # Ember secondary effect
            ember_count = random.randint(22, 34)
            for _ in range(ember_count):
                self.ember_particles.append(_EmberParticle(self.batch, cx, cy, self.group))
            # White flash circle
            self.flash_shape = shapes.Circle(cx, cy, int(34 * 0.6), color=(255,255,255), batch=self.batch, group=self.group)
            self.flash_shape.opacity = 255
            # Shockwave ring (thin circle simulated via two concentric circles fade)
            self.shockwave = shapes.Circle(cx, cy, 10, color=(255,255,255), batch=self.batch, group=self.group)
            self.shockwave.opacity = 180

    def update(self, dt):
        if self._dead:
            return False
        if self.stage == 'rocket':
            self.elapsed += dt
            self.y += self.rocket_speed * dt
            # Move rocket visuals
            if self.rocket_shapes:
                # Horizontal micro wobble for life-like flight; amplified for small explosions (3x)
                base_wobble = math.sin(self.elapsed * 17.0) * 0.9
                if self._small_explosion:
                    wobble = base_wobble * 3.0
                else:
                    wobble = base_wobble
                body_x = self.x + wobble
                # Update body & stripe
                self.rocket_body.x = body_x-3.5
                self.rocket_body.y = self.y
                self.rocket_stripe.x = body_x-3.5
                self.rocket_stripe.y = self.y+10
                # Recreate fins (simpler than per-vertex move)
                self.rocket_fin_left.delete(); self.rocket_fin_right.delete()
                self.rocket_fin_left = shapes.Triangle(
                    body_x-3.5, self.y+4,
                    body_x-3.5, self.y-2,
                    body_x-8.0, self.y+1,
                    color=(205,205,215), batch=self.batch, group=self.group)
                self.rocket_fin_right = shapes.Triangle(
                    body_x+3.5, self.y+4,
                    body_x+3.5, self.y-2,
                    body_x+8.0, self.y+1,
                    color=(205,205,215), batch=self.batch, group=self.group)
                # Nose (recreate for slight jitter highlight)
                self.rocket_nose.delete()
                self.rocket_nose = shapes.Triangle(
                    body_x-3.5, self.y+26,
                    body_x+3.5, self.y+26,
                    body_x, self.y+36,
                    color=(255, random.randint(70,100), random.randint(40,70)), batch=self.batch, group=self.group)
                # Flame (outer) + core (inner) flicker
                self.rocket_flame.delete(); self.rocket_flame_core.delete()
                flame_len = random.uniform(11, 19)
                flame_spread = random.uniform(3.5, 4.4)
                outer_color = random.choice([(255,200,80),(255,160,50),(255,220,120)])
                self.rocket_flame = shapes.Triangle(
                    body_x-flame_spread, self.y,
                    body_x+flame_spread, self.y,
                    body_x + random.uniform(-0.6,0.6), self.y - flame_len,
                    color=outer_color, batch=self.batch, group=self.group)
                core_len = flame_len * random.uniform(0.45,0.6)
                core_spread = flame_spread * 0.55
                self.rocket_flame_core = shapes.Triangle(
                    body_x-core_spread, self.y,
                    body_x+core_spread, self.y,
                    body_x + random.uniform(-0.3,0.3), self.y - core_len,
                    color=(255,240,200), batch=self.batch, group=self.group)
                # Replace entries in list (keep ordering for delete())
                # Indices: body(0), stripe(1), nose(2), flame(3), flame_core(4), fin_left(5), fin_right(6)
                self.rocket_shapes[2] = self.rocket_nose
                self.rocket_shapes[3] = self.rocket_flame
                self.rocket_shapes[4] = self.rocket_flame_core
                self.rocket_shapes[5] = self.rocket_fin_left
                self.rocket_shapes[6] = self.rocket_fin_right
                # Opacity flicker
                self.rocket_flame.opacity = random.randint(150,255)
                self.rocket_flame_core.opacity = random.randint(180,255)
            # Spawn small fading trail dots
            self._trail_spawn_acc += dt
            if self._trail_spawn_acc >= 0.025 and self.rocket_shapes:
                self._trail_spawn_acc = 0.0
                # Spark
                dot = shapes.Circle(self.x + random.uniform(-2,2), self.y-12, random.uniform(2.2,3.2), color=(255, random.randint(120,200), 50), batch=self.batch, group=self.group)
                dot.opacity = 200
                self.trail.append((dot, 0.0, 0.35))
                # Smoke puff (slower fade)
                if random.random() < 0.6:
                    self.smoke_particles.append(_SmokeParticle(self.batch, self.x + random.uniform(-4,4), self.y-14, self.group))
            # Trail update
            new_trail = []
            for shape, age, life in self.trail:
                age += dt
                fade = 1.0 - (age / life)
                if fade > 0:
                    shape.opacity = int(160 * fade)
                    shape.y -= 30 * dt
                    new_trail.append((shape, age, life))
                else:
                    shape.delete()
            self.trail = new_trail
            # Explosion condition: reached target OR timeout fallback
            if self.y >= self.target_y or self.elapsed >= 1.2:
                self._start_explosion()
        elif self.stage == 'explosion':
            alive = []
            for p in self.particles:
                if p.update(dt):
                    alive.append(p)
                else:
                    p.delete()
            self.particles = alive
            # Smoke update
            smoke_alive = []
            for s in self.smoke_particles:
                if s.update(dt):
                    smoke_alive.append(s)
                else:
                    s.delete()
            self.smoke_particles = smoke_alive
            # Ember update
            ember_alive = []
            for e in self.ember_particles:
                if e.update(dt):
                    ember_alive.append(e)
                else:
                    e.delete()
            self.ember_particles = ember_alive
            # Flash fade
            if self.flash_shape:
                self.flash_age += dt
                fade = 1.0 - (self.flash_age / self.flash_life)
                if fade <= 0:
                    self.flash_shape.delete()
                    self.flash_shape = None
                else:
                    self.flash_shape.opacity = int(255 * fade)
            # Shockwave expansion
            if self.shockwave:
                self.shockwave_age += dt
                progress = self.shockwave_age / self.shockwave_life
                if progress >= 1.0:
                    self.shockwave.delete()
                    self.shockwave = None
                else:
                    # Scaled final radius (60% of previous 180 -> 108)
                    self.shockwave.radius = 10 + 108 * progress
                    self.shockwave.opacity = int(180 * (1.0 - progress))
            if (not self.particles and not self.flash_shape and not self.shockwave and not self.smoke_particles and not self.ember_particles):
                self._dead = True
        return not self._dead

    def delete(self):
        if self.rocket_shapes:
            for s in self.rocket_shapes:
                s.delete()
        for shape, _, _ in self.trail:
            shape.delete()
        for p in self.particles:
            p.delete()
        for s in self.smoke_particles:
            s.delete()
        for e in self.ember_particles:
            e.delete()
        if self.flash_shape:
            self.flash_shape.delete()
        if self.shockwave:
            self.shockwave.delete()
        self.particles = []
        self._dead = True
