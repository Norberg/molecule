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
import glob
import math
import time
import json
import os

import pyglet
import pymunk

from molecule import Universe
from molecule import Config
from molecule import CollisionTypes
from molecule import Effects
from molecule import Gui
from molecule import pyglet_util
from molecule import HUD
from molecule.gui import GUI_PADDING
from molecule.emitters import Emitters
from libcml import Cml

class Levels:
    def __init__(self, path, start_level = 1, window = None):
        self.path = path
        self.window = window
        self.init_levels()
        self.current_level = None
        for i, level in enumerate(self.levels):
            levelIndex = int(level.strip("data/levels/").split("-")[0])
            if levelIndex == start_level:
                self.current_level = i
                break
        if self.current_level is None:
            raise Exception(f"Requested level {start_level} not found!")
        elif self.current_level > 0:
            print("Starting on level %s" % self.levels[self.current_level])
        self.load_progress()

    def load_progress(self):
        self.completed_levels = set()
        if os.path.exists("progress.json"):
            with open("progress.json", "r") as f:
                try:
                    data = json.load(f)
                    self.completed_levels = set(data.get("completed", []))
                except:
                    pass

    def save_progress(self):
        with open("progress.json", "w") as f:
            json.dump({"completed": sorted(list(self.completed_levels))}, f)

    def mark_completed(self, level_path):
        self.completed_levels.add(level_path)
        self.save_progress()

    def is_completed(self, level_path):
        return level_path in self.completed_levels

    def init_levels(self):
        # Only include real level definition files (.cml)
        pattern = self.path + "/*.cml"
        filenames = glob.glob(pattern)
        # files that contains # are disabled
        self.levels = [name for name in filenames if '#' not in name]
        self.levels.sort()

    def next_level(self):
        self.current_level += 1
        if self.current_level >= len(self.levels):
            return None
        return self.get_current_level()

    def get_current_level(self):
        path = self.levels[self.current_level]
        cml = Cml.Level()
        cml.parse(path)
        return Level(cml, self.window, path)

    def level_iter(self):
        level = self.next_level()
        while level is not None:
            yield level
            level = self.next_level()

class Level:
    def __init__(self, cml, window, path):
        self.cml = cml
        self.path = path
        self.finished = False
        self.window = window
        self.batch = pyglet.graphics.Batch()
        self.start_time = time.time()
        self.points = 0
        self.reaction_log = []
        self.emitters = []
        self.victory_popup = None
        self.hud = None
        Config.current.zoom = self.cml.zoom
        self.init_chipmunk()
        self.init_pyglet()
        self.init_elements()
        self.init_gui()
        self.init_effects()

    def init_chipmunk(self):
        self.space = pymunk.Space()
        self.space.idle_speed_threshold = 0.5
        thickness = 1000
        offset = thickness
        game_area = self.window.get_size()

        max_x, max_y = map(sum, zip(game_area,(offset,offset)))
        hud_x = max_x - (HUD.HUD.VERTICAL_HUD_WIDTH + GUI_PADDING)
        hud_y = offset - HUD.HUD.HEIGHT
        screen_boundaries = [
          pymunk.Segment(self.space.static_body, (-offset, -hud_y), (max_x, -hud_y), thickness),
          pymunk.Segment(self.space.static_body, (-offset, -offset), (-offset, max_y), thickness),
          pymunk.Segment(self.space.static_body, (-offset, max_y), (max_x, max_y), thickness),
          pymunk.Segment(self.space.static_body, (hud_x, max_y), (hud_x, -offset), thickness)
                ]
        for boundary in screen_boundaries:
            boundary.elasticity = 0.95
            boundary.collision_type = CollisionTypes.SCREEN_BOUNDARY
            boundary.filter = CollisionTypes.SCREEN_BOUNDARY_FILTER
        self.space.add(*screen_boundaries)
        self.mouse_spring = None
        #Kinematic is working but to much energy in the system
        self.mouse_body = pymunk.Body(body_type = pymunk.Body.KINEMATIC)
        #self.mouse_body = pymunk.Body(mass=0.1, moment=10)

        # Pymunk >=7 uses on_collision instead of add_collision_handler. We attach
        # a post_solve callback for element/element collisions that may trigger reactions.
        self.space.on_collision(
            CollisionTypes.ELEMENT,
            CollisionTypes.ELEMENT,
            post_solve=self.element_collision,
        )
        # Dwell-time tracking for element/effect collisions (molecule_id,effect_id)->start_time
        self._effect_collision_times = {}
        self.space.on_collision(
            CollisionTypes.ELEMENT,
            CollisionTypes.EFFECT,
            begin=self.effect_reaction,      # start timing
            pre_solve=self.effect_reaction,  # check dwell while overlapping
            separate=self.effect_reaction_separate,
        )

    def init_pyglet(self):
        self.window.push_handlers(self)

    def init_elements(self):
        self.elements = Universe.create_elements(self.space, self.cml.molecules,
                                          self.batch)

    def init_effects(self):
        self.areas = Effects.create_effects(
            self.space,
            self.batch,
            self.cml.effects,
            emitters=self.emitters,
            consume_molecule_cb=self.consume_molecule,
        )
        self.areas.extend(self.hud.get_effects())

    def consume_molecule(self, molecule):
        """Callback from effects when a molecule is consumed, returnes true if used for victory condition"""
        for area in self.areas:
            if isinstance(area, Effects.VictoryInventory):
                return area.put_element(molecule)
        raise Exception("No VictoryInventory area to consume molecule into")

    def init_gui(self):
        self.hud = HUD.HUD(self.window, self.batch, self.space, self.cml, self.create_elements)

    def create_elements(self, elements, pos = None):
        self.elements.extend(Universe.create_elements(self.space, elements,
                                          self.batch, pos))

    def get_colliding_molecules(self, collisions):
        molecules = list()
        for collision in collisions:
            #TODO: Should be possible to filter collision type earlier
            if collision.collision_type == CollisionTypes.ELEMENT:
                molecule = collision.molecule
                #each atom in the molecule can have 1 entry in the collision
                #map, make sure that the molecule is only added once.
                if not molecule in molecules and molecule.can_react():
                    molecules.append(molecule)
        return molecules

    def is_molecule_part_of_reactants(self, molecule, reactants):
        """
        check if the molecule is part of the reactants,
        and if it is remove itself from the list of reactants
        """
        if molecule.state_formula in reactants:
            reactants.remove(molecule.state_formula)
            return True

    def get_molecules_in_reaction(self, collisions, reaction):
        """ return all molecules included in the reaction """
        reactants = list(reaction.reactants)
        molecules = list()
        collidingMolecules = self.get_colliding_molecules(collisions)
        for molecule in collidingMolecules:
            if self.is_molecule_part_of_reactants(molecule, reactants):
                molecules.append(molecule)
        return molecules

    def react(self, collisions, reacting_areas):
        collidingMolecules = self.get_colliding_molecules(collisions)
        reactingForumlas = list(map((lambda m: m.state_formula), collidingMolecules))
        return Universe.universe.react(reactingForumlas, reacting_areas)

    def perform_reaction(self, reaction, collisions, position):
        if len(collisions) == 1:
            print(f"self.perform_reaction(): {reaction.reactants} -> {reaction.products} with only one reacting molecule")
            reactingMolecules = [collisions[0].molecule]
            if collisions[0].molecule.is_deleted():
                print(f"self.perform_reaction(): reactants {reaction.reactants} is already deleted")
                return
        else:
            reactingMolecules = self.get_molecules_in_reaction(collisions, reaction)
        self.add_to_reaction_log(reaction.cml)
        if len(reactingMolecules) < 1:
            print(f"self.perform_reaction(): {reaction.reactants} -> {reaction.products} without any reacting molecules")
            reactingMolecules = self.get_molecules_in_reaction(collisions, reaction)
            return
        for molecule in reactingMolecules:
            self.delete_molecule(molecule)
        new_elements = Universe.create_elements(self.space, reaction.products, self.batch, position)
        self.elements.extend(new_elements)
        print("Reaction products:", reaction.products)
        for mol in new_elements:
            base = mol.formula
            emitter_name = mol.current_state.emitter
            if emitter_name:
                emitter = Emitters.spawn_reaction_emitter(emitter_name, self.batch, position)
                if emitter:
                    print(f"Emitter trigger: product {mol.state_formula} -> {emitter_name} at {position}")
                    self.emitters.append(emitter)
                elif Config.current.DEBUG:
                    print(f"Emitter suppressed (no reaction autospawn): {emitter_name} for {mol.state_formula}")

    def add_to_reaction_log(self, reaction):
        self.points += 1
        self.reaction_log.append(reaction)

    def element_collision(self, arbiter, space, data):
        """ Called if two elements collides"""
        a, b = arbiter.shapes
        pos = a.body.position
        reacting_areas = list(self.get_affecting_areas(pos))

        def perform_query(distance):
            query = space.point_query(pos, distance, shape_filter=pymunk.ShapeFilter(categories=CollisionTypes.ELEMENT))
            colls = [point.shape for point in query]
            reaction = self.react(colls, reacting_areas)
            return colls, reaction

        collisions, reaction = perform_query(100)
        if reaction is not None:
            self.perform_reaction(reaction, collisions, pos)
            return

        # If we have many collideing molecule we increase the search area to make sure we
        # find all elements if its a big reaction
        collidingMolecules = [molecule.state_formula for molecule in self.get_colliding_molecules(collisions)]
        bigReactionThreshold = 8
        if a.molecule != b.molecule and len(collidingMolecules) >= bigReactionThreshold:
            collisions, reaction = perform_query(300)
            if reaction is not None and len(reaction.reactants) >= bigReactionThreshold:
                self.perform_reaction(reaction, collisions, pos)

    def effect_reaction(self, arbiter, space, data):
        """Called when an element touches an effect; only react after 1s continuous contact."""
        a, b = arbiter.shapes
        molecule = a.molecule
        effect = b.effect
        key = (id(molecule), id(effect))
        now = time.time()
        dwell_required = 1.0
        # First contact: start timer
        if key not in self._effect_collision_times:
            self._effect_collision_times[key] = now
            return True
        # Check dwell time
        if (now - self._effect_collision_times[key]) < dwell_required:
            return True
        # Enough time: remove key so it triggers only once
        self._effect_collision_times.pop(key, None)
        # Custom effect reaction first
        reaction = effect.react(molecule)

        # If the effect did not supply a reaction, attempt a normal reactor-based
        # reaction with a single reactant + this effect (enables decomposition
        # without requiring self-collision of the molecule's own atoms).
        if reaction is None:
            reaction = Universe.universe.react([molecule.state_formula], [effect])
        if reaction is not None:
            self.perform_reaction(reaction, [a], b.body.position)
            return False
        return True

    def effect_reaction_separate(self, arbiter, space, data):
        a, b = arbiter.shapes
        molecule = a.molecule
        effect = b.effect
        self._effect_collision_times.pop((id(molecule), id(effect)), None)
        return True

    def get_affecting_areas(self, position):
        """Return all areas that have a affect on reactions in the area """
        for area in self.get_effect_supporting("reaction"):
            if area.inside(position):
                yield area

    def get_time(self):
        return time.time() - self.start_time

    def get_points(self):
        return self.points

    def victory(self):
        return self.hud.horizontal.victory.victory()

    def limit_pos_to_screen(self, x, y):
        x = max(0,x)
        y = max(0,y)
        w, h = self.window.get_size()
        x = min(w,x)
        y = min(h,y)
        return x,y

    def get_effect_supporting(self, support):
        for effect in self.areas:
            if effect.supports(support):
                yield effect

    def on_mouse_press(self, x, y, button, modifiers):
        self.handle_element_pressed(x, y)
        def create_elements_cb(elements):
            self.create_elements(elements, (x,y))
        for action in self.get_effect_supporting("action"):
            if action.clicked((x,y)):
                action.on_click(create_elements_cb)

    def handle_element_pressed(self, x, y):
        if self.mouse_spring != None:
            self.handle_element_released(None, None, None, None)
        self.mouse_body.position = (x, y)
        clicked = self.space.point_query_nearest((x,y), 16, shape_filter=CollisionTypes.ELEMENT_PICK_FILTER)
        if (clicked is None or clicked.shape.collision_type != CollisionTypes.ELEMENT):
            return
        mol = clicked.shape.molecule
        if self.cml.aqueous_not_draggable and mol.current_state.short == "aq":
            return
        shape = clicked.shape
        shape.molecule.set_dragging(True)
        rest_length = self.mouse_body.position.get_distance(shape.body.position)
        self.mouse_spring = pymunk.PivotJoint(self.mouse_body, shape.body, (0,0), (0,0))
        self.mouse_spring.error_bias = math.pow(1.0-0.2, 30.0)
        self.space.add(self.mouse_spring)
        self.hud.update_info_text(shape.molecule.formula)

    def on_mouse_release(self, x, y, button, modifiers):
        self.handle_element_released(x, y, button, modifiers)
        for action in self.get_effect_supporting("action"):
            if action.is_clicked == True:
                action.on_release()

    def handle_element_released(self, x, y, button, modifiers):
        if self.mouse_spring != None:
            self.mouse_spring.b.velocity = (0,0)
            molecule = self.mouse_spring.b.molecule
            molecule.set_dragging(False)
            self.space.remove(self.mouse_spring)
            self.mouse_spring = None
            for effect in self.get_effect_supporting("put"):
                if effect.clicked((x,y)):
                    if effect.put_element(molecule):
                        self.delete_molecule(molecule)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x,y = self.limit_pos_to_screen(x,y)
        self.mouse_body.position = (x, y)

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.M:
            import objgraph
            objgraph.show_growth()
            m  = objgraph.by_type("Molecule")
            print ("nr of Molecule:", len(m))
            #for n in m:
            #    objgraph.show_backrefs(n)
        elif symbol == pyglet.window.key.ESCAPE:
                self.window.show_menu()
        elif symbol == pyglet.window.key.S:
            Gui.create_popup(self.window, self.batch, "Skipping level, Cheater!",
                             on_escape=self.window.switch_level)
        elif symbol == pyglet.window.key.R:
            self.window.reset_level()
        elif symbol == pyglet.window.key.D:
            self.window.DEBUG_GRAPHICS = not self.window.DEBUG_GRAPHICS
        elif symbol == pyglet.window.key.H:
            hint = self.window.level.cml.hint
            Gui.create_popup(self.window, self.batch, hint)

    def update(self):
        dt = 1/120.0
        self.space.step(dt)

        for element in self.elements:
            element.update()
        for area in self.areas:
            area.update()
        if self.finished == False and self.victory():
            print("Victory")
            self.window.levels.mark_completed(self.path)
            self.victory_popup = Gui.create_popup(self.window, self.batch, "Congratulation, you finished the level",
                             on_escape=self.window.switch_level)
            print("Victory popup created")
            self.finished = True

        self.update_emitters(dt)

    def update_emitters(self, dt):
        alive_emitters = []
        for emitter in self.emitters:
            if emitter.update(dt):
                alive_emitters.append(emitter)
            else:
                emitter.delete()
        # Remove dead emitters without creating a new list
        self.emitters[:] = alive_emitters

    def delete_molecule(self, molecule):
        if molecule in self.elements:
            self.elements.remove(molecule)
        else:
            print(f"Warning: Attempted to delete a molecule not in the list: {molecule}")
        molecule.delete()


    def delete(self):
        if self.hud:
            self.hud.delete()
        self.window.remove_handlers(self)
        if self.victory_popup:
            self.victory_popup.delete()
