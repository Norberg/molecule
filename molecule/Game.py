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
import math
import pymunk
from pymunk import pyglet_util
import pyglet
from pyglet.window import mouse
from pyglet import gl

from molecule import Universe
from molecule import Config
from molecule.Levels import Levels
from molecule import Gui
from molecule.server.Server import Server
from molecule.LevelMenu import LevelMenu

class Game(pyglet.window.Window):
    def __init__(self):
        config = self.create_config()
        fullscreen = Config.current.fullscreen
        resizable = Config.current.resizable
        width = Config.current.width
        height = Config.current.height
        if fullscreen:
            width = None
            height = None
        super(Game, self).__init__(caption="Molecule", config=config,
            vsync=True, resizable=resizable, fullscreen=fullscreen,
            width=width, height=height)
        self.init_pyglet()
        self.DEBUG_GRAPHICS = False
        self.level = None
        self.menu = None # Add menu state
        self.start()

    def create_config(self):
        # In pyglet 2+, we can create a config directly without going through canvas
        try:
            config = pyglet.gl.Config(sample_buffers=1,
                                      samples=4,
                                      double_buffer=True)
        except pyglet.window.NoSuchConfigException:
            print("Hardware does not support all features,",
                  "fallback to just the basic features")
            config = pyglet.gl.Config(double_buffer=True)
        return config

    def start(self):
        pyglet.gl.glClearColor(250/256.0, 250/256.0, 250/256.0, 0)
        self.levels = Levels("data/levels", Config.current.level, window=self)
        self.penalty = 0
        self.server = Server(self)
        pyglet.clock.schedule_interval(self.update, 1/100.0)
        self.server.start()
        self.show_menu(start_at_map=True)

    def add_penalty(self, seconds):
        self.penalty += seconds


    def show_menu(self, start_at_map=False):
        if self.level:
            self.level.delete()
            self.level = None
        if self.menu:
            self.menu.delete()
        self.menu = LevelMenu(self, self.levels, self.on_level_selected, start_at_map=start_at_map)

    def on_level_selected(self, level_path):
        # Find index of selected level
        for i, path in enumerate(self.levels.levels):
            if path == level_path:
                self.levels.current_level = i
                break
        self.penalty = 0
        self.menu.delete()


        self.menu = None
        level = self.levels.get_current_level()
        self.switch_level(level)
        

    def init_pyglet(self):
        gl.glLineWidth(4)
        gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def update(self, dt):
        if self.level:
            self.level.update()

    def on_draw(self):
        if self.menu:
            self.menu.on_draw()
            return
        # Ensure white background for gameplay
        pyglet.gl.glClearColor(250/256.0, 250/256.0, 250/256.0, 0)
        self.clear()
        if self.batch:
            self.batch.draw()
        if self.DEBUG_GRAPHICS:
            options = pyglet_util.DrawOptions()
            self.space.debug_draw(options)

    def switch_level(self, level):
        """ Switch to level """
        if self.level is not None:
            self.level.delete()
        self.run_level(level)

    def run_level(self, level):
        self.batch = level.batch
        self.level = level
        self.space = level.space

    def reset_level(self):
        level = self.levels.get_current_level()
        self.switch_level(level)
