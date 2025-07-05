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
import re

import pyglet
from molecule.CustomGUI import (
    Manager, VerticalContainer, Document, Frame, SectionHeader, 
    FoldingSection, PopupMessage, Scrollable, OneTimeButton,
    ANCHOR_BOTTOM_RIGHT, HALIGN_LEFT
)
from molecule import RenderingOrder
import re

# Theme is no longer needed as we use simple colors
NA = "<b>N<sub>A<sub><b>"
formula_pattern = re.compile(r"([A-Z][a-z]?)(\d*)|(\+|\-)(\d*)?")
identify_formula_pattern = re.compile(r"([A-Z][a-z]?)(\d+|[+-]\d*)")

def create_folding_description(window, batch, heading, description, chapters=list()):
    """
        window - window
        batch - batch
        heading - heading of the widget
        description - description for the widget
        chapters - list of tuples (heading,text)
    """
    # Create description document
    description_doc = Document(description, 0, 0, 300, 100, batch)

    layout = list()
    layout.append(SectionHeader(heading, 0, 0, 300, 30, batch))
    layout.append(description_doc)

    for chapter in chapters:
        heading, text = chapter
        text_doc = Document(text, 0, 0, 300, 100, batch)
        layout.append(FoldingSection(heading, text_doc, 0, 0, 300, 130, batch, is_open=False))

    # Create container and scrollable
    container = VerticalContainer(0, 0, 300, 400)
    for item in layout:
        container.add(item)
    
    scrollable = Scrollable(container, 0, 0, 300, 400, batch, height_limit=400)
    content = Frame(0, 0, 300, 400, batch, is_expandable=True)
    content.add_child(scrollable)

    Manager(content, window=window, batch=batch, group=RenderingOrder.gui,
           anchor=ANCHOR_BOTTOM_RIGHT, is_movable=False)

def create_popup(window, batch, text, on_escape=None):
    """
        window - window
        batch - batch
        text - text message in popup
        on_escape - callback when popup is closed
    """
    PopupMessage(text=text, window=window, batch=batch,
                 group=RenderingOrder.gui, on_escape=on_escape)

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

def formula_to_html(formula):
    def html_formatter(match):
        element, count, charge_sign, charge_count = match.groups()
        if element:
            return f"{element}{f'<sub>{count}</sub>' if count else ''}"
        else:
            charge = charge_count if charge_count else ""
            return f"<sup>{charge}{charge_sign}</sup>"
    html_formula = formula_pattern.sub(html_formatter, formula)
    return html_formula

def find_and_convert_formulas(text):

    def replace_formula(match):
        #print(f"Match: {match.group()}")
        return formula_to_html(match.group())
    
    converted_text = identify_formula_pattern.sub(replace_formula, text)
    return converted_text