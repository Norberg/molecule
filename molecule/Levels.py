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

import pyglet
import pymunk

from molecule import Universe
from molecule import Config
from molecule import CollisionTypes
from molecule import Effects
from molecule import Gui
from molecule import pyglet_util
from molecule import HUD
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

    def init_levels(self):
        filenames = glob.glob(self.path+"/*")
        #files that contains # is disabled
        self.levels = [name for name in filenames if not '#' in name]
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
        return Level(cml, self.window)

    def level_iter(self):
        level = self.next_level()
        while level is not None:
            yield level
            level = self.next_level()

class Level:
    def __init__(self, cml, window):
        self.cml = cml
        self.finished = False
        self.window = window
        self.batch = pyglet.graphics.Batch()
        self.start_time = time.time()
        self.points = 0
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
        hud_x = max_x - 214
        hud_y = offset - 134
        screen_boundaries = [
          pymunk.Segment(self.space.static_body, (-offset, -hud_y), (max_x, -hud_y), thickness),
          pymunk.Segment(self.space.static_body, (-offset, -offset), (-offset, max_y), thickness),
          pymunk.Segment(self.space.static_body, (-offset, max_y), (max_x, max_y), thickness),
          pymunk.Segment(self.space.static_body, (hud_x, max_y), (hud_x, -offset), thickness)
                ]
        for boundary in screen_boundaries:
            boundary.elasticity = 0.95
            boundary.collision_type = CollisionTypes.SCREEN_BOUNDARY
            boundary.layers = CollisionTypes.LAYER_WALL
        self.space.add(*screen_boundaries)
        self.mouse_spring = None
        #Kinematic is working but to much energy in the system
        self.mouse_body = pymunk.Body(body_type = pymunk.Body.KINEMATIC)
        #self.mouse_body = pymunk.Body(mass=0.1, moment=10)

        self.space.add_collision_handler(CollisionTypes.ELEMENT,CollisionTypes.ELEMENT).post_solve=self.element_collision
        self.space.add_collision_handler(CollisionTypes.ELEMENT,CollisionTypes.EFFECT).begin=self.effect_reaction

    def init_pyglet(self):
        self.window.set_handlers(self)

    def init_elements(self):
        self.elements = Universe.create_elements(self.space, self.cml.molecules,
                                          self.batch)

    def init_effects(self):
        self.areas = Effects.create_effects(self.space, self.batch, self.cml.effects)
        self.areas.extend(self.hud.get_effects())

    def init_gui(self):
        self.hud = HUD.HUD(self.window, self.batch, self.space, self.cml, self.create_elements)

    def create_elements(self, elements, pos = None):
        self.elements.extend(Universe.create_elements(self.space, elements,
                                          self.batch, pos))

    def get_colliding_molecules(self, collisions):
        molecules = list()
        for collision in collisions:
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

    def perform_reaction(self, space, key, reaction, collisions, position):
        reactingMolecules = self.get_molecules_in_reaction(collisions, reaction)
        for molecule in reactingMolecules:
            molecule.delete()
        self.create_elements(reaction.products, position)

    def element_collision(self, arbiter, space, data):
        """ Called if two elements collides"""
        a,b = arbiter.shapes
        reacting_areas = list(self.get_affecting_areas(a.body.position))
        #FIXME: this point query return more than just elements. something is wrong with the filter
        pointQuery = space.point_query(a.body.position, 100, shape_filter = pymunk.ShapeFilter(categories = CollisionTypes.ELEMENT))
        collisions = [point.shape for point in pointQuery]
        reaction = self.react(collisions, reacting_areas)
        if reaction != None:
            key = 1 # use 1 as key so only one callback per iteration can trigger
            space.add_post_step_callback(self.perform_reaction, key, reaction, collisions, a.body.position)

    def effect_reaction(self, arbiter, space, data):
        """ Called if an element touches a effect """
        a,b = arbiter.shapes
        molecule = a.molecule
        effect = b.effect
        reaction = effect.react(molecule)
        collisions = [a]
        if reaction != None:
            key = 1 # use 1 as key so only one callback per iteration can trigger
            space.add_post_step_callback(self.perform_reaction, key, reaction, collisions, b.body.position)
        return False

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
        clicked = self.space.point_query_nearest((x,y), 16, shape_filter = pymunk.ShapeFilter(categories = CollisionTypes.LAYER_DRAGGING))
        if (clicked != None and
            clicked.shape.collision_type == CollisionTypes.ELEMENT and
            clicked.shape.molecule.draggable):
            clicked = clicked.shape
            clicked.molecule.set_dragging(True)
            rest_length = self.mouse_body.position.get_distance(clicked.body.position)
            self.mouse_spring = pymunk.PivotJoint(self.mouse_body, clicked.body, (0,0), (0,0))
            self.mouse_spring.error_bias = math.pow(1.0-0.2, 30.0)
            self.space.add(self.mouse_spring)
            self.hud.update_info_text(clicked.molecule.formula)

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
                        molecule.delete()

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
                self.window.close()
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
        self.space.step(1/120.0)
        if self.victory() and self.finished == False:
            Gui.create_popup(self.window, self.batch, "Congratulation, you finished the level",
                             on_escape=self.window.switch_level)
            self.finished = True
        for element in self.elements:
            element.update()
        for area in self.areas:
            area.update()

    def delete(self):
        self.window.remove_handlers(self)
        self.hud.delete()
