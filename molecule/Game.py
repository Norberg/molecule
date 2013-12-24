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
import sys
import time
import os
import random
import inspect
import math
import pymunk
from pymunk import pyglet_util
import pyglet
from pyglet.window import mouse
from pyglet import gl

from molecule import Universe
from molecule import Config
from molecule import CollisionTypes    
from molecule.Levels import Levels
from molecule import Gui

class Game(pyglet.window.Window):
    def __init__(self):
        config = self.create_config()
        super(Game, self).__init__(caption="Molecule", config=config,
                                   vsync=True, resizable=True)
        self.init_pyglet()
        self.init_pymunk()
        self.DEBUG_GRAPHICS = False
        self.start()


    def create_config(self):
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        screen = display.get_default_screen()
        try:
            template = pyglet.gl.Config(sample_buffers=1,
                                        samples=4,
                                        double_buffer=True)
            config = screen.get_best_config(template)
        except pyglet.window.NoSuchConfigException:
            print("Hardware does not support all features,",
                  "fallback to just the basic features")
            config = pyglet.gl.Config(double_buffer=True)
        return config

    def start(self):
        pyglet.gl.glClearColor(250/256.0, 250/256.0, 250/256.0, 0)
        self.fps_display = pyglet.clock.ClockDisplay()
        self.levels = Levels("data/levels", Config.current.level, window=self)
        self.switch_level() 
        pyglet.clock.schedule_interval(self.update, 1/100.0)
    
    def init_pymunk(self):
        self.last_collision = 0
        self.space = None
        self.mouse_body = pymunk.Body()    
        self.mouse_spring = None

    def init_pyglet(self):
        gl.glLineWidth(4)
        gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
        #gl.glTexParameteri(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER,
        #                   gl.GL_NEAREST_MIPMAP_NEAREST)
    
    def on_draw(self):
        self.clear()
        self.level.update()
        self.batch.draw()
        if self.DEBUG_GRAPHICS:
            pymunk.pyglet_util.draw(self.space)
        self.fps_display.draw()
    
    def switch_level(self, level=None):
        """ Switch to level, if level=None switch to next level"""
        if level is None:
            level = self.levels.next_level()
            self.run_level(level)
        else:
            raise NotImplementedError("not yet possible to swith to a specific level")

    def run_level(self, level):
        if level is None:
            Gui.create_popup(self, self.batch, "Congratulation you have won the game!",
                             on_escape=self.close)
            return
        self.active = None
        self.batch = level.batch
        self.level = level
        self.space = level.space
        self.level.window = self
        self.mouse_spring = None
        self.space.add_collision_handler(CollisionTypes.ELEMENT,
                                         CollisionTypes.ELEMENT,
                                         post_solve=self.level.element_collision)
        self.space.add_collision_handler(CollisionTypes.ELEMENT,
                                         CollisionTypes.EFFECT,
                                         begin=self.level.effect_reaction)

    def limit_pos_to_screen(self, x, y):
        x = max(0,x)
        y = max(0,y)
        w, h = self.get_size()
        x = min(w,x)
        y = min(h,y)
        return x,y 

    def on_mouse_press(self, x, y, button, modifiers):
        self.handle_mouse_button_down(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        if self.mouse_spring != None:
            self.mouse_spring.b.mass *= 50
            self.mouse_spring.b.velocity = (0,0)
            self.mouse_spring.b.molecule.set_dragging(False)
            self.space.remove(self.mouse_spring)
            self.mouse_spring = None
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x,y = self.limit_pos_to_screen(x,y)
        self.mouse_body.position = (x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.M:
            print("dumping memory..")
            from meliae import scanner
            scanner.dump_all_objects("memory.dump")
        elif symbol == pyglet.window.key.ESCAPE:
            self.close()
        elif symbol == pyglet.window.key.S:    
            Gui.create_popup(self, self.batch, "Skipping level, Cheater!",
                             on_escape=self.switch_level)
        elif symbol == pyglet.window.key.R:
            print("reseting..")    
            self.level.reset()
            self.run_level(self.level)
        elif symbol == pyglet.window.key.D:    
            self.DEBUG_GRAPHICS = not self.DEBUG_GRAPHICS

    def update(self, dt):
        self.space.step(1/120.0)
        if self.level.victory:
            Gui.create_popup(self, self.batch, "Congratulation, you finished the level",
                             on_escape=self.switch_level)
            self.level.victory = False

    def handle_mouse_button_down(self, x, y):
        if self.mouse_spring != None:
            self.on_mouse_release(None, None, None, None)
        self.mouse_body.position = (x, y)
        clicked = self.space.nearest_point_query_nearest((x,y), 16)
        if (clicked != None and 
            clicked["shape"].collision_type == CollisionTypes.ELEMENT and
            clicked["shape"].molecule.draggable):
            clicked = clicked["shape"]
            clicked.molecule.set_dragging(True)
            rest_length = self.mouse_body.position.get_distance(clicked.body.position)
            self.mouse_spring = pymunk.PivotJoint(self.mouse_body, clicked.body, (0,0), (0,0))
            self.mouse_spring.error_bias = math.pow(1.0-0.2, 30.0)
            clicked.body.mass /= 50
            self.space.add(self.mouse_spring) 
