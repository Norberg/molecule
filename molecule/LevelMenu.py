import pyglet
import os

from molecule.gui import (
    Manager, Container, HorizontalContainer, VerticalContainer, Document, Frame,
    Button, SpriteWidget, AbsoluteContainer, ANCHOR_CENTER, HALIGN_LEFT, GUI_PADDING,
    Scrollable
)
from . import RenderingOrder
from molecule import Config

from libcml import Cml

def load_pages():
    campaign = Cml.Campaign()
    path = os.path.join("data", "levels", "campaign.cml")
    try:
        campaign.parse(path)
        return campaign.pages
    except Exception as e:
        print(f"Error loading campaign.cml: {e}")
        return []

PAGES = load_pages()


class LevelMenu:
    def __init__(self, window, levels, on_level_selected, start_at_map=False):
        self.window = window
        self.levels = levels
        self.on_level_selected = on_level_selected
        self.batch = pyglet.graphics.Batch()
        
        # Load background
        bg_path = os.path.join("molecule", "theme", "level_menu_bg_v2.png")
        self.bg_image = pyglet.image.load(bg_path)
        self.bg_sprite = pyglet.sprite.Sprite(self.bg_image, batch=self.batch, group=RenderingOrder.background)
        
        # Scale background to fit window
        self.bg_sprite.scale_x = window.width / self.bg_image.width
        self.bg_sprite.scale_y = window.height / self.bg_image.height
        
        # Load icons
        self.star_img = pyglet.image.load(os.path.join("molecule", "theme", "star.png"))
        self.play_img = pyglet.image.load(os.path.join("molecule", "theme", "play.png"))
        self.lock_img = pyglet.image.load(os.path.join("molecule", "theme", "lock_fancy.png"))
        
        self.state = "MAIN"
        if self.levels.player_id is None:
            self.state = "PLAYER"
        self.selected_biome = None
        
        # Determine initial state based on current level
        if not start_at_map:
            try:
                current_level_path = self.levels.levels[self.levels.current_level]
                for page in PAGES:
                    for b_name, b_icon, b_paths in page:
                        if any(os.path.abspath(p) == os.path.abspath(current_level_path) for p in b_paths):
                            self.selected_biome = b_name
                            self.state = "BIOME"
                            break
                    if self.selected_biome: break
            except:
                pass

        self.page_index = 0
        # If we found a biome, make sure we are on the right page
        if self.selected_biome:
            for i, page in enumerate(PAGES):
                if any(b[0] == self.selected_biome for b in page):
                    self.page_index = i
                    break

        self.view_manager = None
        
        self.refresh()
        self.window.push_handlers(self)

    def refresh(self):
        if self.view_manager:
            self.view_manager.delete()
        
        width, height = self.window.get_size()
        
        if self.state == "MAIN":
            self.init_main_view(width, height)
        elif self.state == "BIOME":
            self.init_biome_view(width, height)
        elif self.state == "PLAYER":
            self.init_player_selection_view(width, height)

    def init_main_view(self, width, height):
        root = AbsoluteContainer(0, 0, width, height)
        
        # 5 fixed island positions relative to screen (x, y)
        ISLAND_POSITIONS = [
            (0.25, 0.75),
            (0.75, 0.75),
            (0.50, 0.50),
            (0.25, 0.25),
            (0.75, 0.25)
        ]
        
        current_page = PAGES[self.page_index]
        prev_biome_started = True 
        
        for i, (biome_name, icon_file, level_paths) in enumerate(current_page):
            if i >= len(ISLAND_POSITIONS): break
            
            rel_x, rel_y = ISLAND_POSITIONS[i]
            abs_x = int(rel_x * width)
            abs_y = int(rel_y * height)
            
            # Load and draw island sprite
            try:
                island_img = pyglet.image.load(os.path.join("img", "campaign", icon_file))
                island_img.anchor_x = island_img.width // 2
                island_img.anchor_y = island_img.height // 2 - 70
                island_sprite = SpriteWidget(island_img, abs_x, abs_y, 0, 0, self.batch, RenderingOrder.gui_background)
                
                # Scale sprite if needed (assuming 128x128 placeholders, maybe scale up slightly)
                island_sprite.scale_x = 1.5
                island_sprite.scale_y = 1.5
                
                root.add(island_sprite) 
            except Exception as e:
                print(f"Failed to load island {icon_file}: {e}")

            # Progress summary
            total = len(level_paths)
            done = sum(1 for p in level_paths if self.levels.is_completed(p))
            is_unlocked = prev_biome_started
            
            frame_w = 220
            frame_h = 90
            fx = abs_x - frame_w // 2
            fy = abs_y - frame_h // 2 - 80 # Position below the island
            
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
            
        # Navigation Buttons
        nav_y = 50
        
        if self.page_index > 0:
            def prev_page(btn):
                self.page_index -= 1
                self.refresh()
            prev_btn = Button("<< PREV PAGE", 50, nav_y, 150, 40, self.batch, on_click=prev_page, button_type="molecule-button")
            root.add(prev_btn)
            
        if self.page_index < len(PAGES) - 1:
            def next_page(btn):
                self.page_index += 1
                self.refresh()
            next_btn = Button("NEXT PAGE >>", width - 200, nav_y, 150, 40, self.batch, on_click=next_page, button_type="molecule-button")
            root.add(next_btn)

        # Exit Button
        def on_exit(btn):
            pyglet.app.exit()
        
        exit_btn = Button("EXIT GAME", width - 150, height - 70, 120, 40, self.batch, on_click=on_exit, button_type="molecule-button")
        root.add(exit_btn)

        # Change Player Button
        player_name = Config.current.player or "Unknown"
        def change_player(btn):
            self.state = "PLAYER"
            self.refresh()
        
        player_btn = Button(f"PLAYER: {player_name.upper()}", 50, height - 70, 250, 40, self.batch, on_click=change_player, button_type="molecule-button")
        root.add(player_btn)

        self.view_manager = Manager(root, window=self.window, batch=self.batch, 
                                     is_movable=False, push_handlers=False, anchor=None)

    def init_biome_view(self, width, height):
        root = AbsoluteContainer(0, 0, width, height)
        
        biome_name = self.selected_biome
        
        # Flatten biomes list to find the selected one
        all_biomes = [biome for page in PAGES for biome in page]
        icon_file, level_paths = next((icon, lvls) for name, icon, lvls in all_biomes if name == biome_name)
        
        num_levels = len(level_paths)
        item_h = 32
        spacing = 4
        title_h = 40
        back_h = 40
        content_spacing = 8
        calc_height = title_h + 10 + (num_levels * (item_h + spacing)) + back_h + 30
        frame_width = 440
        
        fx = width // 2 - frame_width // 2
        fy = height // 2 - calc_height // 2
        
        # Add Campaign Image
        icon_path = os.path.join("img", "campaign", icon_file)
        camp_img = pyglet.image.load(icon_path)
        # Anchor center-bottom for natural placement
        camp_img.anchor_x = camp_img.width // 2
        camp_img.anchor_y = 0
        
        # Positioned above/behind the top of the frame
        camp_sprite = SpriteWidget(camp_img, width // 2, fy + calc_height - 10, 
                                  camp_img.width, camp_img.height, 
                                  self.batch, RenderingOrder.gui_background)
        root.add(camp_sprite)

        frame = Frame(fx, fy, frame_width, calc_height + 20, self.batch, RenderingOrder.gui_background,
                     background_color=[15, 15, 20, 240], border_color=[255, 215, 0, 120],
                     frame_type="none")
        
        content = VerticalContainer(0, 0, frame_width - 24, calc_height, spacing=content_spacing)
        content.align = 'center'
        
        # Title Header with background
        header_h = title_h + 20
        header = Frame(fx, fy + calc_height + 15 - header_h, frame_width, header_h, self.batch, RenderingOrder.gui_background,
                      background_color=[20, 20, 30, 255], border_color=[255, 215, 0, 180], frame_type="none")
        root.add(header)
        
        # Center title in header
        title_y_offset = (header_h - title_h) // 2
        title = Document(f"<h3 align='center'><font color='#FFD700'>{biome_name}</font></h3>", 
                        0, -title_y_offset, frame_width - 40, title_h, self.batch)
        title.is_fixed_size = True
        content.add(title, do_layout=False)
        
        # Spacer for visual balance
        spacer = Document("", 0, 0, frame_width, 10, self.batch)
        content.add(spacer, do_layout=False)
        
        prev_done = True
        for path in level_paths:
            level_name = os.path.basename(path).replace(".cml", "")
            display_name = level_name.split("-", 1)[1] if "-" in level_name else level_name
            is_done = self.levels.is_completed(path)
            is_unlocked = prev_done
            
            row = HorizontalContainer(0, 0, frame_width - 40, item_h, spacing=10)
            
            icon_size = 32
            
            if is_done:
                icon_img = self.star_img
            elif is_unlocked:
                icon_img = self.play_img
            else:
                icon_img = self.lock_img
                
            icon_w = SpriteWidget(icon_img, 0, 0, icon_size, icon_size, self.batch, RenderingOrder.gui)
            row.add(icon_w, do_layout=False)
            
            def make_lvl_click(p):
                return lambda btn: self.on_level_selected(p)
                
            btn_text = display_name
            if len(display_name) > 22:
                btn_text = f"<font size='2'>{display_name}</font>"
                
            if is_unlocked:
                btn = Button(btn_text, 0, 0, frame_width - 80, item_h, self.batch, 
                           on_click=make_lvl_click(path), button_type="molecule-button")
            else:
                btn = Button(btn_text, 0, 0, frame_width - 80, item_h, self.batch)
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

    def init_player_selection_view(self, width, height):
        root = AbsoluteContainer(0, 0, width, height)
        
        frame_w = 400
        players = self.levels.persistence.get_players()
        item_h = 40
        header_h = 60
        footer_h = 80
        # Ensure we have at least some height for the list even if empty
        list_h = max(100, min(len(players) * (item_h + 4), height - 300))
        calc_height = header_h + list_h + footer_h + 20
        
        fx = width // 2 - frame_w // 2
        fy = height // 2 - calc_height // 2
        
        frame = Frame(fx, fy, frame_w, calc_height, self.batch, RenderingOrder.gui_background,
                     background_color=[20, 20, 30, 240], border_color=[255, 215, 0, 150])
        
        content = VerticalContainer(0, 0, frame_w - 24, calc_height - 20, spacing=10)
        content.align = 'center'
        
        title = Document("<h3><font color='#FFD700' align='center'>SELECT PLAYER</font></h3>", 0, 0, frame_w - 40, 40, self.batch)
        content.add(title, do_layout=False)
        
        # Player list container
        player_list_cont = VerticalContainer(0, 0, frame_w - 60, max(1, len(players) * (item_h + 4)), spacing=4)
        player_list_cont.align = 'center'
        
        def make_player_click(name):
            return lambda btn: self.on_player_selected(name)

        for p_name in players:
            btn = Button(p_name, 0, 0, frame_w - 80, item_h, self.batch, on_click=make_player_click(p_name), button_type="molecule-button")
            player_list_cont.add(btn, do_layout=False)
            
        scrollable = Scrollable(player_list_cont, 0, 0, frame_w - 40, list_h, self.batch)
        content.add(scrollable, do_layout=False)
        
        def on_new_player(btn):
            # Use random name for now as we don't have text input
            import random
            adjectives = ["Cool", "Smart", "Swift", "Atomic", "Brave"]
            nouns = ["Chemist", "Scientist", "Player", "Pro", "Expert"]
            name = f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(10, 99)}"
            self.on_player_selected(name)

        new_btn = Button("NEW PLAYER", 0, 0, 200, 40, self.batch, on_click=on_new_player, button_type="molecule-button")
        content.add(new_btn, do_layout=False)
        
        frame.add(content)
        frame.layout()
        root.add(frame)
        
        self.view_manager = Manager(root, window=self.window, batch=self.batch, 
                                      is_movable=False, push_handlers=False, anchor=None)

    def on_player_selected(self, name):
        self.levels.set_player(name)
        self.state = "MAIN"
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
