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
import random
import math

import pyglet
from pyglet import gl
from pymunk.vec2d import Vec2d
import pymunk

from molecule import pyglet_util
from molecule import CollisionTypes
from molecule import RenderingOrder
from libcml import Cml
from libcml import CachedCml
from libreact import Reaction

SPRITE_SIZE = 96.0
DEFAULT_SIZE = 32.0
SCALE_FACTOR = DEFAULT_SIZE/SPRITE_SIZE
SPRITE_RADIUS = SPRITE_SIZE/2
BOND_LENGTH_FACTOR = 1.4
    
class Molecule:
    def __init__(self, formula_with_state, space, batch, pos=None):
        self.space = space
        self.batch = batch
        formula, state = Reaction.split_state(formula_with_state)
        self.formula = formula
        if pos is None:
            pos = (random.randint(10, 600), random.randint(10, 400))
        self.pos = pos
        self.cml = CachedCml.getMolecule(formula)
        self.cml.normalize_pos()
        self.current_state = self.cml.get_state(state)
        if self.current_state is None:
            raise Exception("did not find state for:" + formula_with_state)
        self.create_atoms()

    def __repr__(self):
        return "Molecule<%s>" % (self.state_formula)
            
    @property
    def enthalpy(self):
        """Return enthalpy(aka H) for current state"""
        return self.state.enthalpy

    @property
    def entropy(self):
        """Return entropy(aka S) for current state"""
        return self.state.entropy

    @property
    def state(self):
        """Return current state"""
        return self.current_state

    @property
    def state_formula(self):
        return self.formula + "(%s)" % self.current_state.short

    @property
    def draggable(self):
        return self.current_state.short != "aq"

    def change_state(self, new_state):
        """new_state: shortform of wanted state"""
        if not self.try_change_state(new_state):
            raise Exception("Tried to change: " + self.formula + " to non existing state:" + new_state)

    def try_change_state(self, new_state):
        """new_state: shortform of wanted state"""
        state = self.cml.get_state(new_state)
        if state is None:
            return False
        else:
            self.current_state = state
            return True    
    
    def toAqueous(self):
        if self.try_change_state("aq"):
            return self.state.ions
    
    def create_atoms(self):
        self.atoms = dict()
        for atom in self.cml.atoms.values():
            new = Atom(atom.elementType, atom.formalCharge,
                       self.space, self.batch, self, self.pos)
            self.atoms[atom.id] = new
        self.create_bonds()

    def get_bond_lenght(self, bond):
        rA = CachedCml.getMolecule(bond.atomA.elementType).property["Radius"]
        rB = CachedCml.getMolecule(bond.atomB.elementType).property["Radius"]
        return (rA + rB) * SPRITE_RADIUS * SCALE_FACTOR * BOND_LENGTH_FACTOR


    def create_bonds(self):
        self.joints = list()
        self.vertexes = list()
        for bond in self.cml.bonds:
            #bond.atomA.pos
            #bond.atomB.pos
            atomA = self.atoms[bond.atomA.id]
            atomB = self.atoms[bond.atomB.id]
            bond_length = self.get_bond_lenght(bond)    
            joint = pymunk.SlideJoint(atomA.body, atomB.body, (0,0), (0,0),
                                      10, bond_length)
            joint.error_bias = math.pow(1.0-0.1, 30.0)
            joint.bonds = bond.bonds 
            self.joints.append(joint)
            self.space.add(joint)
        for joint in self.joints:
            pv1 = joint.a.position
            pv2 = joint.b.position 
            line = (pv1.x, pv1.y, pv2.x, pv2.y)
            color = (90,90,90)
            group = RenderingOrder.elements
            bonds = joint.bonds
            size = 2 * bonds
            v = self.batch.add(size, pyglet.gl.GL_LINES, group,
                               ('v2f', line * bonds),
                               ('c3B', color * size))
            
            self.vertexes.append(v)

    def set_dragging(self, value):
        for atom in self.atoms.values():
            if value:
                atom.shape.layers = CollisionTypes.LAYER_DRAGGING
            else:
                atom.shape.layers = CollisionTypes.LAYER_ALL

    def update(self):
        for atom in self.atoms.values():
            atom.update()
    
        for joint,vertex in zip(self.joints, self.vertexes):
            pv1 = joint.a.position
            pv2 = joint.b.position
            line = self.create_parallell_lines(pv1,pv2,joint.bonds) 
            vertex.vertices = line


    def create_parallell_lines(self, pv1, pv2, nr):
        line = (pv1.x, pv1.y, pv2.x, pv2.y)
        if nr == 1:
            return line
        elif nr == 2:
            k_x, k_y = self.create_parallell_factor(pv1, pv2, 4)
            line1 = (pv1.x-k_x, pv1.y-k_y, pv2.x-k_x, pv2.y-k_y)
            line2 = (pv1.x+k_x, pv1.y+k_y, pv2.x+k_x, pv2.y+k_y)
            return line1 + line2
        elif nr == 3:
            k_x, k_y = self.create_parallell_factor(pv1, pv2, 6)
            line1 = (pv1.x-k_x, pv1.y-k_y, pv2.x-k_x, pv2.y-k_y)
            line3 = (pv1.x+k_x, pv1.y+k_y, pv2.x+k_x, pv2.y+k_y)
            return line1 + line + line3
        raise Exception("Unsupported nr of lines",nr)

    
    def create_parallell_factor(self, pv1, pv2, k):    
        if pv2.x - pv1.x != 0.0:
            v = math.atan((pv2.y-pv1.y)/(pv2.x-pv1.x))
        else:
            v = 0
        k_x = k * math.sin(v) 
        k_y = k * -math.cos(v)
        return k_x, k_y


    def delete(self):
        for vertex in self.vertexes:
            vertex.delete()
        self.vertexes = list()
        
        for atom in self.atoms.values():
            atom.delete()
        self.atoms = dict()

        for joint in self.joints:
            self.space.remove(joint)
        self.joints = list()
        

class Atom(pyglet.sprite.Sprite):
    def __init__(self, symbol, charge, space, batch, molecule, pos):
        img = pyglet_util.loadImage("img/atom-" + symbol.lower() + ".png")
        group = RenderingOrder.elements
        pyglet.sprite.Sprite.__init__(self, img, batch=batch, group=group, subpixel=True)
        self.cml = CachedCml.getMolecule(symbol)
        self.scale = self.cml.property["Radius"] * SCALE_FACTOR
        self.create_electric_charge_sprite(charge, batch)
        self.molecule = molecule
        self.symbol = symbol
        self.charge = charge
        self.space = space
        self.active = False
        self.init_chipmunk()
        self.move(pos)
    
    def init_chipmunk(self):
        weight = self.cml.property["Weight"]    
        radius = self.scale * SPRITE_RADIUS
        body = pymunk.Body(weight,moment = pymunk.inf)#pymunk.moment_for_circle(10, 0, 32))
        body.velocity_limit = 1000
        body.molecule = self.molecule
        shape = pymunk.Circle(body, radius)
        shape.elasticity = 0.95
        shape.collision_type = CollisionTypes.ELEMENT
        shape.layer = CollisionTypes.LAYER_ALL
        shape.molecule = self.molecule
        self.space.add(body, shape)
        
        body.apply_impulse(self.create_force_vector())
        self.body = body
        self.shape = shape

    def create_force_vector(self):
        x = random.randrange(-10, 10)/10.0
        y = random.randrange(-10, 10)/10.0
        vec = Vec2d(x,y)
        force = 1500
        return force * vec

    @property
    def affected_by_gravity(self):
        return self.molecule.current_state.short == "s"

    def create_electric_charge_sprite(self, charge, batch):
        self.electric_charge_sprite = None
        if charge == 0:
            return
        elif charge > 0:
            charge_str = "+" + str(charge)
        else:
            charge_str = str(charge)
            
        e = pyglet_util.loadImage("img/e" + charge_str + ".png")
        group = RenderingOrder.charge
        self.electric_charge_sprite = pyglet.sprite.Sprite(e, batch=batch, group=group)
        self.electric_charge_sprite.scale = self.scale

    def get_only_atom_symbol(self, symbol):
        """ returns the atom symbol without any electric charge """
        return symbol.split("-")[0].split("+")[0]
    
    def cartesian2pymunk(self, pos):
        FACTOR = 42
        center_x, center_y = self.rect.center
        offset_x = -center_x + self.molecule.ATOM_SIZE/2
        offset_y = -center_y + self.molecule.ATOM_SIZE/2
        x, y = pos
        pymunk_pos = (offset_x + FACTOR*x,-(offset_y + FACTOR*y))
        return pymunk_pos

    def move(self, pos):
        self.body.position = pos
        
    def update(self):
        x, y = self.body.position
        self.x = x - self.width/2
        self.y = y - self.height/2
        if self.electric_charge_sprite is not None:
            self.electric_charge_sprite.x = self.x
            self.electric_charge_sprite.y = self.y
        if self.affected_by_gravity:
            self.body.velocity_func = self.gravity_func
        else:
            self.body.velocity_func = pymunk.Body.update_velocity

    def gravity_func(self, body, gravity, damping, dt):
        gravity = (0.0,-920.0)
        return pymunk.Body.update_velocity(body, gravity, damping, dt)

    def delete(self):
        self.space.remove(self.shape)
        self.space.remove(self.body)
        if self.electric_charge_sprite is not None:
            self.electric_charge_sprite.delete()
        super(Atom, self).delete()
