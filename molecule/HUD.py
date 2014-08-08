# Molecule - a chemical reaction puzzle game
# Copyright (C) 2013-2014 Simon Norberg <simon@pthread.se>
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
import os

import pyglet
import pyglet_gui.theme
from pyglet_gui.manager import Manager
from pyglet_gui.containers import Container, HorizontalContainer,VerticalContainer
from pyglet_gui.document import Document
from pyglet_gui.constants import ANCHOR_BOTTOM_LEFT, HALIGN_LEFT, ANCHOR_TOP_RIGHT
from pyglet_gui.gui import Frame, SectionHeader, FoldingSection, PopupMessage
from pyglet_gui.scrollable import Scrollable

from molecule import RenderingOrder
from molecule import Effects
theme = pyglet_gui.theme.ThemeFromPath(os.getcwd()+'/molecule/theme')

class HUD:
    def __init__(self, window, batch, space, level):
        height = 100
        width = window.width - 300
        self.horizontal = HorizontalHUD(window, batch, space, level, height, width)
        height = window.height - 40
        width = 180
        self.vertical = VerticalHUD(window, batch, space, level, height, width)

    def get_effects(self):
        return self.horizontal.get_effects()

    def delete(self):
        self.horizontal.delete()
        self.vertical.delete()

class HorizontalHUD:
    def __init__(self, window, batch, space, level, height, width):
        self.space = space
        self.level = level
        progress_text = "Progress: ..."
        self.progress_doc = Document(progress_text, width = width/2)
        objective_doc = Document(level.objective, width = width/2)
        left_frame = Frame(VerticalContainer([objective_doc, None,
            self.progress_doc]), is_expandable = True)
        self.left_container = VerticalContainer([left_frame])
        info_text = pyglet.text.decode_attributed('''
Methane is a hydrocarbon that is a gas at room temperature (20°C). Its
molecular formula is CH4, so it has one carbon atom and four hydrogen
atoms in a molecule. It is often found as the main part of natural gas.
Methane is a greenhouse gas 22 times more effective than carbon
dioxide. It is also less stable and slowly oxidates by oxygen to carbon
dioxide and water.
''')
        info_doc = Document(info_text, height=height, width=width/2,
                is_fixed_size = True)
        info_frame = Frame(info_doc)
        info_container = VerticalContainer([info_frame])
        container = HorizontalContainer([self.left_container, info_container])
        self.manager = Manager(container, window=window, batch=batch,
                group=RenderingOrder.hud, anchor=ANCHOR_BOTTOM_LEFT,
                theme=theme, is_movable=False)
        self.window = window
        self.window.push_handlers(on_draw=self.on_draw)
        self.tick = 0
        self.init_effects(space, level)

    def init_effects(self, space, level):
        pos = (self.left_container.x + self.left_container.width / 2,
               self.left_container.y + self.left_container.height / 2 - 100)
        self.victory = Effects.VictoryInventory(space, pos, "Victory Inventory",
                self.left_container.width, self.left_container.height + 100,
                level.victory_condition)

    def get_effects(self):
        return [self.victory]

    def on_draw(self):
        self.tick += 1
        if self.tick > 30:
            return
        self.tick = 0
        self.update_progress()

    def update_progress(self):
        progress_text = self.victory.progress_text()
        self.progress_doc.set_text("Progress: " + progress_text)

    def delete(self):
        self.window.remove_handlers(on_draw = self.on_draw)
        self.manager.delete()


class VerticalHUD():
    def __init__(self, window, batch, space, level, height, width):
        self.space = space
        self.level = level
        status_text = pyglet.text.decode_attributed('''
Time: 0 sec \n
Points: 0 points \n
FPS: 00.00 FPS
''')
        self.status_doc = Document(status_text, height=height, width=width)
        status_frame = Frame(self.status_doc)
        inventory_text = pyglet.text.decode_attributed('''
Inventory: \n
H2O 1 mol  18 g\n
CH4 2 mol 18 g\n
Total: 36/100 g \n
''')
        inventory_doc = Document(inventory_text, height=height, width=width)
        inventory_frame = Frame(inventory_doc)
        container = VerticalContainer([status_frame, inventory_frame])
        self.manager = Manager(container, window=window, batch=batch,
                group=RenderingOrder.hud, anchor=ANCHOR_TOP_RIGHT, theme=theme,
                is_movable=False)
        self.window = window
        self.window.push_handlers(on_draw=self.on_draw)
        self.tick = 0

    def on_draw(self):
        self.tick += 1
        if self.tick > 30:
            return
        self.tick = 0
        self.update_status()

    def update_status(self):
        level_time = self.window.level.get_time()
        points = self.window.level.get_points()
        status_text = '''
Time: %d sec
Points: %d points
FPS: %.2f FPS
''' % (level_time, points, pyglet.clock.get_fps())
        self.status_doc.set_text(status_text)

    def delete(self):
        self.window.remove_handlers(on_draw = self.on_draw)
        self.manager.delete()

