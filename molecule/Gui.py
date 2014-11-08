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
import os

import pyglet
import pyglet_gui.theme
from pyglet_gui.manager import Manager
from pyglet_gui.containers import VerticalContainer
from pyglet_gui.document import Document
from pyglet_gui.constants import ANCHOR_BOTTOM_RIGHT, HALIGN_LEFT
from pyglet_gui.gui import Frame, SectionHeader, FoldingSection, PopupMessage
from pyglet_gui.scrollable import Scrollable
from pyglet_gui.buttons import OneTimeButton

from molecule import RenderingOrder

theme = pyglet_gui.theme.ThemeFromPath(os.getcwd()+'/molecule/theme')
NA = "<b>N<sub>A<sub><b>"

def create_folding_description(window, batch, heading, description, chapters=list()):
    """
        window - window
        batch - batch
        heading - heading of the widget
        description - description for the widget
        chapters - list of tuples (heading,text)
    """
    description_doc = pyglet.text.decode_attributed(description)

    layout = list()
    layout.append(SectionHeader(heading))
    layout.append(Document(description_doc, width=300))

    for chapter in chapters:
        heading, text = chapter
        text_doc = pyglet.text.decode_attributed(text)
        layout.append(FoldingSection(heading,
                      Document(text_doc, width=300),
                      is_open=False))

    content = Frame(Scrollable(VerticalContainer(layout, align=HALIGN_LEFT),height=400))

    Manager(content, window=window, batch=batch, group=RenderingOrder.gui,
           anchor=ANCHOR_BOTTOM_RIGHT, theme=theme, is_movable=False)

def create_popup(window, batch, text, on_escape=None):
    """
        window - window
        batch - batch
        text - text message in popup
        on_escape - callback when popup is closed
    """
    def on_escape_cb(dialog):
            if on_escape is not None:
                on_escape()
    PopupMessage(text=text, window=window, batch=batch,
                 group=RenderingOrder.gui, theme=theme, on_escape=on_escape_cb)

class MoleculeButton(OneTimeButton):
    def __init__(self, element, count, on_click=None):
        self.element = element
        self.count = count
        self.update_label()
        OneTimeButton.__init__(self, self.label)
        self._on_click = on_click

    def on_mouse_press(self, x, y, button, modifiers):
        self.change_state()
        if self._on_click is not None:
            self._on_click(self)

    def update_label(self):
        self.label = "%d - %s" % (self.count, self.element)

    def get_path(self):
        path = ["molecule-button"]
        if self.is_pressed:
                path.append('down')
        else:
                path.append('up')
        return path
