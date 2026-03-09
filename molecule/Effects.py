# Molecule - a chemical reaction puzzle game
# Copyright (C) 2013 Simon Norberg <simon@pthread.se>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from collections.abc import Callable
import glob
import random
import time
import math
import pyglet
import pymunk
from collections import OrderedDict
from molecule import Config
from molecule import CollisionTypes
from molecule import pyglet_util
from molecule import RenderingOrder
from molecule import Gui
from libreact import Reaction
from libcml import Cml

Vec2 = tuple[float, float]
InventoryMap = OrderedDict[str, int]


class Effect:
    """Effect base class, act as a sensor"""
    def __init__(
        self,
        space: object | None = None,
        width: float | None = None,
        height: float | None = None,
        pos: Vec2 | None = None,
        name: str | None = None,
    ) -> None:
        self.name = name
        if width != None:
            self.width = width
        if height != None:
            self.height = height
        self.init_chipmunk(space, pos)
        if pos != None:
            self.set_pos(pos)
        self.supported_attributes = list()

    def set_pos(self, pos: Vec2) -> None:
        self.shape.body.position = pos
        x, y = self.shape.body.position
        self.x = x - self.width/2
        self.y = y - self.height/2

    def init_chipmunk(self, space: object, pos: Vec2 | None) -> None:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body, (self.width,self.height))
        self.shape = shape
        self.shape.collision_type = CollisionTypes.EFFECT
        self.shape.sensor = True
        self.shape.effect = self
        self.shape.filter = CollisionTypes.EFFECT_FILTER
        space.add(shape, body)

    def clicked(self, pos: Vec2) -> bool:
        return self.inside(pos)

    def inside(self, pos: Vec2) -> bool:
        bp = self.shape.body.position
        position = (bp.x - self.width / 2, bp.y - self.height / 2)
        return pos_inside(pos, position, self.width, self.height)

    def supports(self, attribute: str) -> bool:
        return attribute in self.supported_attributes

    def update(self) -> None:
        pass

    def react(self, element: object) -> None:
        pass

    def on_click(self, callback: Callable[..., None] | None = None) -> None:
        pass

    def on_release(self, callback: Callable[..., None] | None = None) -> None:
        pass

    def clamp_pos(self, pos: Vec2) -> Vec2:
        """Clamp position to be inside the effect, if possible"""
        return pos


class EffectSprite(pyglet.sprite.Sprite, Effect):
    """Effect base class + sprite"""
    def __init__(self, space: object, batch: object, pos: Vec2, img_path: str, name: str) -> None:
        group = RenderingOrder.background
        img = pyglet_util.load_image(img_path)
        pyglet.sprite.Sprite.__init__(self, img, batch=batch, group=group)
        Effect.__init__(self, space = space, name = name, pos = pos)


class Action(EffectSprite):
    def __init__(self, space: object, batch: object, pos: Vec2, img_path: str, name: str) -> None:
        EffectSprite.__init__(self, space, batch, pos, img_path, name)
        self.supported_attributes.append("action")
        self.is_clicked = False
        self.callback: Callable[..., None] | None = None

class Temperature(EffectSprite):
    def __init__(self, space: object, batch: object, pos: Vec2, img_path: str, name: str, temp: float) -> None:
        EffectSprite.__init__(self, space, batch, pos, img_path, name)
        if temp is None:
            raise Exception("Temperature must be specified for effect: " + name)
        self.temp = temp
        self.supported_attributes.append("temp")
        self.supported_attributes.append("reaction")

class Fire(Temperature):
    """Fire effect"""
    def __init__(self, space: object, batch: object, pos: Vec2, temp: float = 1000) -> None:
        Temperature.__init__(self, space, batch, pos, "fire.png", "Fire", temp)

class Cold(Temperature):
    """Cold effect"""
    def __init__(self, space: object, batch: object, pos: Vec2, temp: float = 250) -> None:
        Temperature.__init__(self, space, batch, pos, "cold.png", "Cold", temp)

class EnergySource(EffectSprite):
    """EnergySource effect"""
    def __init__(self, space: object, batch: object, pos: Vec2, img_path: str, name: str, energy_source: object) -> None:
        EffectSprite.__init__(self, space, batch, pos, img_path, name)
        self.energy_source = energy_source
        self.supported_attributes.append("energy_source")
        self.supported_attributes.append("reaction")

class UvLight(EnergySource):
    """UvLight effect"""
    def __init__(self, space: object, batch: object, pos: Vec2) -> None:
        EnergySource.__init__(self, space, batch, pos, "uv-light.png", "UvLight", Cml.Requirement.EnergyType.UV_LIGHT)

class Electrolysis(EnergySource):
    """Electrolysis effect"""
    def __init__(self, space: object, batch: object, pos: Vec2) -> None:
        EnergySource.__init__(self, space, batch, pos, "electrolysis-beaker.png", "Electrolysis", Cml.Requirement.EnergyType.ELECTROLYSIS)
        self.body = None
        self.space = space

    def clamp_pos(self, pos: Vec2) -> Vec2:
        """Clamp position to be inside the electrolysis beaker walls"""
        bp = self.shape.body.position
        # Internal wall bounds: left=-215, right=215, bottom=-255, top=255
        # Use a margin of 60 to account for possible jitter during product spawning (up to 50)
        margin = 60
        min_x = bp.x - 215 + margin
        max_x = bp.x + 215 - margin
        min_y = bp.y - 255 + margin
        max_y = bp.y + 255 - margin
        
        px, py = pos
        return (max(min_x, min(max_x, px)), max(min_y, min(max_y, py)))

    def init_chipmunk(self, space: object, pos: Vec2) -> None:
        static_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        static_body.position = pos
        
        # Relative dimensions from center (pos)
        left = -215
        right = 215
        bottom = -255
        top = 255
        thickness = 10

        # Creating walls relative to body position
        walls = [
            pymunk.Segment(static_body, (left, bottom), (left, top), thickness),  # Left wall
            pymunk.Segment(static_body, (left, bottom), (right, bottom), thickness),  # Bottom wall
            pymunk.Segment(static_body, (right, bottom), (right, top), thickness),  # Right wall
            pymunk.Segment(static_body, (left, top), (right, top), thickness),  # Top wall
        ]
        for wall in walls:
            wall.elasticity = 0.95
            wall.collision_type = CollisionTypes.WALL
            wall.filter = CollisionTypes.WALL_FILTER
        space.add(static_body, *walls)
        shape = pymunk.Poly.create_box(static_body, (430, 520), 5)
        space.add(shape) 
        self.shape = shape
        self.shape.collision_type = CollisionTypes.EFFECT
        self.shape.sensor = True
        self.shape.effect = self
        self.shape.filter = CollisionTypes.EFFECT_FILTER

    def set_pos(self, pos: Vec2) -> None:
        OFFSET_X, OFFSET_Y = 0,140
        self.shape.body.position = pos
        x, y = self.shape.body.position
        self.x = x - self.width/2 + OFFSET_X
        self.y = y - self.height/2 + OFFSET_Y

    def update(self) -> None:
        if not self.space:
            return
            
        if not hasattr(self, 'ion_joints'):
            self.ion_joints = {}

        # Find molecules inside the electrolysis area
        bp = self.shape.body.position
        # Electrolysis beaker is approx 430x520 box
        query_rect = pymunk.Poly.create_box(None, (430, 520))
        query_rect.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        query_rect.body.position = bp

        bb = query_rect.cache_bb()
        query = self.space.bb_query(bb, pymunk.ShapeFilter(categories=CollisionTypes.ELEMENT))
        
        valid_mols = set()
        for shape in query:
            if shape.collision_type != CollisionTypes.ELEMENT:
                continue
            mol = shape.molecule
            if mol in valid_mols:
                continue

            # Check if inside logically
            if not self.inside(shape.body.position):
                continue
                
            # Only affect aqueous state molecules
            if mol.current_state.short != "aq":
                continue
                
            if mol.charge == 0:
                continue
                
            valid_mols.add(mol)

        # Clean up joints for molecules that are deleted or left the valid area
        mols_to_remove = []
        for mol, joints in self.ion_joints.items():
            if mol.is_deleted() or mol not in valid_mols:
                for atom, spring, target_x in joints:
                    try:
                        self.space.remove(spring)
                    except:
                        pass
                mols_to_remove.append(mol)
            else:
                # Keep the spring pulling purely horizontally
                for atom, spring, target_x in joints:
                    spring.anchor_b = (target_x, atom.body.position.y)

        for mol in mols_to_remove:
            del self.ion_joints[mol]
            
        # Create springs for new molecules
        for mol in valid_mols:
            if mol not in self.ion_joints:
                joints = []
                charge = mol.charge
                # Cations (+) to left, Anions (-) to right based on image
                # Beaker physics box width is 430, so edges are at offset 215
                target_x = bp.x - 215 + 20 if charge > 0 else bp.x + 215 - 20
                
                target_atom = None
                for atom in mol.atoms.values():
                    if (charge > 0 and atom.charge > 0) or (charge < 0 and atom.charge < 0):
                        target_atom = atom
                        break
                if not target_atom:
                    target_atom = list(mol.atoms.values())[0]
                    
                spring = pymunk.DampedSpring(target_atom.body, self.space.static_body, 
                                             (0,0), (target_x, target_atom.body.position.y), 
                                             rest_length=0, stiffness=100, damping=20)
                self.space.add(spring)
                joints.append((target_atom, spring, target_x))
                self.ion_joints[mol] = joints

class WaterBeaker(EffectSprite):
    """WaterBeaker"""
    def __init__(self, space: object, batch: object, pos: Vec2) -> None:
        EffectSprite.__init__(self, space, batch, pos, "water-beaker.png","Water Beaker")
        self.supported_attributes.append("reaction")
        self.supported_attributes.append("action")
        self.is_clicked = False
        self.body = None

    def clamp_pos(self, pos: Vec2) -> Vec2:
        """Clamp position to be inside the water beaker walls"""
        bp = self.shape.body.position
        # Internal wall bounds: left=-280, right=285, bottom=-320, top=340
        # Use a margin of 60 to account for possible jitter during product spawning (up to 50)
        margin = 60
        min_x = bp.x - 280 + margin
        max_x = bp.x + 285 - margin
        min_y = bp.y - 320 + margin
        max_y = bp.y + 340 - margin
        
        px, py = pos
        return (max(min_x, min(max_x, px)), max(min_y, min(max_y, py)))

    def init_chipmunk(self, space: object, pos: Vec2) -> None:
        static_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        x, y = pos
        # Rectangle dimensions
        left_x = x - 280
        right_x = x + 285
        bottom_y = y - 320
        top_y = y + 340
        thickness = 10

        # Creating walls with clearer structure
        walls = [
            pymunk.Segment(static_body, (left_x, bottom_y), (left_x, top_y), thickness),  # Left wall
            pymunk.Segment(static_body, (left_x, bottom_y), (right_x, bottom_y), thickness),  # Bottom wall
            pymunk.Segment(static_body, (right_x, bottom_y), (right_x, top_y), thickness),  # Right wall
            pymunk.Segment(static_body, (left_x, top_y), (right_x, top_y), thickness),  # Top wall
        ]
        for wall in walls:
            wall.elasticity = 0.95
            wall.collision_type = CollisionTypes.WALL
            wall.filter = CollisionTypes.WALL_FILTER
        space.add(static_body, *walls)
        shape = pymunk.Poly.create_box(static_body, (570,630), 5)
        shape.body.position = pos
        space.add(shape) 
        self.shape = shape
        self.shape.collision_type = CollisionTypes.EFFECT
        self.shape.sensor = True
        self.shape.effect = self
        self.shape.filter = CollisionTypes.EFFECT_FILTER

    def set_pos(self, pos: Vec2) -> None:
        OFFSET_X, OFFSET_Y = 0,60
        self.shape.body.position = pos
        x, y = self.shape.body.position
        self.x = x - self.width/2 + OFFSET_X
        self.y = y - self.height/2 + OFFSET_Y

    def react(self, molecule: object) -> object | None:
        ions = molecule.to_aqueous()
        if ions != None and len(ions) > 0:
            print(molecule.formula, "-(Water)>", ions)
            cml = Cml.Reaction([molecule.formula],ions)
            reaction = Reaction.Reaction(cml,[molecule.state_formula])
            return reaction
        elif Config.current.DEBUG:
            print("Water beaker didnt react with:", molecule.formula)
        return None

    def on_click(self, callback: Callable[..., None]) -> None:
        print("Water beaker clicked")

class InertSolventBeaker(EffectSprite):
    """InertSolventBeaker"""
    def __init__(self, space: object, batch: object, pos: Vec2) -> None:
        EffectSprite.__init__(self, space, batch, pos, "inert-solvent-beaker.png","Inert Solvent Beaker")
        self.body = None

    def init_chipmunk(self, space: object, pos: Vec2) -> None:
        static_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        x, y = pos
        # Rectangle dimensions
        left_x = x - 280
        right_x = x + 285
        bottom_y = y - 320
        top_y = y + 340
        thickness = 10

        # Creating walls with clearer structure
        walls = [
            pymunk.Segment(static_body, (left_x, bottom_y), (left_x, top_y), thickness),  # Left wall
            pymunk.Segment(static_body, (left_x, bottom_y), (right_x, bottom_y), thickness),  # Bottom wall
            pymunk.Segment(static_body, (right_x, bottom_y), (right_x, top_y), thickness),  # Right wall
            pymunk.Segment(static_body, (left_x, top_y), (right_x, top_y), thickness),  # Top wall
        ]
        for wall in walls:
            wall.elasticity = 0.95
            wall.collision_type = CollisionTypes.WALL
            wall.filter = CollisionTypes.WALL_FILTER
        space.add(static_body, *walls)
        shape = pymunk.Poly.create_box(static_body, (570,630), 5)
        shape.body.position = pos
        space.add(shape)
        self.shape = shape
        self.shape.collision_type = CollisionTypes.EFFECT
        self.shape.sensor = True
        self.shape.effect = self
        self.shape.filter = CollisionTypes.EFFECT_FILTER

    def set_pos(self, pos: Vec2) -> None:
        OFFSET_X, OFFSET_Y = 0,60
        self.shape.body.position = pos
        x, y = self.shape.body.position
        self.x = x - self.width/2 + OFFSET_X
        self.y = y - self.height/2 + OFFSET_Y

class HotplateBeaker(EffectSprite):
    """HotplateBeaker"""
    def __init__(self, space: object, batch: object, pos: Vec2, temp: float = 100) -> None:
        EffectSprite.__init__(self, space, batch, pos, "hotplate.png","Hotplate Beaker")
        self.supported_attributes.append("reaction")
        self.supported_attributes.append("temp")
        self.temp = temp
        self.is_clicked = False
        self.body = None

    def init_chipmunk(self, space: object, pos: Vec2) -> None:
        static_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        x, y = pos
        # Rectangle dimensions
        left_x = x - 300
        right_x = x + 305
        bottom_y = y - 265
        top_y = y + 270
        thickness = 10

        # Creating walls with clearer structure
        walls = [
            pymunk.Segment(static_body, (left_x, bottom_y), (left_x, top_y), thickness),  # Left wall
            pymunk.Segment(static_body, (left_x, bottom_y), (right_x, bottom_y), thickness),  # Bottom wall
            pymunk.Segment(static_body, (right_x, bottom_y), (right_x, top_y), thickness),  # Right wall
            pymunk.Segment(static_body, (left_x, top_y), (right_x, top_y), thickness),  # Top wall
        ]
        for wall in walls:
            wall.elasticity = 0.95
            wall.collision_type = CollisionTypes.WALL
            wall.filter = CollisionTypes.WALL_FILTER
        space.add(static_body, *walls)
        shape = pymunk.Poly.create_box(static_body, (600,530), 5)
        shape.body.position = pos
        space.add(shape)
        self.shape = shape
        self.shape.collision_type = CollisionTypes.EFFECT
        self.shape.sensor = True
        self.shape.effect = self
        self.shape.filter = CollisionTypes.EFFECT_FILTER

    def set_pos(self, pos: Vec2) -> None:
        OFFSET_X, OFFSET_Y = 0,-70
        self.shape.body.position = pos
        x, y = self.shape.body.position
        self.x = x - self.width/2 + OFFSET_X
        self.y = y - self.height/2 + OFFSET_Y

    def react(self, molecule: object) -> object | None:
        ions = molecule.to_aqueous()
        if ions != None and len(ions) > 0:
            print(molecule.formula, "-(Water)>", ions)
            cml = Cml.Reaction([molecule.formula],ions)
            reaction = Reaction.Reaction(cml,[molecule.state_formula])
            return reaction
        elif Config.current.DEBUG:
            print("HotplateBeaker didnt react with:", molecule.formula)
        return None

class Furnace(EffectSprite):
    """Furnace"""
    def __init__(self, space: object, batch: object, pos: Vec2, temp: float = 100) -> None:
        EffectSprite.__init__(self, space, batch, pos, "furnace.png","Furnace")
        self.supported_attributes.append("temp")
        self.supported_attributes.append("reaction")
        self.temp = temp
        self.is_clicked = False
        self.body = None

    def init_chipmunk(self, space: object, pos: Vec2) -> None:
        static_body = pymunk.Body(body_type=pymunk.Body.STATIC)
        x, y = pos
        # Rectangle dimensions
        left_x = x - 160
        right_x = x + 160
        bottom_y = y - 140
        top_y = y + 150
        thickness = 10

        # Creating walls with clearer structure
        walls = [
            pymunk.Segment(static_body, (left_x, bottom_y), (left_x, top_y), thickness),  # Left wall
            pymunk.Segment(static_body, (left_x, bottom_y), (right_x, bottom_y), thickness),  # Bottom wall
            pymunk.Segment(static_body, (right_x, bottom_y), (right_x, top_y), thickness),  # Right wall
            pymunk.Segment(static_body, (left_x, top_y), (right_x, top_y), thickness),  # Top wall
        ]
        for wall in walls:
            wall.elasticity = 0.95
            wall.collision_type = CollisionTypes.WALL
            wall.filter = CollisionTypes.WALL_FILTER
        space.add(static_body, *walls)
        shape = pymunk.Poly.create_box(static_body, (305,280), 5)
        shape.body.position = pos
        space.add(shape)
        self.shape = shape
        self.shape.collision_type = CollisionTypes.EFFECT
        self.shape.sensor = True
        self.shape.effect = self
        self.shape.filter = CollisionTypes.EFFECT_FILTER

    def set_pos(self, pos: Vec2) -> None:
        OFFSET_X, OFFSET_Y = 5,-30
        self.shape.body.position = pos
        x, y = self.shape.body.position
        self.x = x - self.width/2 + OFFSET_X
        self.y = y - self.height/2 + OFFSET_Y

class Fireworks(EffectSprite):
    """Fireworks ignition effect.

    Behavior:
      - After a molecule has dwelled 1s (handled in Level.effect_reaction timing)
        the fuse is considered lit. We then start an internal timer (2s) after
        which a fireworks emitter is spawned at the effect position using the
        molecule state's optional emitter color (falling back to white).
      - Non-reactive: doesn't alter chemistry (no reaction), purely visual.
    """
    FUSE_TIME = 1.0  # already enforced by dwell system, kept for clarity
    ROCKET_TIME = 1.2  # shorter internal fuse for snappier feedback
    def __init__(
        self,
        space: object,
        batch: object,
        pos: Vec2,
        emitters_ref: list[object],
        consume_callback: Callable[[object], None] | None,
    ) -> None:
        EffectSprite.__init__(self, space, batch, pos, "fireworks.png", "Fireworks")
        self._active_fuse: tuple[object, float] | None = None  # (molecule, start_time)
        self._pending_launches: list[tuple[float, str | None]] = []  # list of (launch_time, color)
        self.batch = batch
        self.emitters_ref = emitters_ref  # direct list reference
        self.consume_callback = consume_callback
        self._pulse_dir = 1
        self._last_pulse = time.time()
        # Mark as put-capable so Level/Inventory can call put_element
        self.supported_attributes.append("put")
        self._pending_victory: object | None = None  # (molecule) to be added after explosion


    def put_element(self, molecule: object) -> bool:
        # Only allow one active rocket at a time
        if self._active_fuse is not None or self._pending_victory is not None:
            return False
        self._active_fuse = (molecule, time.time())
        if Config.current.DEBUG:
            print("Fireworks fuse lit for", molecule.formula)
        return True

    def update(self) -> None:
        now = time.time()
        # Promote active fuse to pending launch after ROCKET_TIME
        if self._active_fuse is not None:
            molecule, start = self._active_fuse
            elapsed = now - start
            if elapsed >= self.ROCKET_TIME:
                color_hex = getattr(molecule.current_state, 'emitter_color', None)
                # Spawn emitter, pass callback for explosion
                from molecule.emitters import Emitters
                emitter = Emitters.spawn_emitter(
                    "fireworks", self.batch, self.shape.body.position,
                    color=color_hex, consume_callback=self._on_explosion, molecule=molecule
                )
                if emitter is not None:
                    self.emitters_ref.append(emitter)
                self._active_fuse = None
                self.opacity = 255
                if Config.current.DEBUG:
                    print("Fireworks launching rocket for", molecule.formula)
            else:
                # Strong pulse: sine based between 110 and 255
                phase = (elapsed / self.ROCKET_TIME) * 3.14159  # 0..pi
                opacity = int(110 + (255-110) * abs(math.sin(phase)))
                self.opacity = opacity

        # If explosion finished, add molecule to VictoryInventory
        if self._pending_victory is not None:
            molecule = self._pending_victory
            # Find VictoryInventory effect and put molecule
            for area in getattr(self, 'areas', []):
                if hasattr(area, 'put_element') and 'victory' in getattr(area, 'supported_attributes', []):
                    area.put_element(molecule)
                    if Config.current.DEBUG:
                        print("Fireworks: molecule added to VictoryInventory", molecule.formula)
                    break
            self._pending_victory = None

    def _on_explosion(self, molecule: object) -> None:
        # Called by emitter when explosion/fade is done
        if self.consume_callback:
            self.consume_callback(molecule)

class Mining(Action):
    ACTION_TIME = 3
    FRAME_DURATION = 5
    def __init__(self, space: object, batch: object, pos: Vec2, mineral_list: list[str]) -> None:
        Action.__init__(self, space, batch, pos,
                        "mining_animation/frame_0000.png","mining")
        self.mineral_list = mineral_list
        self.timer: float | None = None
        self.current_frame = 0
        self.current_frame_duration = self.FRAME_DURATION
        self.frames = list()
        for img in sorted(glob.glob("img/mining_animation/frame_*")):
            self.frames.append(pyglet_util.load_image(img.split("img/")[1]))

    def update(self) -> None:
        if self.timer:
            self.switch_frame()
        if self.timer and self.timer < time.time():
            self.perform_callback()
            self.timer = None

    def switch_frame(self) -> None:
        self.current_frame_duration -= 1
        if self.current_frame_duration == 0:
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.current_frame = 0
            self.image = self.frames[self.current_frame]
            self.current_frame_duration = self.FRAME_DURATION

    def perform_callback(self) -> None:
            mineral = random.choice(self.mineral_list)
            if self.callback is not None:
                self.callback(mineral)

    def on_click(self, callback: Callable[[str], None]) -> None:
        self.is_clicked = True
        self.callback = callback
        self.timer = time.time() + self.ACTION_TIME

    def on_release(self, callback: Callable[..., None] | None = None) -> None:
        self.is_clicked = False
        self.timer = None
        self.image = self.frames[0]



class Inventory(Effect):
    def __init__(
        self,
        space: object,
        pos: Vec2,
        name: str,
        width: float,
        height: float,
        content: list[str] | None = None,
        capacity: int = 0,
        gui_container: object | None = None,
        create_element_callback: Callable[[str, Vec2], None] | None = None,
        batch: object | None = None,
    ) -> None:
        Effect.__init__(self, space = space, pos = pos, width =
                width, height = height, name = name)
        self.batch = batch
        self.content = self.list_to_inventory(content or [])
        self.supported_attributes.append("get")
        self.supported_attributes.append("put")
        self.gui_container = gui_container
        self.create_element_callback = create_element_callback
        self.reload_gui()

    def put_element(self, element: object) -> bool:
        self.add_to_inventory(self.content, element.state_formula)
        self.reload_gui()
        return True

    def get_callback(self, button: object) -> None:
        if self.create_element_callback is None:
            return
        self.create_element_callback(button.element, (button.x, button.y))
        self.remove_element(button.element)
        # Always sync UI with inventory state to avoid inconsistencies
        self.reload_gui()

    def get_element(self, element: str, x: float, y: float) -> None:
        return None

    def list_to_inventory(self, inventory_list: list[str]) -> InventoryMap:
        inventory: InventoryMap = OrderedDict()
        for element in inventory_list:
            self.add_to_inventory(inventory, element)
        return inventory

    def add_to_inventory(self, inventory: InventoryMap, element: str) -> None:
        if element in inventory:
            inventory[element] += 1
        else:
            inventory[element] = 1

    def remove_element(self, element: str) -> None:
        if element not in self.content:
            return
        if self.content[element] == 1:
            self.content.pop(element)
        else:
            self.content[element] -= 1

    def reload_gui(self) -> None:
        if self.gui_container is None:
            return
        
        # Track which elements we have buttons for
        existing_buttons = {}
        for button in list(self.gui_container.children):
            if hasattr(button, 'element'):
                existing_buttons[button.element] = button

        # Update existing buttons and remove stale ones
        for element, button in list(existing_buttons.items()):
            if element in self.content:
                # Update count
                count = self.content[element]
                if button.count != count:
                    button.count = count
                    button.update_label()
            else:
                # Remove button
                self.gui_container.remove(button)
                del existing_buttons[element]

        # Add new buttons
        for element, count in self.content.items():
            if element not in existing_buttons:
                button = Gui.MoleculeButton(element, count, self.get_callback, batch=self.batch)
                self.gui_container.add(button)

class VictoryInventory(Inventory):
    def __init__(self, space: object, pos: Vec2, name: str, width: float, height: float, victory_condition: list[str]) -> None:
        Inventory.__init__(self, space, pos, name, width, height)
        self.victory_condition = self.list_to_inventory(victory_condition)
        self.supported_attributes.append("put")
        self.supported_attributes.append("victory")

    def put_element(self, element: object) -> bool:
        element = element.formula
        if element in self.victory_condition:
            if self.victory_condition_fullfilled(element):
                return False
            else:
                self.add_to_inventory(self.content, element)
                return True
        return False

    def victory_condition_fullfilled(self, element: str) -> bool:
        needed = self.victory_condition[element]
        if element in self.content:
            return needed <= self.content[element]
        return False

    def progress_text(self) -> str:
        progress = ""
        for element, victory_count in self.victory_condition.items():
            if len(progress) != 0:
                progress += " "
            current_count = 0
            if element in self.content:
                current_count = self.content[element]
            progress += "%d/%d %s" % (current_count,victory_count, element)

        return progress

    def victory(self) -> bool:
        for element in self.victory_condition:
            if not self.victory_condition_fullfilled(element):
                return False
        return True


def pos_inside(pos: Vec2, rec_pos: Vec2, rec_width: float, rec_height: float) -> bool:
    x, y = pos
    rec_x, rec_y = rec_pos
    rec_X = rec_x + rec_width
    rec_Y = rec_y + rec_height
    return between(x, rec_x, rec_X) and between(y, rec_y, rec_Y)

def between(a: float, b: float, B: float) -> bool:
    return a >= b and a <= B

def create_effects(
    space: object,
    batch: object,
    effects: list[object],
    emitters: list[object],
    consume_molecule_cb: Callable[[object], None] | None,
) -> list[Effect]:
    new_effects: list[Effect] = []
    for effect in effects:
        x = effect.x2
        y = effect.y2
        value = effect.value
        molecules = effect.molecules
        if effect.title == "Fire":
            fire = Fire(space, batch, (x,y), value)
            new_effects.append(fire)
        elif effect.title == "Cold":
            cold = Cold(space, batch, (x,y), value)
            new_effects.append(cold)
        elif effect.title == "WaterBeaker":
            water = WaterBeaker(space, batch, (x, y))
            new_effects.append(water)
        elif effect.title == "InertSolventBeaker":
            inertSolvedBeaker = InertSolventBeaker(space, batch, (x, y))
            new_effects.append(inertSolvedBeaker)
        elif effect.title == "HotplateBeaker":
            hotplate_beaker = HotplateBeaker(space, batch, (x, y), value)
            new_effects.append(hotplate_beaker)
        elif effect.title == "Furnace":
            furnace = Furnace(space, batch, (x, y), value)
            new_effects.append(furnace)
        elif effect.title == "Mining":
            mining = Mining(space, batch, (x, y), molecules)
            new_effects.append(mining)
        elif effect.title == "UvLight":
            uv_light = UvLight(space, batch, (x, y))
            new_effects.append(uv_light)
        elif effect.title == "Electrolysis":
            electrolysis = Electrolysis(space, batch, (x, y))
            new_effects.append(electrolysis)
        elif effect.title == "Fireworks":
            fireworks = Fireworks(space, batch, (x, y), emitters, consume_molecule_cb)
            new_effects.append(fireworks)
        else:
            raise Exception("Effect not implemented:" + effect.title)

    return new_effects
