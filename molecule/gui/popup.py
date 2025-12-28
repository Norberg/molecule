from molecule import RenderingOrder
from .base import Widget
from .frame import Frame
from .document import Document
from .button import Button

class PopupMessage(Widget):
    def __init__(self, text, window, batch, group=None, theme_obj=None, on_escape=None):
        self.window = window
        window_width, window_height = window.get_size()
        width = min(400, window_width - 100)
        height = min(200, window_height - 100)
        x = (window_width - width) // 2
        y = (window_height - height) // 2
        super().__init__(x, y, width, height, batch, group)
        self.text = text
        self.theme_obj = theme_obj
        self.on_escape = on_escape
        self._create_popup()
        self.window.push_handlers(
            on_mouse_press=self.on_mouse_press,
            on_mouse_release=self.on_mouse_release
        )
        self._mouse_press_within = False

    def _create_popup(self):
        if self.batch:
            self.frame = Frame(self.x, self.y, self.width, self.height,
                              self.batch, RenderingOrder.gui_background,
                              background_color=(240, 240, 240, 255),
                              border_color=(100, 100, 100, 255))
            margin_x = 24
            top_margin = 20
            bottom_space_for_button = 60
            doc_height = self.height - top_margin - bottom_space_for_button
            if doc_height < 40:
                doc_height = 40
            self.document = Document(self.text, self.x + margin_x, self.y + self.height - top_margin - doc_height,
                                   self.width - 2*margin_x, doc_height,
                                   self.batch, RenderingOrder.gui)
            def ok_popup(button):
                if self.on_escape:
                    try:
                        self.on_escape()
                    except TypeError:
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
        if self.frame:
            self.frame.delete()
            self.frame = None
        if self.document:
            self.document.delete()
            self.document = None
        if self.close_button:
            self.close_button.delete()
            self.close_button = None
        try:
            self.window.pop_handlers()
        except Exception:
            pass
        super().delete()

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
