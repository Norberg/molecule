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
import math
import random
import time

import pyglet
from pyglet import gl
from pymunk.vec2d import Vec2d
import pymunk

from molecule import pyglet_util
from molecule import CollisionTypes
from molecule import RenderingOrder
from molecule import Config
from libcml import Cml
from libcml import CachedCml
from libreact import Reaction


SPRITE_SIZE = 96.0
DEFAULT_SIZE = 32.0
SCALE_FACTOR = DEFAULT_SIZE/SPRITE_SIZE * Config.current.zoom
SPRITE_RADIUS = SPRITE_SIZE/2
BOND_LENGTH_FACTOR = 1.4
ATOM_SPACE = SPRITE_SIZE / 1.5

class Molecule:
    def __init__(self, formula_with_state, space, batch, pos=None, render_only=False):
        self.space = space
        self.batch = batch
        self.creation_time = time.time()
        formula, state = Reaction.split_state(formula_with_state)
        self.formula = formula
        self.cml = CachedCml.getMolecule(formula)
        self.cml.normalize_pos()
        self.current_state = self.cml.get_state(state)
        if self.current_state is None and render_only:
            self.current_state = Cml.State("Gas")
        elif self.current_state is None:
            raise Exception("Did not find state for:" + formula_with_state
                    + " existing states are:" + str(self.cml.states.keys()))
        if pos is None:
            pos = (random.randint(10, 600), random.randint(200, 500))
        self.pos = pos
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
        return True
        #return self.current_state.short != "aq"

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

    def to_aqueous(self):
        if self.try_change_state("aq"):
            return self.state.ions

    def create_atoms(self):
        self.atoms = dict()
        for atom in self.cml.atoms.values():
            x, y = self.pos
            pos = (x + atom.x * ATOM_SPACE, y + atom.y *ATOM_SPACE)
            new = Atom(atom.elementType, atom.formalCharge,
                       self.space, self.batch, self, pos)
            self.atoms[atom.id] = new
        self.create_bonds()

    def create_bonds(self):
        self.bonds = list()
        for cml_bond in self.cml.bonds:
            atomA = self.atoms[cml_bond.atomA.id]
            atomB = self.atoms[cml_bond.atomB.id]
            bond = Bond(cml_bond, atomA, atomB, self.space, self.batch)
            self.bonds.append(bond)

    def set_dragging(self, value):
        for atom in self.atoms.values():
            if value:
                atom.shape.layers = CollisionTypes.LAYER_DRAGGING
            else:
                atom.shape.layers = CollisionTypes.LAYER_ALL

    def can_react(self):
        return self.creation_time + 2 < time.time()

    def update(self):
        for atom in self.atoms.values():
            atom.update()

        for bond in self.bonds:
            bond.update()

    def delete(self):
        for bond in self.bonds:
            bond.delete()
        self.bonds = list()

        for atom in self.atoms.values():
            atom.delete()
        self.atoms = dict()


class Bond:
    def __init__(self, cml_bond, atomA, atomB, space, batch):
        self.joints = list()
        self.vertex = None
        self.cml_bond = cml_bond
        self.batch = batch
        self.space = space
        self.atomA = atomA
        self.atomB = atomB

        bond_length = self.get_bond_lenght(cml_bond)
        slide_joint = pymunk.SlideJoint(atomA.body, atomB.body, (0,0), (0,0),
                                        10, bond_length)
        slide_joint.max_force = 15000000
        self.joints.append(slide_joint)
        self.space.add(slide_joint)

        if self.cml_bond.bonds > 0:
            self.vertex = self.create_vertex()

            groove_joint_a = self.create_groove_joint(atomA, atomB)
            groove_joint_b = self.create_groove_joint(atomB, atomA)

            self.joints.append(groove_joint_a)
            self.joints.append(groove_joint_b)

            self.space.add(groove_joint_a)
            self.space.add(groove_joint_b)

    def create_groove_joint(self, bodyA, bodyB):
        relative_pos = bodyB.body.position - bodyA.body.position
        joint = pymunk.GrooveJoint(bodyA.body, bodyB.body, (0,0), relative_pos*2, (0,0))
        joint.max_force = 1500000
        return joint

    def get_bond_lenght(self, bond):
        rA = CachedCml.getMolecule(bond.atomA.elementType).property["Radius"]
        rB = CachedCml.getMolecule(bond.atomB.elementType).property["Radius"]
        bond_lenght = (rA + rB) * SPRITE_RADIUS * SCALE_FACTOR
        if bond.bonds != 0:
            bond_lenght *= BOND_LENGTH_FACTOR
        return bond_lenght

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

    def create_vertex(self):
        pv1 = self.joints[0].a.position
        pv2 = self.joints[0].b.position
        bonds = self.cml_bond.bonds
        line = self.create_parallell_lines(pv1, pv2, bonds)
        color = (90,90,90)
        group = RenderingOrder.elements
        size = 2 * bonds
        vertex = self.batch.add(size, pyglet.gl.GL_LINES, group,
                               ('v2f', line),
                               ('c3B', color * size))
        return vertex

    def update(self):
        if self.vertex is not None:
            pv1 = self.joints[0].a.position
            pv2 = self.joints[0].b.position
            line = self.create_parallell_lines(pv1,pv2,self.cml_bond.bonds)
            self.vertex.vertices = line

    def delete(self):
        for joint in self.joints:
            self.space.remove(joint)
        self.joints = list()

        if self.vertex is not None:
            self.vertex.delete()
        self.vertex = None

class Atom(pyglet.sprite.Sprite):
    def __init__(self, symbol, charge, space, batch, molecule, pos):
        img = pyglet_util.load_image("atom-" + symbol.lower() + ".png")
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
        body = pymunk.Body(weight,moment = pymunk.moment_for_circle(weight, 0, radius))
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

        e = pyglet_util.load_image("e" + charge_str + ".png")
        group = RenderingOrder.charge
        self.electric_charge_sprite = pyglet.sprite.Sprite(e, batch=batch, group=group)
        self.electric_charge_sprite.scale = self.scale

    def get_only_atom_symbol(self, symbol):
        """ returns the atom symbol without any electric charge """
        return symbol.split("-")[0].split("+")[0]

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
