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
#FIXME: Commit missing file
#from molecule import pymunk_debug

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
        self.start()

    def create_config(self):
        display = pyglet.canvas.get_display();
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
        self.levels = Levels("data/levels", Config.current.level, window=self)
        pyglet.clock.schedule_interval(self.update, 1/100.0)
        self.reset_level()

    def init_pyglet(self):
        gl.glLineWidth(4)
        gl.glHint(gl.GL_LINE_SMOOTH_HINT, gl.GL_NICEST)
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

    def update(self, dt):
        self.level.update()

    def on_draw(self):
        self.clear()
        self.batch.draw()
        if self.DEBUG_GRAPHICS:
            options = pymunk_debug.DrawOptions()
            self.space.debug_draw(options)

    def switch_level(self, level=None):
        """ Switch to level, if level=None switch to next level"""
        if self.level is not None:
            self.level.delete()
        if level is None:
            level = self.levels.next_level()
            if level is None:
                Gui.create_popup(self, self.batch, "Congratulation you have won the game!",
                             on_escape=self.close)
            else:
                self.run_level(level)
        else:
            self.run_level(level)

    def run_level(self, level):
        self.batch = level.batch
        self.level = level
        self.space = level.space

    def reset_level(self):
        level = self.levels.get_current_level()
        self.switch_level(level)
