import pyglet
import os
from molecule.gui import (
    Manager, Container, HorizontalContainer, VerticalContainer, Document, Frame,
    Button, SpriteWidget, AbsoluteContainer, ANCHOR_CENTER, HALIGN_LEFT, GUI_PADDING
)
from . import RenderingOrder

BIOMES = [
    ("Laboratory", [
        "data/levels/01-Water.cml",
        "data/levels/02-Methane-1.cml",
        "data/levels/03-Methane-2.cml",
        "data/levels/04-Methane-3.cml",
    ]),
    ("Acid Zone", [
        "data/levels/05-Nitration-Nitrobenzene.cml",
        "data/levels/06-Sodium-sulfate.cml",
        "data/levels/10-Sulfur-1.cml",
        "data/levels/11-Sulfur-2.cml",
        "data/levels/16-Acid-production-1-Sulfuric-acid.cml",
        "data/levels/17-Acid-production-2-Nitric-acid.cml",
        "data/levels/18-Golden-rain.cml",
    ]),
    ("Desert", [
        "data/levels/07-Urea.cml",
        "data/levels/08-Calcium-carbonate.cml",
        "data/levels/09-Magnesium-1.cml",
        "data/levels/12-Iron-1.cml",
        "data/levels/13-Phosphorus-pentoxide.cml",
        "data/levels/14-Soda-1-Leblanc-process.cml",
        "data/levels/15-Soda-2-Solvay-process.cml",
    ]),
    ("Cold Zone", [
        "data/levels/19-Fireworks-Copper.cml",
        "data/levels/20-Organic-Addition-1.cml",
        "data/levels/21-Organic-Addition-2.cml",
        "data/levels/22-Organic-Substitution-1.cml",
        "data/levels/23-Organic-Substitution-2.cml",
        "data/levels/24-Organic-Substitution-3.cml",
    ]),
    ("Forest Biome", [
        "data/levels/30-Organic-Multistep-1-Paracetamol.cml",
        "data/levels/31-Organic-Multistep-2-Aspirin.cml",
        "data/levels/32-Organic-Multistep-3-3-Bromonitrobenzene.cml",
        "data/levels/33-Organic-Industrial-1-Cativa.cml",
        "data/levels/34-Organic-Reduction-Aniline.cml",
        "data/levels/35-Organic-Multistep-4-Sulfanilamide.cml",
        "data/levels/37-Petrochemical-1-Benzene.cml",
        "data/levels/39-Petrochemical-1-MTBE.cml",
        "data/levels/40-Life-1-DAMN.cml",
        "data/levels/41-Life-2-Adenine.cml",
        "data/levels/42-Life-3-Guanine.cml",
        "data/levels/43-Life-4-Formaldehyde.cml",
    ])
]

class LevelMenu:
    def __init__(self, window, levels, on_level_selected):
        self.window = window
        self.levels = levels
        self.on_level_selected = on_level_selected
        self.batch = pyglet.graphics.Batch()
        
        # Load background
        bg_path = os.path.join("molecule", "theme", "level_menu_bg.png")
        self.bg_image = pyglet.image.load(bg_path)
        self.bg_sprite = pyglet.sprite.Sprite(self.bg_image, batch=self.batch, group=RenderingOrder.background)
        
        # Scale background to fit window
        self.bg_sprite.scale_x = window.width / self.bg_image.width
        self.bg_sprite.scale_y = window.height / self.bg_image.height
        
        # Load icons
        self.check_img = pyglet.image.load(os.path.join("molecule", "theme", "checkmark.png"))
        self.lock_img = pyglet.image.load(os.path.join("molecule", "theme", "lock.png"))
        
        self.state = "MAIN"
        self.selected_biome = None
        self.view_manager = None
        
        self.refresh()
        self.window.push_handlers(self)

    def refresh(self):
        if self.view_manager:
            self.view_manager.delete()
        
        width, height = self.window.get_size()
        
        if self.state == "MAIN":
            self.init_main_view(width, height)
        else:
            self.init_biome_view(width, height)

    def init_main_view(self, width, height):
        root = AbsoluteContainer(0, 0, width, height)
        
        ISLANDS = {
            "Laboratory": (0.24, 0.81),
            "Acid Zone": (0.76, 0.81),
            "Desert": (0.23, 0.32),
            "Cold Zone": (0.50, 0.54),
            "Forest Biome": (0.77, 0.29)
        }
        
        prev_biome_started = True 
        
        for biome_name, level_paths in BIOMES:
            rel_x, rel_y = ISLANDS.get(biome_name, (0.5, 0.5))
            abs_x = int(rel_x * width)
            abs_y = int(rel_y * height)
            
            # Progress summary
            total = len(level_paths)
            done = sum(1 for p in level_paths if self.levels.is_completed(p))
            is_unlocked = prev_biome_started
            
            frame_w = 160
            frame_h = 75
            fx = abs_x - frame_w // 2
            fy = abs_y - frame_h - 15
            
            # Clamp to screen
            fx = max(10, min(fx, width - frame_w - 10))
            fy = max(10, min(fy, height - frame_h - 10))
            
            frame = Frame(fx, fy, frame_w, frame_h, self.batch, RenderingOrder.gui_background,
                         background_color=[0, 0, 0, 180], border_color=[255, 255, 255, 30])
            
            content = VerticalContainer(0, 0, frame_w - 16, frame_h - 16, spacing=4)
            content.align = 'center'
            
            title_color = "gold" if is_unlocked else "gray"
            title = Document(f"<h4 align='center' color='{title_color}'>{biome_name}</h4>", 
                            0, 0, frame_w - 24, 24, self.batch)
            title.is_fixed_size = True
            content.add(title, do_layout=False)
            
            prog_text = f"<p align='center' color='white' size='2'>{done}/{total} Completed</p>"
            prog = Document(prog_text, 0, 0, frame_w - 24, 18, self.batch)
            prog.is_fixed_size = True
            content.add(prog, do_layout=False)
            
            def make_click(name):
                return lambda btn: self.on_biome_clicked(name)

            if is_unlocked:
                btn = Button("ENTER", 0, 0, 90, 22, self.batch, on_click=make_click(biome_name), button_type="molecule-button")
            else:
                btn = Button("LOCKED", 0, 0, 90, 22, self.batch)
                btn.background_color = [40, 40, 40, 150]
            
            content.add(btn, do_layout=False)
            frame.add(content)
            frame.layout()
            root.add(frame)
            
            # Unlock next biome if at least one level is done in this one
            prev_biome_started = (done > 0)
            
        # push_handlers=False because LevelMenu itself is the handler and dispatches manually
        # anchor=None because we already positioned the root container at (0,0) with correct size
        self.view_manager = Manager(root, window=self.window, batch=self.batch, 
                                     is_movable=False, push_handlers=False, anchor=None)

    def init_biome_view(self, width, height):
        root = AbsoluteContainer(0, 0, width, height)
        
        biome_name = self.selected_biome
        level_paths = next(lvls for name, lvls in BIOMES if name == biome_name)
        
        num_levels = len(level_paths)
        item_h = 24
        spacing = 4
        title_h = 30
        back_h = 32
        
        calc_height = title_h + 10 + (num_levels * (item_h + spacing)) + back_h + 10
        frame_width = 300
        
        fx = width // 2 - frame_width // 2
        fy = height // 2 - calc_height // 2
        
        frame = Frame(fx, fy, frame_width, calc_height + 20, self.batch, RenderingOrder.gui_background,
                     background_color=[0, 0, 0, 200], border_color=[255, 215, 0, 80])
        
        content = VerticalContainer(0, 0, frame_width - 24, calc_height, spacing=spacing)
        content.align = 'center'
        
        title = Document(f"<h3 align='center' color='gold'>{biome_name}</h3>", 0, 0, frame_width - 40, title_h, self.batch)
        title.is_fixed_size = True
        content.add(title, do_layout=False)
        
        prev_done = True
        for path in level_paths:
            level_name = os.path.basename(path).replace(".cml", "")
            display_name = level_name.split("-", 1)[1] if "-" in level_name else level_name
            is_done = self.levels.is_completed(path)
            is_unlocked = prev_done
            
            row = HorizontalContainer(0, 0, frame_width - 40, item_h, spacing=6)
            
            icon_img = self.check_img if is_done else (self.lock_img if not is_unlocked else None)
            if icon_img:
                icon_w = SpriteWidget(icon_img, 0, 0, 18, 18, self.batch, RenderingOrder.gui)
                row.add(icon_w, do_layout=False)
            else:
                row.add(Container(0, 0, 18, 18), do_layout=False)
            
            def make_lvl_click(p):
                return lambda btn: self.on_level_selected(p)
                
            if is_unlocked:
                btn = Button(display_name, 0, 0, frame_width - 80, item_h, self.batch, 
                           on_click=make_lvl_click(path), button_type="molecule-button")
            else:
                btn = Button(display_name, 0, 0, frame_width - 80, item_h, self.batch)
                btn.background_color = [30, 30, 30, 180]
            
            row.add(btn, do_layout=False)
            content.add(row, do_layout=False)
            prev_done = is_done
            
        def go_back(btn):
            self.state = "MAIN"
            self.refresh()
            
        back_btn = Button("BACK TO MAP", 0, 0, 160, back_h, self.batch, on_click=go_back, button_type="molecule-button")
        content.add(back_btn, do_layout=False)
        
        frame.add(content)
        frame.layout()
        root.add(frame)
        
        self.view_manager = Manager(root, window=self.window, batch=self.batch, 
                                     is_movable=False, push_handlers=False, anchor=None)

    def on_biome_clicked(self, name):
        self.selected_biome = name
        self.state = "BIOME"
        self.refresh()

    def on_draw(self):
        self.window.clear()
        self.batch.draw()
        
    def on_mouse_press(self, x, y, button, modifiers):
        if self.view_manager:
            return self.view_manager.on_mouse_press(x, y, button, modifiers)
        return False

    def on_mouse_release(self, x, y, button, modifiers):
        if self.view_manager:
            return self.view_manager.on_mouse_release(x, y, button, modifiers)
        return False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.view_manager:
            return self.view_manager.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
        return False

    def on_mouse_motion(self, x, y, dx, dy):
        if self.view_manager:
            return self.view_manager.on_mouse_motion(x, y, dx, dy)
        return False

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        if self.view_manager:
            return self.view_manager.on_mouse_scroll(x, y, scroll_x, scroll_y)
        return False

    def delete(self):
        self.window.remove_handlers(self)
        if self.view_manager:
            self.view_manager.delete()
        self.bg_sprite.delete()
