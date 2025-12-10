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
from molecule import RenderingOrder
from molecule import pyglet_util

class ScissorGroup(Group):
    """Group that sets GL scissor rect"""
    def __init__(self, x, y, width, height, parent=None):
        super().__init__(parent=parent)
        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)

    def set_state(self):
        gl.glEnable(gl.GL_SCISSOR_TEST)
        gl.glScissor(self.x, self.y, self.width, self.height)

    def unset_state(self):
        gl.glDisable(gl.GL_SCISSOR_TEST)

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return id(self)


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
            "green-button-up.png", "red-button-down.png",
            "vscrollbar.png", "hscrollbar.png"
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

GUI_PADDING = 2

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

    def shift(self, dx, dy):
        """Default shift just moves coordinates; subclasses should override to move visuals."""
        self.x += dx
        self.y += dy

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Handle mouse scroll events"""
        return False


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
    
    # Calculate dimensions for all 9 regions
    # Structure: (name, x_in_img, y_in_img, w_in_img, h_in_img, dest_x, dest_y, dest_w, dest_h)
    
    center_w = img_w - left - right
    center_h = img_h - top - bottom
    
    # Definitions of source regions and destination geometries
    # Note: pyglet image coordinates: (0,0) is bottom-left.
    # get_region(x, y, width, height)
    
    # Rows in image (bottom to top):
    # Bottom row (y=0, h=bottom): BL, B, BR
    # Center row (y=bottom, h=center_h): L, C, R
    # Top row (y=bottom+center_h, h=top): TL, T, TR
    
    # Destination layout (x,y is bottom-left of target area)
    # Rows in destination (bottom to top):
    # Bottom: y=y. h=bottom (fixed) or scaled? Usually corners are fixed size?
    # Actually draw_nine_patch usually scales center and edges, keeps corners fixed.
    # But if target size < corners, they might overlap or shrink.
    # For now assume standard behavior: corners fixed size, edges stretched in one dim, center stretched in both.
    
    parts = []
    
    # Corners
    parts.append(('bl', 0, 0, left, bottom, 
                  x, y, left, bottom))
    parts.append(('br', img_w - right, 0, right, bottom, 
                  x + width - right, y, right, bottom))
    parts.append(('tl', 0, img_h - top, left, top, 
                  x, y + height - top, left, top))
    parts.append(('tr', img_w - right, img_h - top, right, top, 
                  x + width - right, y + height - top, right, top))
                  
    # Edges
    parts.append(('b', left, 0, center_w, bottom, 
                  x + left, y, width - left - right, bottom))
    parts.append(('t', left, img_h - top, center_w, top, 
                  x + left, y + height - top, width - left - right, top))
    parts.append(('l', 0, bottom, left, center_h, 
                  x, y + bottom, left, height - top - bottom))
    parts.append(('r', img_w - right, bottom, right, center_h, 
                  x + width - right, y + bottom, right, height - top - bottom))
                  
    # Center
    parts.append(('c', left, bottom, center_w, center_h,
                  x + left, y + bottom, width - left - right, height - top - bottom))
                  
    sprites = []
    for (name, sx, sy, sw, sh, dx, dy, dw, dh) in parts:
        if sw <= 0 or sh <= 0 or dw <= 0 or dh <= 0:
            continue
            
        region = img.get_region(sx, sy, sw, sh)
        sprite = pyglet.sprite.Sprite(region, x=dx, y=dy, batch=batch, group=group)
        
        # Scale if destination size differs from source size
        if dw != sw:
            sprite.scale_x = dw / sw
        if dh != sh:
            sprite.scale_y = dh / sh
            
        sprites.append(sprite)
            
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
        else:
            self.bg_slices = []
            self.bg_sprite = None
            self.bg_rect = None
            self.border_rect = None
        
    def add_child(self, child):
        """Add a child widget"""
        self.children.append(child)
        child.parent = self
        
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Propagate scroll events to children"""
        # Check if point is inside frame
        if not self.contains_point(x, y):
            return False
            
        for child in reversed(self.children):
            if child and hasattr(child, 'on_mouse_scroll'):
                if child.on_mouse_scroll(x, y, scroll_x, scroll_y):
                    return True
        return False

    def layout(self):
        """Layout children and update background"""
        # Update background positions
        if self.bg_rect is not None:
            self.bg_rect.x = self.x
            self.bg_rect.y = self.y
            self.bg_rect.width = self.width
            self.bg_rect.height = self.height
        if self.border_rect is not None:
            self.border_rect.x = self.x - 1
            self.border_rect.y = self.y - 1
            self.border_rect.width = self.width + 2
            self.border_rect.height = self.height + 2
        
        # Update 9-slice sprites
        if self.bg_slices:
            # We need to re-generate or shift slices. 
            # Since shift is relative, and we have absolute x,y, it's easier to re-create or calculate diff.
            # But shift() method exists. 
            # However, we don't know the previous x,y easily unless we store it.
            # Better to just re-run draw_nine_patch logic or update sprite positions manually.
            # Given the complexity of 9-patch resizing, let's try to update them if size hasn't changed, 
            # or re-create if it has.
            # For now, let's assume size is constant and just update position?
            # No, Container might resize Frame.
            # So we should probably recreate the background if size/pos changes.
            # Or call _create_background() again?
            # _create_background() cleans up old slices.
            self._create_background()

        pad_left, pad_right, pad_top, pad_bottom = self.get_padding()
        for child in self.children:
            if child is None:
                continue
            child.x = self.x + pad_left
            child.y = self.y + pad_bottom
            # Only resize if not fixed size (if that attribute exists)
            if not getattr(child, 'is_fixed_size', False):
                child.width = self.width - pad_left - pad_right
                child.height = self.height - pad_top - pad_bottom
            
            if hasattr(child, 'layout'):
                child.layout()
        
    def delete(self):
        """Clean up frame and children"""
        for child in self.children:
            child.delete()
        self.children.clear()
        # Clean up background elements
        for s in self.bg_slices:
            s.delete()
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
            self.bg_sprite.delete()
        if hasattr(self, 'bg_rect') and self.bg_rect is not None:
            self.bg_rect.delete()
        if hasattr(self, 'border_rect') and self.border_rect is not None:
            self.border_rect.delete()
        super().delete()

    def get_padding(self):
        frame_theme = theme.theme_data.get(self.frame_type, theme.theme_data.get("frame"))
        if frame_theme and "image" in frame_theme:
            return frame_theme["image"].get("padding", [8, 8, 8, 8])
        return [8, 8, 8, 8]

    # --- Position helpers -------------------------------------------------
    def shift(self, dx, dy):
        """Shift frame and all its visual primitives by (dx, dy)."""
        self.x += dx
        self.y += dy
        # Rectangles (always defined or None)
        if self.bg_rect is not None:
            self.bg_rect.x += dx
            self.bg_rect.y += dy
        if self.border_rect is not None:
            self.border_rect.x += dx
            self.border_rect.y += dy
        # 9-slice sprites
        for s in self.bg_slices:
            s.x += dx
            s.y += dy
        # Children
        for c in self.children:
            if c is None:
                continue
            if hasattr(c, 'shift'):
                c.shift(dx, dy)
            else:
                c.x += dx
                c.y += dy

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.contains_point(x, y):
            return False
        for child in reversed(self.children):
            if child and hasattr(child, 'on_mouse_press'):
                if child.on_mouse_press(x, y, button, modifiers):
                    return True
        return False

    def on_mouse_release(self, x, y, button, modifiers):
        # Only forward to children under the cursor
        for child in reversed(self.children):
            if child and child.contains_point(x, y) and hasattr(child, 'on_mouse_release'):
                if child.on_mouse_release(x, y, button, modifiers):
                    return True
        return False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.contains_point(x, y):
            return False
        for child in reversed(self.children):
            if child and hasattr(child, 'on_mouse_drag'):
                if child.on_mouse_drag(x, y, dx, dy, buttons, modifiers):
                    return True
        return False


class Document(Widget):
    """A text document widget"""
    
    def __init__(self, text, x, y, width, height=None, batch=None, group=None, 
                 font_size=12, color=None, multiline=True, is_fixed_size=False, autosize_height=False):
        super().__init__(x, y, width, height or 100, batch, group)
        self.text = text
        self.font_size = font_size
        self.color = color or theme.get_color("text_color")
        self.multiline = multiline
        self.is_fixed_size = is_fixed_size
        self.autosize_height = autosize_height
        self._create_label()
        
    def _create_label(self):
        """Create the text label"""
        # Use padding if parent is Frame or has get_padding
        pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
        x = self.x + pad_left
        y = self.y + self.height - pad_top
        width = self.width - pad_left - pad_right
        height = self.height - pad_top - pad_bottom
        if self.batch:
            # Use self.group if set (e.g. by Scrollable), otherwise default to RenderingOrder.gui
            group = self.group or RenderingOrder.gui
            
            if isinstance(self.text, str) and '<' in self.text and '>' in self.text:
                self.label = HTMLLabel(
                    self.text, x=x, y=y,
                    width=width, height=height,
                    batch=self.batch, group=group,
                    anchor_x='left', anchor_y='top',
                    multiline=self.multiline
                )
            else:
                self.label = Label(
                    self.text, x=x, y=y,
                    width=width, height=height,
                    batch=self.batch, group=group,
                    anchor_x='left', anchor_y='top',
                    font_size=self.font_size, color=self.color,
                    multiline=self.multiline
                )
            
            if self.autosize_height:
                self.height = self.label.content_height + pad_top + pad_bottom
                # Re-position label because y depends on height
                y = self.y + self.height - pad_top
                self.label.y = y
                self.label.height = self.height - pad_top - pad_bottom
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
    
    def shift(self, dx, dy):
        self.x += dx
        self.y += dy
        if self.label:
            self.label.x += dx
            self.label.y += dy

    def layout(self):
        """Update label position based on widget position"""
        if self.label:
            # Re-calculate position including padding
            pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
            
            x = self.x + pad_left
            y = self.y + self.height - pad_top
            width = self.width - pad_left - pad_right
            height = self.height - pad_top - pad_bottom
            
            self.label.x = x
            self.label.y = y
            self.label.width = width
            self.label.height = height


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
        """Create button visuals; prebuild up/down slices and toggle visibility."""
        if not self.batch:
            self.bg_slices = []
            self.bg_sprite = None
            self.bg_rect = None
            self.label = None
            return

        btn_theme = theme.theme_data.get(self.button_type, theme.theme_data.get("button")) or {}
        self._up_conf = (btn_theme.get("up") or {}).get("image")
        self._down_conf = (btn_theme.get("down") or {}).get("image")
        self._up_text_color = (btn_theme.get("up") or {}).get("text_color", [0,0,0,255])
        self._down_text_color = (btn_theme.get("down") or {}).get("text_color", self._up_text_color)

        def build_slices(conf):
            if not conf:
                return None
            img = theme.get_image(conf.get("source", ""))
            if not img:
                return None
            frame = conf.get("frame", [6,6,6,6])
            padding = conf.get("padding", [8,8,8,8])
            slices = draw_nine_patch(self.batch, RenderingOrder.gui_background, img, self.x, self.y, self.width, self.height, frame, padding)
            return {'slices': slices, 'frame': frame, 'padding': padding}

        self._up_slices = build_slices(self._up_conf)
        self._down_slices = build_slices(self._down_conf)

        self.bg_rect = None
        if not self._up_slices:
            # fallback flat rectangle
            self.bg_rect = Rectangle(
                self.x, self.y, self.width, self.height,
                color=self.background_color[:3],
                batch=self.batch, group=RenderingOrder.gui_background
            )
        # hide down state initially
        if self._down_slices:
            for s in self._down_slices['slices']:
                s.visible = False
        self.label = Label(
            self.text, x=self.x + self.width//2, y=self.y + self.height//2,
            batch=self.batch, group=RenderingOrder.gui,
            anchor_x='center', anchor_y='center',
            font_size=12, color=tuple(self._up_text_color)
        )
        
    def on_mouse_press(self, x, y, button, modifiers):
        """Switch to down visuals if present."""
        if not self.contains_point(x, y):
            return False
        self.pressed = True
        if self._down_slices:
            if self._up_slices:
                for s in self._up_slices['slices']:
                    s.visible = False
            for s in self._down_slices['slices']:
                s.visible = True
            if self.label:
                self.label.color = tuple(self._down_text_color)
        elif self.bg_rect is not None:
            if not hasattr(self, '_orig_color'):
                self._orig_color = tuple(self.bg_rect.color)
            r,g,b = self._orig_color
            self.bg_rect.color = (max(0,int(r*0.7)), max(0,int(g*0.7)), max(0,int(b*0.7)))
        return True
        
    def on_mouse_release(self, x, y, button, modifiers):
        """Restore up visuals and fire click if inside."""
        was_pressed = self.pressed
        self.pressed = False
        if self._down_slices and self._up_slices:
            for s in self._down_slices['slices']:
                s.visible = False
            for s in self._up_slices['slices']:
                s.visible = True
            if self.label:
                self.label.color = tuple(self._up_text_color)
        elif self.bg_rect is not None and hasattr(self, '_orig_color'):
            self.bg_rect.color = self._orig_color
        if was_pressed and self.contains_point(x, y) and self.on_click:
            self.on_click(self)
        
    def delete(self):
        """Clean up button"""
        if self.label:
            self.label.delete()
        for s in self.bg_slices if hasattr(self, 'bg_slices') and self.bg_slices else []:
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
    
    def shift(self, dx, dy):
        self.x += dx
        self.y += dy
        if self.label:
            self.label.x += dx
            self.label.y += dy
        def shift_slices(conf):
            if not conf:
                return
            for s in conf['slices']:
                s.x += dx
                s.y += dy
        shift_slices(self._up_slices)
        shift_slices(self._down_slices)
        if self.bg_rect is not None:
            self.bg_rect.x += dx
            self.bg_rect.y += dy

    def layout(self):
        """Update button visuals"""
        # Re-create button to handle size/pos changes
        self._create_button()


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
        if hasattr(self, 'bg_sprite') and self.bg_sprite:
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
        if widget:
            widget.parent = self
        self.children.append(widget)
        self.layout()
        
    def remove(self, widget):
        """Remove a widget from the container"""
        if widget in self.children:
            self.children.remove(widget)
            widget.delete()
            self.layout()
            
    def _layout_children(self):
        """Layout children widgets"""
        pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
        if hasattr(self, 'get_padding'):
            pad_left, pad_right, pad_top, pad_bottom = self.get_padding()
        current_y = self.y + self.height - pad_top
        for child in self.children:
            if child is None:
                continue
            child.x = self.x + pad_left
            child.width = self.width - pad_left - pad_right
            child.y = current_y - child.height
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

    def shift(self, dx, dy):
        super().shift(dx, dy)
        for child in self.children:
            if child:
                if hasattr(child, 'shift'):
                    child.shift(dx, dy)
                else:
                    child.x += dx
                    child.y += dy

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Propagate scroll events to children"""
        # Check if point is inside container
        if not self.contains_point(x, y):
            return False
            
        for child in reversed(self.children):
            if child and hasattr(child, 'on_mouse_scroll'):
                if child.on_mouse_scroll(x, y, scroll_x, scroll_y):
                    return True
        return False


    def on_mouse_press(self, x, y, button, modifiers):
        if not self.contains_point(x, y):
            return False
        for child in reversed(self.children):
            if child and hasattr(child, 'on_mouse_press'):
                if child.on_mouse_press(x, y, button, modifiers):
                    return True
        return False

    def on_mouse_release(self, x, y, button, modifiers):
        # Only forward to children under the cursor
        for child in reversed(self.children):
            if child and child.contains_point(x, y) and hasattr(child, 'on_mouse_release'):
                if child.on_mouse_release(x, y, button, modifiers):
                    return True
        return False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.contains_point(x, y):
            return False
        for child in reversed(self.children):
            if child and hasattr(child, 'on_mouse_drag'):
                if child.on_mouse_drag(x, y, dx, dy, buttons, modifiers):
                    return True
        return False

class VerticalContainer(Container):
    """A container that arranges widgets vertically"""
    
    def _layout_children(self):
        """Layout children vertically from top to bottom"""
        pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
        if hasattr(self, 'get_padding'):
            pad_left, pad_right, pad_top, pad_bottom = self.get_padding()
        
        # Vertical spacing between children
        spacing = getattr(self, 'spacing', 4)  # Default 4 pixels spacing
        
        current_y = self.y + self.height - pad_top
        for i, child in enumerate(self.children):
            if child is None:
                continue
            child.x = self.x + pad_left
            child.width = self.width - pad_left - pad_right
            child.y = current_y - child.height
            #child.y = self.y + current_y - child.height
            current_y -= child.height
            # Add spacing after each child except the last one
            if i < len(self.children) - 1:
                current_y -= spacing
            
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
    
    def __init__(self, x, y, width, height, batch=None, group=None, spacing=0):
        super().__init__(x, y, width, height, batch, group)
        self.spacing = spacing

    def _layout_children(self):
        """Layout children horizontally from left to right"""
        pad_left, pad_right, pad_top, pad_bottom = 0, 0, 0, 0
        if hasattr(self, 'get_padding'):
            pad_left, pad_right, pad_top, pad_bottom = self.get_padding()
        current_x = self.x + pad_left
        for child in self.children:
            if child is None:
                continue
            child.x = current_x
            child.y = self.y + pad_bottom
            child.height = self.height - pad_top - pad_bottom
            current_x += child.width + self.spacing

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
        self.scrollbar_width = 16 # updated to match probable theme width or keep 10? Theme region is 16.
        
        # Create scissor group for clipping
        if self.batch:
            self.scissor_group = ScissorGroup(x, y, width, height, parent=group)
        else:
            self.scissor_group = None

        self._setup_scrolling()
        
        # Scrollbar visuals (lists of sprites or single rects)
        self.scrollbar_bg_items = []
        self.scrollbar_handle_items = []

    def _setup_scrolling(self):
        """Setup scrolling functionality"""
        if self.content:
            if self.scissor_group:
                self.content.group = self.scissor_group
                if hasattr(self.content, '_create_label'):
                    if hasattr(self.content, 'label') and self.content.label:
                        self.content.label.delete()
                    self.content._create_label()
                elif hasattr(self.content, 'children'):
                    pass

            self.content.x = self.x
            self.content.y = self.y + self.height - self.content.height + self.scroll_offset
            self.content.width = self.width - self.scrollbar_width
            
    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if not self.contains_point(x, y):
            return False
            
        content_height = self.content.height if self.content else 0
        view_height = self.height
        
        if content_height <= view_height:
            return False
            
        max_scroll = content_height - view_height
        
        scroll_speed = 20
        self.scroll_offset -= scroll_y * scroll_speed
        
        if self.scroll_offset < 0:
            self.scroll_offset = 0
        if self.scroll_offset > max_scroll:
            self.scroll_offset = max_scroll
            
        self._update_positions()
        return True

    def on_mouse_press(self, x, y, button, modifiers):
        if not self.contains_point(x, y):
            return False
        if self.content and hasattr(self.content, 'on_mouse_press'):
            return self.content.on_mouse_press(x, y, button, modifiers)
        return False

    def on_mouse_release(self, x, y, button, modifiers):
        if self.content and hasattr(self.content, 'on_mouse_release'):
            return self.content.on_mouse_release(x, y, button, modifiers)
        return False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.contains_point(x, y):
            return False
        if self.content and hasattr(self.content, 'on_mouse_drag'):
            return self.content.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        return False

    def _create_scrollbar_part(self, part_name, x, y, width, height):
        """Create scrollbar visual part (knob or bar)"""
        if not self.batch:
            return []
            
        items = []
        # Try to load from theme
        sb_theme = theme.theme_data.get("vscrollbar", {})
        part_theme = sb_theme.get(part_name)
        
        if part_theme and "image" in part_theme:
            img_conf = part_theme["image"]
            img = theme.get_image(img_conf.get("source", ""))
            if img:
                region_rect = img_conf.get("region")
                if region_rect:
                    # Extract region from texture
                    # region: [x, y, w, h]
                    # Pyglet image regions are usually from bottom-left? 
                    # theme.json structure implies [x, y, w, h] from top-left usually in texture atlases, 
                    # but Pyglet is bottom-left origin.
                    # Looking at draw_nine_patch usage in this file:
                    # regions['tl'] = img.get_region(0, img_h - top, left, top)
                    # It seems to assume standard GL coordinates (bottom-up).
                    # But texture packing tools often use top-down.
                    # Let's assume the helper handles it or the region coords are correct for pyglet.
                    # Wait, theme.json just has "region": [0, 0, 16, 16].
                    # Let's try finding the image directly if possible?
                    # The get_image returns full image. 
                    # We can use .get_region(x, y, width, height).
                    # Assuming coords in theme.json are compatible with pyglet.image.AbstractImage.get_region
                    img = img.get_region(*region_rect)
                
                frame = img_conf.get("frame", [0, 0, 0, 0])
                padding = img_conf.get("padding", [0, 0, 0, 0])
                
                # Check if we should use draw_nine_patch
                # If frame is all 0, it wraps center stretch.
                # draw_nine_patch handles this fine (stretches center).
                items = draw_nine_patch(self.batch, self.group, img, x, y, width, height, frame, padding)
                return items

        # Fallback to Rectangle
        color = (200, 200, 200, 255) if part_name == "bar" else (100, 100, 100, 255)
        rect = Rectangle(x, y, width, height, color=color, batch=self.batch, group=self.group)
        return [rect]
        
    def _update_positions(self):
        if self.content:
            # Update content width first (keeping scrollbar width reserved)
            self.content.width = self.width - self.scrollbar_width
            
            self.content.y = self.y + self.height - self.content.height + self.scroll_offset
            self.content.x = self.x

            if hasattr(self.content, 'layout'):
                self.content.layout()
            
            if self.scissor_group:
                self.scissor_group.x = int(self.x)
                self.scissor_group.y = int(self.y)
                self.scissor_group.width = int(self.width)
                self.scissor_group.height = int(self.height)
                
            # Clear old visuals
            for item in self.scrollbar_bg_items:
                item.delete()
            self.scrollbar_bg_items = []
            
            for item in self.scrollbar_handle_items:
                item.delete()
            self.scrollbar_handle_items = []
            
            # Create new visuals if needed
            should_show_scrollbar = self.content.height > self.height
            if should_show_scrollbar:
                # Background (Bar)
                self.scrollbar_bg_items = self._create_scrollbar_part("bar", 
                    self.x + self.width - self.scrollbar_width, self.y,
                    self.scrollbar_width, self.height)
                
                # Handle (Knob)
                ratio = self.height / self.content.height
                handle_height = max(20, self.height * ratio)
                max_scroll = self.content.height - self.height
                scroll_ratio = self.scroll_offset / max_scroll if max_scroll > 0 else 0
                
                track_height = self.height
                scrollable_track = track_height - handle_height
                handle_y = self.y + self.height - handle_height - (scrollable_track * scroll_ratio)
                
                self.scrollbar_handle_items = self._create_scrollbar_part("knob",
                    self.x + self.width - self.scrollbar_width, handle_y,
                    self.scrollbar_width, handle_height)

    def layout(self):
        """Layout content"""
        self._update_positions()
        
    def shift(self, dx, dy):
        self.x += dx
        self.y += dy
        self._update_positions()
        
    def delete(self):
        """Clean up scrollable"""
        if self.content:
            self.content.delete()
        for item in self.scrollbar_bg_items:
            item.delete()
        for item in self.scrollbar_handle_items:
            item.delete()
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
        # Register event handlers (no ESC handling)
        self.window.push_handlers(
            on_mouse_press=self.on_mouse_press,
            on_mouse_release=self.on_mouse_release
        )
        self._mouse_press_within = False
        
    def _create_popup(self):
        """Create the popup dialog"""
        if self.batch:
            # Background frame
            self.frame = Frame(self.x, self.y, self.width, self.height, 
                              self.batch, RenderingOrder.gui_background, 
                              background_color=(240, 240, 240, 255),
                              border_color=(100, 100, 100, 255))
            
            # Text content with nicer margins
            margin_x = 24
            top_margin = 20
            bottom_space_for_button = 60
            doc_height = self.height - top_margin - bottom_space_for_button
            if doc_height < 40:
                doc_height = 40
            self.document = Document(self.text, self.x + margin_x, self.y + self.height - top_margin - doc_height, 
                                   self.width - 2*margin_x, doc_height,
                                   self.batch, RenderingOrder.gui)
            
            # Ok button (legacy behaviour: triggers on_escape callback)
            def ok_popup(button):
                # First invoke callback (no args expected) then delete popup
                if self.on_escape:
                    try:
                        self.on_escape()
                    except TypeError:
                        # Fallback if old signature expected popup
                        self.on_escape(self)
                self.delete()

            button_width = 100
            self.close_button = Button("Ok", self.x + (self.width - button_width)//2,
                                     self.y + 16, button_width, 32, self.batch, RenderingOrder.gui,
                                     on_click=ok_popup)
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
        # Remove our handlers (safe even if already removed)
        try:
            self.window.remove_handlers(self.on_mouse_press, self.on_mouse_release)
        except Exception:
            pass
        super().delete()

    # --- Event Handling ---
    def _inside_button(self, x, y):
        return (self.close_button and
                self.close_button.x <= x <= self.close_button.x + self.close_button.width and
                self.close_button.y <= y <= self.close_button.y + self.close_button.height)

    def on_mouse_press(self, x, y, button, modifiers):
        if self._inside_button(x, y):
            if hasattr(self.close_button, 'on_mouse_press'):
                self.close_button.on_mouse_press(x, y, button, modifiers)
            self._mouse_press_within = True
            return True
        # Swallow clicks inside popup so they don't leak to game
        if self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height:
            return True
        return False

    def on_mouse_release(self, x, y, button, modifiers):
        if self._mouse_press_within and self._inside_button(x, y):
            if hasattr(self.close_button, 'on_mouse_release'):
                self.close_button.on_mouse_release(x, y, button, modifiers)
            self._mouse_press_within = False
            return True
        self._mouse_press_within = False
        return False

    # ESC ska inte påverka popupen längre – ingen on_key_press


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
        
        # Register for events
        self.window.push_handlers(self)
        
    def update_position(self):
        """Position content based on anchor setting (public)"""
        window_width, window_height = self.window.get_size()
        old_x, old_y = self.content.x, self.content.y
        # Determine target anchor position
        if self.anchor == 'bottom_left':
            target_x = GUI_PADDING
            target_y = GUI_PADDING
        elif self.anchor == 'bottom_right':
            target_x = window_width - self.content.width - GUI_PADDING
            target_y = GUI_PADDING
        elif self.anchor == 'top_right':
            target_x = window_width - self.content.width - GUI_PADDING
            target_y = window_height - self.content.height - GUI_PADDING
        elif self.anchor == 'top_left':
            target_x = GUI_PADDING
            target_y = window_height - self.content.height - GUI_PADDING
        else:  # default fall back
            target_x = old_x
            target_y = old_y

        dx = target_x - old_x
        dy = target_y - old_y
        if dx == 0 and dy == 0:
            return

        # Content must implement shift now
        self.content.shift(dx, dy)
        print(f"[Manager] Anchor {self.anchor}: moved content by ({dx},{dy}) to x={self.content.x}, y={self.content.y}")

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        """Handle mouse scroll events"""
        if self.content and hasattr(self.content, 'on_mouse_scroll'):
            return self.content.on_mouse_scroll(x, y, scroll_x, scroll_y)
        return False

    def on_mouse_press(self, x, y, button, modifiers):
        if self.content and hasattr(self.content, 'on_mouse_press'):
            return self.content.on_mouse_press(x, y, button, modifiers)
        return False

    def on_mouse_release(self, x, y, button, modifiers):
        if self.content and hasattr(self.content, 'on_mouse_release'):
            return self.content.on_mouse_release(x, y, button, modifiers)
        return False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.content and hasattr(self.content, 'on_mouse_drag'):
            return self.content.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        return False

    def delete(self):
        """Clean up manager and content"""
        self.window.remove_handlers(self)
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