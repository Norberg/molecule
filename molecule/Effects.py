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
import glob
import random
import time
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


class Effect:
    """Effect base class, act as a sensor"""
    def __init__(self, space = None, width = None, height = None, pos = None,
            name = None):
        self.name = name
        if width != None:
            self.width = width * Config.current.zoom
        if height != None:
            self.height = height * Config.current.zoom
        self.init_chipmunk(space, pos)
        if pos != None:
            self.set_pos(pos)
        self.supported_attributes = list()

    def set_pos(self, pos):
        self.shape.body.position = pos
        x, y = self.shape.body.position
        self.x = x - self.width/2
        self.y = y - self.height/2

    def init_chipmunk(self,space, pos):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body, (self.width,self.height))
        self.shape = shape
        self.shape.collision_type = CollisionTypes.EFFECT
        self.shape.sensor = True
        self.shape.effect = self
        space.add(shape, body)

    def clicked(self, pos):
        return self.inside(pos)

    def inside(self, pos):
        bp = self.shape.body.position
        position = (bp.x - self.width / 2, bp.y - self.height / 2)
        return pos_inside(pos, position, self.width, self.height)

    def supports(self, attribute):
        return attribute in self.supported_attributes

    def update(self):
        pass

    def react(self, element):
        pass

    def on_click(self, callback = None):
        pass

    def on_release(self, callback = None):
        pass


class EffectSprite(pyglet.sprite.Sprite, Effect):
    """Effect base class + sprite"""
    def __init__(self, space, batch, pos, img_path, name):
        group = RenderingOrder.background
        img = pyglet_util.load_image(img_path)
        pyglet.sprite.Sprite.__init__(self, img, batch=batch, group=group)
        Effect.__init__(self, space = space, name = name, pos = pos)


class Action(EffectSprite):
    def __init__(self, space, batch, pos, img_path, name):
        EffectSprite.__init__(self, space, batch, pos, img_path, name)
        self.supported_attributes.append("action")
        self.is_clicked = False
        self.callback = None

class Temperature(EffectSprite):
    def __init__(self, space, batch, pos, img_path, name, temp):
        EffectSprite.__init__(self, space, batch, pos, img_path, name)
        self.temp = temp
        self.supported_attributes.append("temp")
        self.supported_attributes.append("reaction")

class Fire(Temperature):
    """Fire effect"""
    def __init__(self, space, batch, pos, temp=1000):
        Temperature.__init__(self, space, batch, pos, "fire.png", "Fire", temp)

class Cold(Temperature):
    """Cold effect"""
    def __init__(self, space, batch, pos, temp=250):
        Temperature.__init__(self, space, batch, pos, "cold.png", "Cold", temp)

class WaterBeaker(EffectSprite):
    """WaterBeaker"""
    def __init__(self, space, batch, pos):
        EffectSprite.__init__(self, space, batch, pos, "water-beaker.png","Water Beaker")
        self.supported_attributes.append("reaction")
        self.supported_attributes.append("action")
        self.is_clicked = False
        self.body = None

    def init_chipmunk(self,space, pos):
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
            wall.layers = CollisionTypes.LAYER_WALL
        space.add(static_body, *walls)
        shape = pymunk.Poly.create_box(static_body, (570,630), 5)
        shape.body.position = pos
        space.add(shape)
        self.shape = shape
        self.shape.collision_type = CollisionTypes.EFFECT
        self.shape.sensor = True
        self.shape.effect = self

    def set_pos(self, pos):
        OFFSET_X, OFFSET_Y = 0,60
        self.shape.body.position = pos
        x, y = self.shape.body.position
        self.x = x - self.width/2 + OFFSET_X
        self.y = y - self.height/2 + OFFSET_Y

    def react(self, molecule):
        ions = molecule.to_aqueous()
        if ions != None and len(ions) > 0:
            print(molecule.formula, "-(Water)>", ions)
            cml = Cml.Reaction([molecule.formula],ions)
            reaction = Reaction.Reaction(cml,[molecule.state_formula])
            return reaction
        elif Config.current.DEBUG:
            print("Water beaker didnt react with:", molecule.formula)

    def on_click(self, callback):
        print("Water beaker clicked")

class Mining(Action):
    ACTION_TIME = 3
    FRAME_DURATION = 5
    def __init__(self, space, batch, pos, mineral_list):
        Action.__init__(self, space, batch, pos,
                        "mining_animation/frame_0000.png","mining")
        self.mineral_list = mineral_list
        self.timer = None
        self.current_frame = 0
        self.current_frame_duration = self.FRAME_DURATION
        self.frames = list()
        for img in sorted(glob.glob("img/mining_animation/frame_*")):
            self.frames.append(pyglet_util.load_image(img.split("img/")[1]))

    def update(self):
        if self.timer:
            self.switch_frame()
        if self.timer and self.timer < time.time():
            self.perform_callback()
            self.timer = None

    def switch_frame(self):
        self.current_frame_duration -= 1
        if self.current_frame_duration == 0:
            self.current_frame += 1
            if self.current_frame >= len(self.frames):
                self.current_frame = 0
            self.image = self.frames[self.current_frame]
            self.current_frame_duration = self.FRAME_DURATION

    def perform_callback(self):
            mineral = random.choice(self.mineral_list)
            self.callback(mineral)

    def on_click(self, callback):
        self.is_clicked = True
        self.callback = callback
        self.timer = time.time() + self.ACTION_TIME

    def on_release(self, callback = None):
        self.is_clicked = False
        self.timer = None
        self.image = self.frames[0]



class Inventory(Effect):
    def __init__(self, space, pos, name, width, height, content = [],
            capacity = 0, gui_container = None, create_element_callback = None):
        Effect.__init__(self, space = space, pos = pos, width =
                width, height = height, name = name)
        self.content = self.list_to_inventory(content)
        self.supported_attributes.append("get")
        self.supported_attributes.append("put")
        self.gui_container = gui_container
        self.create_element_callback = create_element_callback
        self.reload_gui()

    def put_element(self, element):
        self.add_to_inventroy(self.content, element.state_formula)
        self.reload_gui()
        return True

    def get_callback(self, button):
        self.create_element_callback(button.element, (button.x, button.y))
        self.remove_element(button.element)
        if button.count > 1:
            button.count -= 1
            button.update_label()
        else:
            self.gui_container.remove(button)

    def get_element(self, element, x, y):
        return None

    def list_to_inventory(self, inventory_list):
        inventory = OrderedDict()
        for element in inventory_list:
            self.add_to_inventroy(inventory, element)
        return inventory

    def add_to_inventroy(self, inventory, element):
        if element in inventory:
            inventory[element] += 1
        else:
            inventory[element] = 1

    def remove_element(self, element):
        if self.content[element] == 1:
            self.content.pop(element)
        else:
            self.content[element] -= 1

    def reload_gui(self):
        if self.gui_container is None:
            return
        gui_elements = list()
        #Update existing elements
        index = 0
        for button in list(self.gui_container.content):
            element = button.element
            count = self.content[button.element]
            if (element in self.content.keys() and
                button.count != count):
                new_btn = Gui.MoleculeButton(element, count, self.get_callback)
                self.gui_container.remove(button)
                offset =len(self.gui_container.content)
                self.gui_container.add(new_btn, offset - index)
            if element not in self.content.keys():
                self.gui_container.remove(button)
            index += 1
            gui_elements.append(button.element)

        #Add new elements
        for element, count in self.content.items():
            if element in gui_elements:
                continue
            button = Gui.MoleculeButton(element, count, self.get_callback)
            self.gui_container.add(button)

class VictoryInventory(Inventory):
    def __init__(self, space, pos, name, width, height, victory_condition):
        Inventory.__init__(self, space, pos, name, width, height)
        self.victory_condition = self.list_to_inventory(victory_condition)
        self.supported_attributes.append("put")
        self.supported_attributes.append("victory")

    def put_element(self, element):
        element = element.formula
        if element in self.victory_condition:
            if self.victory_condition_fullfilled(element):
                return False
            else:
                self.add_to_inventroy(self.content, element)
                return True
        return False

    def victory_condition_fullfilled(self, element):
        needed = self.victory_condition[element]
        if element in self.content:
            return needed <= self.content[element]
        return False

    def progress_text(self):
        progress = ""
        for element, victory_count in self.victory_condition.items():
            if len(progress) != 0:
                progress += " "
            current_count = 0
            if element in self.content:
                current_count = self.content[element]
            progress += "%d/%d %s" % (current_count,victory_count, element)

        return progress

    def victory(self):
        for element in self.victory_condition:
            if not self.victory_condition_fullfilled(element):
                return False
        return True


def pos_inside(pos, rec_pos, rec_width, rec_height):
    x, y = pos
    rec_x, rec_y = rec_pos
    rec_X = rec_x + rec_width
    rec_Y = rec_y + rec_height
    return between(x, rec_x, rec_X) and between(y, rec_y, rec_Y)

def between(a, b, B):
    return a >= b and a <= B

def create_effects(space, batch, effects):
    new_effects = list()
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
        elif effect.title == "Mining":
            mining = Mining(space, batch, (x, y), molecules)
            new_effects.append(mining)
        else:
            raise Exception("Effect not implemented:" + effect.title)

    return new_effects
