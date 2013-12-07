import pyglet
import pyglet_gui.theme
from pyglet_gui.dialog import Dialog
from pyglet_gui.containers import Frame, VerticalLayout
from pyglet_gui.document import Document
from pyglet_gui.constants import ANCHOR_BOTTOM_RIGHT, HALIGN_LEFT
from pyglet_gui.gui import SectionHeader, FoldingSection, PopupMessage
from pyglet_gui.scrollable import Scrollable

from molecule import RenderingOrder

theme = pyglet_gui.theme.Theme('molecule/theme')

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

    content = Frame(Scrollable(VerticalLayout(layout, align=HALIGN_LEFT),height=400))

    Dialog(content, window=window, batch=batch, group=RenderingOrder.gui,
           anchor=ANCHOR_BOTTOM_RIGHT, theme=theme, movable=False)

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

