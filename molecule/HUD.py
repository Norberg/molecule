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
import time

import pyglet
from molecule.CustomGUI import (
    Manager, Container, HorizontalContainer, VerticalContainer, Document, Frame, 
    SectionHeader, FoldingSection, PopupMessage, Scrollable, Button, OneTimeButton,
    ANCHOR_BOTTOM_LEFT, HALIGN_LEFT, ANCHOR_TOP_RIGHT, GUI_PADDING
)
from molecule import RenderingOrder
from molecule import Effects
from molecule import Gui
from libcml import CachedCml

class HUD:
    HEIGHT = 108 # 5 lines of text
    VERTICAL_HUD_WIDTH = 180

    def __init__(self, window, batch, space, level, create_elements_callback):
        height = self.HEIGHT
        
        VERTICAL_HUD_WIDTH = self.VERTICAL_HUD_WIDTH
        
        # Calculate dimensions dynamically
        # Horizontal HUD fills width minus the vertical HUD width and padding/gap
        vertical_hud_total_width = VERTICAL_HUD_WIDTH + GUI_PADDING
        horizontal_width = window.width - vertical_hud_total_width - GUI_PADDING
        
        self.horizontal = HorizontalHUD(window, batch, space, level, height, horizontal_width)
        
        vertical_height = window.height - (GUI_PADDING * 2)
        self.vertical = VerticalHUD(window, batch, space, level, vertical_height, VERTICAL_HUD_WIDTH, create_elements_callback)

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
        
        # Calculate widths
        # Left side (Objective/Progress) doesn't need to be huge. 
        # Let's give it a fixed width or a smaller percentage.
        # Previous was 50/50.
        # Let's try fixed width of 400px for left, rest for right.
        left_width = 450
        info_width = width - left_width# - 10 # 10 for spacing

        progress_height = 30
        
        # Progress + objective (fallbacks for missing data)
        progress_text = "Progress:"
        self.progress_doc = Document(progress_text, 0, 0, left_width, progress_height, batch)
        objective_str = level.objective or ""
        objective_html = Gui.find_and_convert_formulas(objective_str)
        objective_doc = Document(objective_html, 0, 0, left_width, height-progress_height, batch)

        # Create left frame container
        left_container = VerticalContainer(0, 0, left_width, height)
        left_container.add(objective_doc)
        #left_container.add(None)  # Spacer
        left_container.add(self.progress_doc)
        left_frame = Frame(0, 0, left_width, height, batch, is_expandable=True)
        left_frame.add_child(left_container)

        self.left_container = VerticalContainer(0, 0, left_width, height)
        self.left_container.add(left_frame)

        # Info text
        self.info_doc = Document("", 0, 0, info_width, height, self.batch, 
                               font_size=10, multiline=True, autosize_height=True)
        
        # Wrap in Scrollable
        self.info_scroll = Scrollable(self.info_doc, 0, 0, info_width, height, 
                                    self.batch, RenderingOrder.gui)

        info_frame = Frame(0, 0, info_width, height, self.batch)
        info_frame.add_child(self.info_scroll)
        
        self.info_container = VerticalContainer(0, 0, info_width, height)
        self.info_container.add(info_frame)

        # Victory formula fallback (avoid index error)
        victory_formula = level.victory_condition[0] if level.victory_condition else "H2O"
        self.update_info_text(victory_formula) # Initialize with victory formula

        container = HorizontalContainer(0, 0, width, height, spacing=0)
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
        cml = CachedCml.getMolecule(formula)
        info_text = "<b>%s - %s</b><br> %s" % (
                cml.property.get("Name", "Undefined"),
                Gui.formula_to_html(formula),
                Gui.find_and_convert_formulas(cml.property.get("Description", "No Description Available"))
                )
        self.info_doc.set_text(info_text)
        # Force scrollable layout update
        if hasattr(self, 'info_scroll'):
            self.info_scroll.scroll_offset = 0
            self.info_scroll.layout()

    def on_draw(self):
        self.tick += 1
        if self.tick > 30:
            return
        self.tick = 0
        self.update_progress()

    def update_progress(self):
        progress_text = self.victory.progress_text()
        formatted_text = "Progress: " + progress_text
        self.progress_doc.set_text(Gui.find_and_convert_formulas(formatted_text))

    def delete(self):
        self.window.remove_handlers(on_draw=self.on_draw)
        self.manager.delete()


class VerticalHUD:
    def __init__(self, window, batch, space, level, height, width, create_elements_callback):
        self.window = window
        self.batch = batch
        self.space = space
        self.level = level
        status_height = 100
        status_text = '''Time: 0 sec
Points: 0 points
FPS: 00.00 FPS'''
        self.status_doc = Document(status_text, 0, 0, width, status_height, batch)
        status_frame = Frame(0, 0, width, status_height, batch)
        status_frame.add_child(self.status_doc)
        
        inv_text = "<h4>Inventory</h4>"
        inventory_header = Document(inv_text, 0, 0, width, 30, batch)
        self.inventory_container = VerticalContainer(0, 0, width, height - status_height - 30)

        container = VerticalContainer(0, 0, width, height - status_height)
        container.add(inventory_header)
        container.add(self.inventory_container)
        self.inventory_frame = Frame(0, 0, width, height - status_height, batch)
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

        # FPS Tracking
        self.last_fps_time = time.time()
        self.frame_count = 0
        self.fps = 0.0

    def init_effects(self, space, level):
        pos = (self.inventory_frame.x + self.inventory_frame.width / 2,
               self.inventory_frame.y + self.inventory_frame.height / 2 - 400)
        self.inventory_effect = Effects.Inventory(space, pos, "Inventory",
                self.inventory_frame.width, self.inventory_frame.height + 800,
                level.inventory, gui_container=self.inventory_container, create_element_callback=self.create_element_callback)

    def get_effects(self):
        return [self.inventory_effect]

    def on_draw(self):
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_fps_time >= 0.2: # Update every 0.2s
            self.fps = self.frame_count / (current_time - self.last_fps_time)
            self.frame_count = 0
            self.last_fps_time = current_time
            self.update_status()

    def update_status(self):
        level_time = self.window.level.get_time()
        points = self.window.level.get_points()
        status_text = '''Time: %d sec
Points: %d points
FPS: %.2f FPS''' % (level_time, points, self.fps)
        self.status_doc.set_text(status_text)

    def delete(self):
        self.window.remove_handlers(on_draw=self.on_draw)
        self.manager.delete()

