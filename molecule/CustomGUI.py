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

import pyglet
from pyglet import gl
from pyglet.graphics import Batch, Group
from pyglet.text import Label, HTMLLabel
from pyglet.shapes import Rectangle
import math
import json
import os
from molecule import RenderingOrder
from molecule import pyglet_util


class Theme:
    """Theme system to load and manage GUI styling"""
    
    def __init__(self, theme_path="molecule/theme/theme.json"):
        self.theme_path = theme_path
        self.theme_data = self._load_theme()
        self.images = {}
        self._load_images()
        
    def _load_theme(self):
        """Load theme configuration from JSON file"""
        try:
            print(f"Loading theme from: {self.theme_path}")
            with open(self.theme_path, 'r') as f:
                theme_data = json.load(f)
                print(f"Successfully loaded theme with {len(theme_data)} entries")
                return theme_data
        except Exception as e:
            print(f"Failed to load theme: {e}")
            # Fallback to default theme
            return {
                "font": "Arial",
                "font_size": 12,
                "text_color": [0, 0, 0, 255],
                "gui_color": [255, 255, 255, 255]
            }
    
    def _load_images(self):
        """Load theme images"""
        theme_dir = os.path.dirname(self.theme_path)
        
        # Load common images
        image_files = [
            "button.png", "button-down.png", "button-highlight.png",
            "panel.png", "green_panel.png", "titlepanel.png",
            "green-button-up.png", "red-button-down.png"
        ]
        
        for img_file in image_files:
            try:
                img_path = os.path.join(theme_dir, img_file)
                if os.path.exists(img_path):
                    # Load image directly from file path
                    self.images[img_file] = pyglet.image.load(img_path)
                    print(f"Loaded theme image: {img_file}")
                else:
                    print(f"Theme image not found: {img_path}")
            except Exception as e:
                print(f"Failed to load theme image {img_file}: {e}")
                pass
    
    def get_image(self, image_name):
        """Get a theme image by name"""
        return self.images.get(image_name)
    
    def get_color(self, color_name):
        """Get a theme color by name"""
        return self.theme_data.get(color_name, [0, 0, 0, 255])


# Global theme instance
theme = Theme()


class CustomGUI:
    """Custom GUI system to replace pyglet-gui functionality"""
    
    def __init__(self, window, batch, group=None):
        self.window = window
        self.batch = batch
        self.group = group
        self.widgets = []
        self.active_widget = None
        
    def add_widget(self, widget):
        """Add a widget to the GUI system"""
        self.widgets.append(widget)
        return widget
        
    def remove_widget(self, widget):
        """Remove a widget from the GUI system"""
        if widget in self.widgets:
            self.widgets.remove(widget)
            
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse press events"""
        for widget in reversed(self.widgets):
            if widget.contains_point(x, y):
                if hasattr(widget, 'on_mouse_press'):
                    widget.on_mouse_press(x, y, button, modifiers)
                self.active_widget = widget
                return True
        self.active_widget = None
        return False
        
    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse release events"""
        if self.active_widget and hasattr(self.active_widget, 'on_mouse_release'):
            self.active_widget.on_mouse_release(x, y, button, modifiers)
        self.active_widget = None
        
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        """Handle mouse drag events"""
        if self.active_widget and hasattr(self.active_widget, 'on_mouse_drag'):
            self.active_widget.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
            
    def delete(self):
        """Clean up all widgets"""
        for widget in self.widgets:
            widget.delete()
        self.widgets.clear()


class Widget:
    """Base class for all GUI widgets"""
    
    def __init__(self, x, y, width, height, batch=None, group=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.batch = batch
        self.group = group
        self.visible = True
        
    def contains_point(self, x, y):
        """Check if a point is within this widget"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)
                
    def delete(self):
        """Clean up widget resources"""
        pass


def draw_nine_patch(batch, group, img, x, y, width, height, frame, padding):
    """
    Draw a 9-slice (9-patch) image using pyglet sprites.
    - img: pyglet image
    - x, y: position
    - width, height: size to fill
    - frame: [left, top, right, bottom] (pixels)
    - padding: [left, right, top, bottom] (pixels)
    Returns: list of sprites
    """
    left, top, right, bottom = frame
    img_w, img_h = img.width, img.height
    # Regions:
    #  TL |  T  |  TR
    #  L  |  C  |  R
    #  BL |  B  |  BR
    regions = {}
    # Corners
    regions['tl'] = img.get_region(0, img_h - top, left, top)
    regions['tr'] = img.get_region(img_w - right, img_h - top, right, top)
    regions['bl'] = img.get_region(0, 0, left, bottom)
    regions['br'] = img.get_region(img_w - right, 0, right, bottom)
    # Edges
    regions['t'] = img.get_region(left, img_h - top, img_w - left - right, top)
    regions['b'] = img.get_region(left, 0, img_w - left - right, bottom)
    regions['l'] = img.get_region(0, bottom, left, img_h - top - bottom)
    regions['r'] = img.get_region(img_w - right, bottom, right, img_h - top - bottom)
    # Center
    regions['c'] = img.get_region(left, bottom, img_w - left - right, img_h - top - bottom)
    # Target sizes
    w, h = width, height
    # Place regions
    sprites = []
    # Corners
    sprites.append(pyglet.sprite.Sprite(regions['tl'], x=x, y=y + h - top, batch=batch, group=group))
    sprites.append(pyglet.sprite.Sprite(regions['tr'], x=x + w - right, y=y + h - top, batch=batch, group=group))
    sprites.append(pyglet.sprite.Sprite(regions['bl'], x=x, y=y, batch=batch, group=group))
    sprites.append(pyglet.sprite.Sprite(regions['br'], x=x + w - right, y=y, batch=batch, group=group))
    # Edges
    sprites.append(pyglet.sprite.Sprite(regions['t'], x=x + left, y=y + h - top, batch=batch, group=group))
    sprites[-1].scale_x = (w - left - right) / regions['t'].width
    sprites.append(pyglet.sprite.Sprite(regions['b'], x=x + left, y=y, batch=batch, group=group))
    sprites[-1].scale_x = (w - left - right) / regions['b'].width
    sprites.append(pyglet.sprite.Sprite(regions['l'], x=x, y=y + bottom, batch=batch, group=group))
    sprites[-1].scale_y = (h - top - bottom) / regions['l'].height
    sprites.append(pyglet.sprite.Sprite(regions['r'], x=x + w - right, y=y + bottom, batch=batch, group=group))
    sprites[-1].scale_y = (h - top - bottom) / regions['r'].height
    # Center
    sprites.append(pyglet.sprite.Sprite(regions['c'], x=x + left, y=y + bottom, batch=batch, group=group))
    sprites[-1].scale_x = (w - left - right) / regions['c'].width
    sprites[-1].scale_y = (h - top - bottom) / regions['c'].height
    return sprites


class Frame(Widget):
    """A frame widget that can contain other widgets"""
    
    def __init__(self, x, y, width, height, batch=None, group=None, 
                 background_color=None, border_color=None,
                 is_expandable=False, frame_type="frame"):
        super().__init__(x, y, width, height, batch, group)
        self.background_color = background_color or theme.get_color("gui_color")
        self.border_color = border_color or [100, 100, 100, 255]
        self.children = []
        self.is_expandable = is_expandable
        self.frame_type = frame_type
        self._create_background()
        
    def _create_background(self):
        """Create the background using theme images"""
        if self.batch:
            # Try to use theme image first
            frame_theme = theme.theme_data.get(self.frame_type, theme.theme_data.get("frame"))
            img = None
            frame = [8, 8, 8, 8]
            padding = [8, 8, 8, 8]
            if frame_theme and "image" in frame_theme:
                img_name = frame_theme["image"]["source"]
                img = theme.get_image(img_name)
                frame = frame_theme["image"].get("frame", frame)
                padding = frame_theme["image"].get("padding", padding)
            if img:
                self.bg_slices = draw_nine_patch(self.batch, RenderingOrder.gui_background, img, self.x, self.y, self.width, self.height, frame, padding)
                self.bg_sprite = None
                self.bg_rect = None
                self.border_rect = None
            else:
                self.bg_slices = []
                self.bg_sprite = None
                self.bg_rect = Rectangle(
                    self.x, self.y, self.width, self.height,
                    color=self.background_color[:3],
                    batch=self.batch, group=RenderingOrder.gui_background
                )
                self.border_rect = Rectangle(
                    self.x - 1, self.y - 1, self.width + 2, self.height + 2,
                    color=self.border_color[:3],
                    batch=self.batch, group=RenderingOrder.gui_background
                )
            # --- DEBUG: Add a visible red border ---
            self.debug_border = Rectangle(
                self.x, self.y, self.width, self.height,
                color=(255, 0, 0), batch=self.batch, group=RenderingOrder.gui
            )
            self.debug_border.opacity = 128
        else:
            self.bg_slices = []
            self.bg_sprite = None
            self.bg_rect = None
            self.border_rect = None
            self.debug_border = None
        
    def add_child(self, child):
        """Add a child widget"""
        self.children.append(child)
        
    def delete(self):
        """Clean up frame and children"""
        for child in self.children:
            child.delete()
        self.children.clear()
        # Clean up background elements
        for s in getattr(self, 'bg_slices', []):
            s.delete()
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.delete()
        if hasattr(self, 'bg_rect') and self.bg_rect is not None:
            self.bg_rect.delete()
        if hasattr(self, 'border_rect') and self.border_rect is not None:
            self.border_rect.delete()
        if hasattr(self, 'debug_border') and self.debug_border is not None:
            self.debug_border.delete()
        super().delete()

    def get_padding(self):
        frame_theme = theme.theme_data.get(self.frame_type, theme.theme_data.get("frame"))
        if frame_theme and "image" in frame_theme:
            return frame_theme["image"].get("padding", [8, 8, 8, 8])
        return [8, 8, 8, 8]


class Document(Widget):
    """A text document widget"""
    
    def __init__(self, text, x, y, width, height=None, batch=None, group=None, 
                 font_size=12, color=None, multiline=True, is_fixed_size=False):
        super().__init__(x, y, width, height or 100, batch, group)
        self.text = text
        self.font_size = font_size
        self.color = color or theme.get_color("text_color")
        self.multiline = multiline
        self.is_fixed_size = is_fixed_size
        self._create_label()
        
    def _create_label(self):
        """Create the text label"""
        # Use padding if parent is Frame or has get_padding
        pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
        if hasattr(self, 'parent') and hasattr(self.parent, 'get_padding'):
            pad_left, pad_right, pad_top, pad_bottom = self.parent.get_padding()
        x = self.x + pad_left
        y = self.y + self.height - pad_top
        width = self.width - pad_left - pad_right
        height = self.height - pad_top - pad_bottom
        if self.batch:
            if isinstance(self.text, str) and '<' in self.text and '>' in self.text:
                self.label = HTMLLabel(
                    self.text, x=x, y=y,
                    width=width, height=height,
                    batch=self.batch, group=RenderingOrder.gui,
                    anchor_x='left', anchor_y='top'
                )
            else:
                self.label = Label(
                    self.text, x=x, y=y,
                    width=width, height=height,
                    batch=self.batch, group=RenderingOrder.gui,
                    anchor_x='left', anchor_y='top',
                    font_size=self.font_size, color=self.color,
                    multiline=self.multiline
                )
        else:
            self.label = None
            
    def set_text(self, text):
        """Update the text content"""
        self.text = text
        if self.label:
            self.label.delete()
        self._create_label()
        
    def delete(self):
        """Clean up label"""
        if self.label:
            self.label.delete()
        super().delete()


class Button(Widget):
    """A clickable button widget"""
    
    def __init__(self, text, x, y, width, height, batch=None, group=None, 
                 on_click=None, background_color=None, button_type="button"):
        super().__init__(x, y, width, height, batch, group)
        self.text = text
        self.on_click = on_click
        self.background_color = background_color or [150, 150, 150, 255]
        self.button_type = button_type
        self.pressed = False
        self._create_button()
        
    def _create_button(self):
        """Create the button visual elements"""
        if self.batch:
            # Try to use theme image first
            btn_theme = theme.theme_data.get(self.button_type, theme.theme_data.get("button"))
            img = None
            frame = [6, 6, 6, 6]
            padding = [8, 8, 8, 8]
            if btn_theme and "up" in btn_theme and "image" in btn_theme["up"]:
                img_name = btn_theme["up"]["image"]["source"]
                img = theme.get_image(img_name)
                frame = btn_theme["up"]["image"].get("frame", frame)
                padding = btn_theme["up"]["image"].get("padding", padding)
            if img:
                self.bg_slices = draw_nine_patch(self.batch, RenderingOrder.gui_background, img, self.x, self.y, self.width, self.height, frame, padding)
                self.bg_sprite = None
                self.bg_rect = None
            else:
                self.bg_slices = []
                self.bg_sprite = None
                self.bg_rect = Rectangle(
                    self.x, self.y, self.width, self.height,
                    color=self.background_color[:3],
                    batch=self.batch, group=RenderingOrder.gui_background
                )
            # Text label
            self.label = Label(
                self.text, x=self.x + self.width//2, y=self.y + self.height//2,
                batch=self.batch, group=RenderingOrder.gui,
                anchor_x='center', anchor_y='center',
                font_size=12, color=(0, 0, 0, 255)
            )
        else:
            self.bg_slices = []
            self.bg_sprite = None
            self.bg_rect = None
            self.label = None
        
    def on_mouse_press(self, x, y, button, modifiers):
        """Handle mouse press on button"""
        self.pressed = True
        # Change to pressed state
        # TODO: Implement 9-slice for pressed state
        
    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse release on button"""
        if self.pressed and self.contains_point(x, y):
            if self.on_click:
                self.on_click(self)
        self.pressed = False
        # TODO: Restore to normal state for 9-slice
        
    def delete(self):
        """Clean up button"""
        if self.label:
            self.label.delete()
        for s in getattr(self, 'bg_slices', []):
            s.delete()
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.delete()
        if hasattr(self, 'bg_rect') and self.bg_rect is not None:
            self.bg_rect.delete()
        super().delete()

    def get_padding(self):
        btn_theme = theme.theme_data.get(self.button_type, theme.theme_data.get("button"))
        if btn_theme and "up" in btn_theme and "image" in btn_theme["up"]:
            return btn_theme["up"]["image"].get("padding", [8, 8, 8, 8])
        return [8, 8, 8, 8]


class OneTimeButton(Button):
    """A button that can only be clicked once"""
    
    def __init__(self, text, x=0, y=0, width=100, height=30, batch=None, group=None, 
                 on_click=None, background_color=None):
        super().__init__(text, x, y, width, height, batch, group, on_click, background_color, "molecule-button")
        self.is_pressed = False
        
    def on_mouse_release(self, x, y, button, modifiers):
        """Handle mouse release on button"""
        if self.pressed and self.contains_point(x, y):
            self.is_pressed = True
            if self.on_click:
                self.on_click(self)
        self.pressed = False
        # Restore to normal state
        if self.bg_sprite:
            normal_img = theme.get_image("green-button-up.png")
            if normal_img:
                self.bg_sprite.image = normal_img
            
    def change_state(self):
        """Change the button state"""
        self.is_pressed = not self.is_pressed
        
    def get_path(self):
        """Get the button path for theming (compatibility)"""
        path = ["molecule-button"]
        if self.is_pressed:
            path.append('down')
        else:
            path.append('up')
        return path


class Container(Widget):
    """A container widget that can hold multiple widgets"""
    
    def __init__(self, x, y, width, height, batch=None, group=None):
        super().__init__(x, y, width, height, batch, group)
        self.children = []
        self.align = 'left'  # 'left', 'center', 'right'
        
    def add(self, widget):
        """Add a widget to the container"""
        self.children.append(widget)
        self._layout_children()
        
    def remove(self, widget):
        """Remove a widget from the container"""
        if widget in self.children:
            self.children.remove(widget)
            widget.delete()
            self._layout_children()
            
    def _layout_children(self):
        """Layout children widgets"""
        pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
        if hasattr(self, 'get_padding'):
            pad_left, pad_right, pad_top, pad_bottom = self.get_padding()
        elif hasattr(self, 'parent') and hasattr(self.parent, 'get_padding'):
            pad_left, pad_right, pad_top, pad_bottom = self.parent.get_padding()
        current_y = self.y + self.height - pad_top
        for child in self.children:
            if child is None:
                continue
            child.x = self.x + pad_left
            child.width = self.width - pad_left - pad_right
            child.y = self.y + current_y - child.height
            current_y -= child.height
            
            # Handle horizontal alignment
            if self.align == 'center':
                child.x = self.x + (self.width - child.width) // 2
            elif self.align == 'right':
                child.x = self.x + self.width - child.width
            else:  # left
                child.x = self.x
                
    def layout(self):
        self._layout_children()
        for child in self.children:
            if hasattr(child, 'layout'):
                child.layout()
        print(f"[Container] After layout: width={self.width}, height={self.height}")
        for i, child in enumerate(self.children):
            if child:
                print(f"  [Child {i}] x={child.x}, y={child.y}, w={child.width}, h={child.height}")
        super().delete()


class VerticalContainer(Container):
    """A container that arranges widgets vertically"""
    
    def _layout_children(self):
        """Layout children vertically from top to bottom"""
        pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
        if hasattr(self, 'get_padding'):
            pad_left, pad_right, pad_top, pad_bottom = self.get_padding()
        elif hasattr(self, 'parent') and hasattr(self.parent, 'get_padding'):
            pad_left, pad_right, pad_top, pad_bottom = self.parent.get_padding()
        current_y = self.y + self.height - pad_top
        for child in self.children:
            if child is None:
                continue
            child.x = self.x + pad_left
            child.width = self.width - pad_left - pad_right
            child.y = self.y + current_y - child.height
            current_y -= child.height
            
            # Handle horizontal alignment
            if self.align == 'center':
                child.x = self.x + (self.width - child.width) // 2
            elif self.align == 'right':
                child.x = self.x + self.width - child.width
            else:  # left
                child.x = self.x

    def layout(self):
        self._layout_children()
        for child in self.children:
            if hasattr(child, 'layout'):
                child.layout()


class HorizontalContainer(Container):
    """A container that arranges widgets horizontally"""
    
    def _layout_children(self):
        """Layout children horizontally from left to right"""
        pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
        if hasattr(self, 'get_padding'):
            pad_left, pad_right, pad_top, pad_bottom = self.get_padding()
        elif hasattr(self, 'parent') and hasattr(self.parent, 'get_padding'):
            pad_left, pad_right, pad_top, pad_bottom = self.parent.get_padding()
        current_x = self.x + pad_left
        for child in self.children:
            if child is None:
                continue
            child.x = current_x
            child.y = self.y + pad_bottom
            child.height = self.height - pad_top - pad_bottom
            current_x += child.width

    def layout(self):
        self._layout_children()
        for child in self.children:
            if hasattr(child, 'layout'):
                child.layout()


class SectionHeader(Widget):
    """A header widget for sections"""
    
    def __init__(self, text, x=0, y=0, width=200, height=30, batch=None, group=None):
        super().__init__(x, y, width, height, batch, group)
        self.text = text
        self._create_label()
        
    def _create_label(self):
        """Create the header label"""
        if self.batch:
            self.label = Label(
                self.text, x=self.x, y=self.y + self.height//2,
                batch=self.batch, group=RenderingOrder.gui,
                anchor_x='left', anchor_y='center',
                font_size=14, color=(0, 0, 0, 255), bold=True
            )
        else:
            self.label = None
            
    def delete(self):
        """Clean up label"""
        if self.label:
            self.label.delete()
        super().delete()


class FoldingSection(Widget):
    """A collapsible section widget"""
    
    def __init__(self, title, content, x=0, y=0, width=200, height=100, 
                 batch=None, group=None, is_open=True):
        super().__init__(x, y, width, height, batch, group)
        self.title = title
        self.content = content
        self.is_open = is_open
        self._create_widgets()
        
    def _create_widgets(self):
        """Create the section widgets"""
        if self.batch:
            # Header
            self.header = SectionHeader(self.title, self.x, self.y + self.height - 30, 
                                       self.width, 30, self.batch, RenderingOrder.gui)
            # Content (only if open)
            if self.is_open and self.content:
                self.content.x = self.x
                self.content.y = self.y
                self.content.width = self.width
                self.content.height = self.height - 30
        else:
            self.header = None
            
    def delete(self):
        """Clean up section"""
        if self.header:
            self.header.delete()
        if self.content:
            self.content.delete()
        super().delete()


class Scrollable(Widget):
    """A scrollable container widget"""
    
    def __init__(self, content, x=0, y=0, width=200, height=100, 
                 batch=None, group=None, height_limit=None):
        super().__init__(x, y, width, height, batch, group)
        self.content = content
        self.height_limit = height_limit or height
        self.scroll_offset = 0
        self._setup_scrolling()
        
    def _setup_scrolling(self):
        """Setup scrolling functionality"""
        if self.content:
            self.content.x = self.x
            self.content.y = self.y + self.scroll_offset
            self.content.width = self.width
            # Limit content height if needed
            if self.content.height > self.height_limit:
                self.content.height = self.height_limit
                
    def delete(self):
        """Clean up scrollable"""
        if self.content:
            self.content.delete()
        super().delete()


class PopupMessage(Widget):
    """A popup message dialog"""
    
    def __init__(self, text, window, batch, group=None, theme_obj=None, on_escape=None):
        self.window = window
        window_width, window_height = window.get_size()
        
        # Calculate popup size and position
        width = min(400, window_width - 100)
        height = min(200, window_height - 100)
        x = (window_width - width) // 2
        y = (window_height - height) // 2
        
        super().__init__(x, y, width, height, batch, group)
        self.text = text
        self.theme_obj = theme_obj
        self.on_escape = on_escape
        self._create_popup()
        
    def _create_popup(self):
        """Create the popup dialog"""
        if self.batch:
            # Background frame
            self.frame = Frame(self.x, self.y, self.width, self.height, 
                              self.batch, RenderingOrder.gui_background, 
                              background_color=(240, 240, 240, 255),
                              border_color=(100, 100, 100, 255))
            
            # Text content
            self.document = Document(self.text, self.x + 10, self.y + 50, 
                                   self.width - 20, self.height - 100,
                                   self.batch, RenderingOrder.gui)
            
            # Close button
            def close_popup(button):
                self.delete()
                if self.on_escape:
                    self.on_escape(self)
                    
            self.close_button = Button("Close", self.x + self.width//2 - 30, 
                                     self.y + 10, 60, 30, self.batch, RenderingOrder.gui,
                                     on_click=close_popup)
        else:
            self.frame = None
            self.document = None
            self.close_button = None
            
    def delete(self):
        """Clean up popup"""
        if self.frame:
            self.frame.delete()
        if self.document:
            self.document.delete()
        if self.close_button:
            self.close_button.delete()
        super().delete()


class Manager:
    """Manager class to handle GUI layout and positioning"""
    
    def __init__(self, content, window, batch, group=None, anchor='bottom_left', 
                 theme_obj=None, is_movable=False):
        self.content = content
        self.window = window
        self.batch = batch
        self.group = group
        self.anchor = anchor
        self.theme_obj = theme_obj
        self.is_movable = is_movable
        if hasattr(self.content, 'layout'):
            self.content.layout()
        self.update_position()
        
    def update_position(self):
        """Position content based on anchor setting (public)"""
        window_width, window_height = self.window.get_size()
        print(f"[Manager] Anchor: {self.anchor}")
        print(f"[Manager] Window size: {window_width}x{window_height}")
        print(f"[Manager] Content size: {self.content.width}x{self.content.height}")
        if self.anchor == 'bottom_left':
            self.content.x = 10
            self.content.y = 10
        elif self.anchor == 'bottom_right':
            self.content.x = window_width - self.content.width - 10
            self.content.y = 10
        elif self.anchor == 'top_right':
            self.content.x = window_width - self.content.width - 10
            self.content.y = window_height - self.content.height - 10
        elif self.anchor == 'top_left':
            self.content.x = 10
            self.content.y = window_height - self.content.height - 10
        print(f"[Manager] Placing at: x={self.content.x}, y={self.content.y}")

    def delete(self):
        """Clean up manager and content"""
        if self.content:
            self.content.delete()


# Constants for compatibility with old pyglet-gui code
ANCHOR_BOTTOM_LEFT = 'bottom_left'
ANCHOR_BOTTOM_RIGHT = 'bottom_right'
ANCHOR_TOP_RIGHT = 'top_right'
ANCHOR_TOP_LEFT = 'top_left'
HALIGN_LEFT = 'left'
HALIGN_CENTER = 'center'
HALIGN_RIGHT = 'right' 