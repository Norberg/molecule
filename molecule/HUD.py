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
from molecule.CustomGUI import (
    Manager, Container, HorizontalContainer, VerticalContainer, Document, Frame, 
    SectionHeader, FoldingSection, PopupMessage, Scrollable, Button, OneTimeButton,
    ANCHOR_BOTTOM_LEFT, HALIGN_LEFT, ANCHOR_TOP_RIGHT
)
from molecule import RenderingOrder
from molecule import Effects
from molecule import Gui
from libcml import CachedCml

# Theme is no longer needed as we use simple colors

class HUD:
    def __init__(self, window, batch, space, level, create_elements_callback):
        height = 100
        width = window.width - 300
        self.horizontal = HorizontalHUD(window, batch, space, level, height, width)
        height = window.height - 40
        width = 180
        self.vertical = VerticalHUD(window, batch, space, level, height, width, create_elements_callback)

    def update_info_text(self, formula):
        self.horizontal.update_info_text(formula)

    def get_effects(self):
        l = list()
        l.extend(self.horizontal.get_effects())
        l.extend(self.vertical.get_effects())
        return l

    def delete(self):
        self.horizontal.delete()
        self.vertical.delete()

class HorizontalHUD:
    def __init__(self, window, batch, space, level, height, width):
        self.window = window
        self.batch = batch
        self.space = space
        self.level = level
        self.height = height
        self.width = width
        # Progress + objective (fallbacks for missing data)
        progress_text = "Progress:"
        self.progress_doc = Document(progress_text, 0, 0, width//2, height, batch)
        objective_str = level.objective or ""
        objective_html = Gui.find_and_convert_formulas(objective_str)
        objective_doc = Document(objective_html, 0, 0, width//2, height, batch)

        # Create left frame container
        left_container = VerticalContainer(0, 0, width//2, height)
        left_container.add(objective_doc)
        left_container.add(None)  # Spacer
        left_container.add(self.progress_doc)
        left_frame = Frame(0, 0, width//2, height, batch, is_expandable=True)
        left_frame.add_child(left_container)

        self.left_container = VerticalContainer(0, 0, width//2, height)
        self.left_container.add(left_frame)

        # Victory formula fallback (avoid index error)
        victory_formula = level.victory_condition[0] if level.victory_condition else "H2O"
        info_frame = self.create_info_frame(victory_formula)
        self.info_container = VerticalContainer(0, 0, width//2, height)
        self.info_container.add(info_frame)

        container = HorizontalContainer(0, 0, width, height)
        container.add(self.left_container)
        container.add(self.info_container)

        self.manager = Manager(container, window=window, batch=batch,
                group=RenderingOrder.gui, anchor=ANCHOR_BOTTOM_LEFT,
                is_movable=False)
        self.window = window
        self.window.push_handlers(on_draw=self.on_draw)
        self.tick = 0
        self.init_effects(space, level)
        self.manager.update_position()

    def init_effects(self, space, level):
        pos = (self.left_container.x + self.left_container.width / 2,
               self.left_container.y + self.left_container.height / 2 - 50)
        self.victory = Effects.VictoryInventory(space, pos, "Victory Inventory",
                self.left_container.width, self.left_container.height + 100,
                level.victory_condition)

    def get_effects(self):
        return [self.victory]

    def update_info_text(self, formula):
        info_frame = self.create_info_frame(formula)
        for content in self.info_container.children:
            self.info_container.remove(content)
        self.info_container.add(info_frame)

    def create_info_frame(self, formula):
        cml = CachedCml.getMolecule(formula)
        info_text = "<b>%s - %s</b><br> %s" % (
                cml.property.get("Name", "Undefined"),
                Gui.formula_to_html(formula),
                Gui.find_and_convert_formulas(cml.property.get("Description", "No Description Available"))
                )
        info_doc = Document(info_text, 0, 0, self.width//2, self.height, self.batch,
                is_fixed_size=True)
        info_frame = Frame(0, 0, self.width//2, self.height, self.batch)
        info_frame.add_child(info_doc)
        return info_frame

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
        self.window.remove_handlers(on_draw=self.on_draw)
        self.manager.delete()


class VerticalHUD:
    def __init__(self, window, batch, space, level, height, width, create_elements_callback):
        self.window = window
        self.batch = batch
        self.space = space
        self.level = level
        status_text = '''
Time: 0 sec
Points: 0 points
FPS: 00.00 FPS
'''
        self.status_doc = Document(status_text, 0, 0, width, height, batch)
        status_frame = Frame(0, 0, width, height, batch)
        status_frame.add_child(self.status_doc)
        
        inv_text = "<h4>Inventory</h4>"
        inventory_header = Document(inv_text, 0, 0, width, 30, batch)
        self.inventory_container = VerticalContainer(0, 0, width, height-30)

        container = VerticalContainer(0, 0, width, height)
        container.add(inventory_header)
        container.add(self.inventory_container)
        self.inventory_frame = Frame(0, 0, width, height, batch)
        self.inventory_frame.add_child(container)
        
        container = VerticalContainer(0, 0, width, height)
        container.add(status_frame)
        container.add(self.inventory_frame)
        
        self.manager = Manager(container, window=window, batch=batch,
                group=RenderingOrder.gui, anchor=ANCHOR_TOP_RIGHT,
                is_movable=False)
        self.window = window
        self.window.push_handlers(on_draw=self.on_draw)
        self.tick = 0
        self.create_element_callback = create_elements_callback
        self.init_effects(space, level)
        self.manager.update_position()

    def init_effects(self, space, level):
        pos = (self.inventory_frame.x + self.inventory_frame.width / 2,
               self.inventory_frame.y + self.inventory_frame.height / 2 - 400)
        self.inventory_effect = Effects.Inventory(space, pos, "Inventory",
                self.inventory_frame.width, self.inventory_frame.height + 800,
                level.inventory, gui_container=self.inventory_container, create_element_callback=self.create_element_callback)

    def get_effects(self):
        return [self.inventory_effect]

    def on_draw(self):
        self.tick += 1
        if self.tick > 30:
            return
        self.tick = 0
        self.update_status()

    def update_status(self):
        level_time = self.window.level.get_time()
        points = self.window.level.get_points()
        # In pyglet 2+, get_fps() is no longer available
        # We'll use a simple counter or skip FPS display for now
        status_text = '''
Time: %d sec
Points: %d points
FPS: N/A
''' % (level_time, points)
        self.status_doc.set_text(status_text)

    def delete(self):
        self.window.remove_handlers(on_draw=self.on_draw)
        self.manager.delete()

