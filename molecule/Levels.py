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

import pyglet
import pymunk

from molecule import Universe
from molecule import Config
from molecule import CollisionTypes
from molecule import Effects
from molecule import Gui
from libcml import Cml




class Levels:
    def __init__(self, path, start_level = 1, window = None):
        self.path = path
        self.window = window
        self.init_levels()
        self.current_level = start_level - 2

    def init_levels(self):
        filenames = glob.glob(self.path+"/*")
        #files that contains # is disabled
        self.levels = [name for name in filenames if not '#' in name]
        self.levels.sort()
    
    def next_level(self):
        self.current_level += 1
        if self.current_level >= len(self.levels):
            return None
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
        self.victory = False
        self.window = window
        self.batch = pyglet.graphics.Batch()
        self.init_chipmunk()
        self.init_elements()
        self.init_effects()
        self.init_gui()
    
    def init_chipmunk(self):
        self.space = pymunk.Space()
        self.space.idle_speed_threshold = 0.5
        #self.space.collision_slop = 0.05
        #self.space.collision_bias = math.pow(1.0 - 0.3, 60.0)
        #self.space.gravity = (0.0, -500.0)
        thickness = 100
        offset = thickness
        max_x, max_y = map(sum, zip(self.window.get_size(),(offset,offset)))
        screen_boundaries = [
          pymunk.Segment(self.space.static_body, (-offset,-offset), (max_x, -offset), thickness),
          pymunk.Segment(self.space.static_body, (-offset, -offset), (-offset, max_y), thickness),
          pymunk.Segment(self.space.static_body, (-offset, max_y), (max_x, max_y), thickness),
          pymunk.Segment(self.space.static_body, (max_x, max_y), (max_x, -offset), thickness)
                ]
        for boundary in screen_boundaries:
            boundary.elasticity = 0.95
            boundary.collision_type = CollisionTypes.SCREEN_BOUNDARY
        self.space.add(screen_boundaries)
    
    def init_elements(self):    
        self.elements = Universe.create_elements(self.space, self.cml.molecules,
                                          self.batch)

    def init_effects(self):
        new_effects = list()
        for effect in self.cml.effects:
            if effect.title == "Fire":
                x = effect.x2
                y = effect.y2
                value = effect.value
                fire = Effects.Fire(self.space, self.batch,
                                    (x,y), value)
                new_effects.append(fire)
            elif effect.title == "WaterBeaker":
                x = effect.x2
                y = effect.y2
                water = Effects.Water_Beaker(self.space, self.batch,
                                             (x, y))
                new_effects.append(water)
        self.areas = new_effects

    def init_gui(self):
        chapters = [("Hint", self.cml.hint)]
        Gui.create_folding_description(self.window,self.batch, "Objective",
                                      self.cml.objective, chapters)


    def create_elements(self, elements, pos = None):
        self.elements.extend(Universe.create_elements(self.space, elements,
                                          self.batch, pos))

    def get_colliding_molecules(self, collisions):
        molecules = list()
        for collision in collisions:
            if collision["shape"].collision_type == CollisionTypes.ELEMENT:
                #each atom in the molecule can have 1 entry in the collision
                #map, make sure that the molecule is only added once.
                molecule = collision["shape"].molecule
                if not molecule in molecules:
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

    def perform_reaction(self, key, reaction, collisions, position):
        reactingMolecules = self.get_molecules_in_reaction(collisions, reaction)
        for molecule in reactingMolecules:
            molecule.delete()
        self.create_elements(reaction.products, position)
        self.check_victory()    
    
    def element_collision(self, space, arbiter):
        """ Called if two elements collides"""
        a,b = arbiter.shapes
        reacting_areas = list(self.get_affecting_areas(a.body.position))
        collisions = space.nearest_point_query(a.body.position, 100)
        reaction = self.react(collisions, reacting_areas)
        if reaction != None:
            key = 1 # use 1 as key so only one callback per iteration can trigger 
            space.add_post_step_callback(self.perform_reaction, key, reaction, collisions, a.body.position)

    def effect_reaction(self, space, arbiter):
        """ Called if an element touches a effect """
        a,b = arbiter.shapes
        molecule = a.molecule
        effect = b.effect
        reaction = effect.react(molecule)
        collisions = [{"shape" : a}]
        if reaction != None:
            key = 1 # use 1 as key so only one callback per iteration can trigger 
            space.add_post_step_callback(self.perform_reaction, key, reaction, collisions, b.body.position)    
        return False

    def get_affecting_areas(self, position):
        """Return all areas that have a affect on position"""
        shapes = self.space.point_query(position)
        for shape in shapes:
            if shape.collision_type == CollisionTypes.EFFECT:
                yield shape.effect

    def update(self):
        """Update pos of all included elements"""
        for element in self.elements:
            element.update()
        for area in self.areas:
            area.update()

    def reset(self):
        self.__init__(self.cml, self.window)

    def check_victory(self):
        to_check = list(self.cml.victory_condition)
        for element in self.elements:
            if element.formula in to_check:
                to_check.remove(element.formula)
        
        if len(to_check) == 0:
            self.victory = True
            return True
        else:
            return False
