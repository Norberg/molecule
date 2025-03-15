# Molecule - a chemical reaction puzzle game
# Copyright (C) 2025 Simon Norberg <simon@pthread.se>
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
from libreact.Reaction import Reaction, list_without_state
from libcml import Cml

REACTION_DIR = "img/skeletal/reaction/"

def reactionFileName(reaction : Cml.Reaction):
    reactants = list_without_state(reaction.reactants)
    products = list_without_state(reaction.products)
    return "_".join(reactants) + "_to_" + "_".join(products) + ".png"

def reactionUnknownProductFileName(reaction : Cml.Reaction):
    products = list_without_state(reaction.products)
    return "UNKNOWN_to_" + "_".join(products) + ".png"

def reactionPath(reaction : Cml.Reaction):
    return REACTION_DIR+ reactionFileName(reaction)

def reactionUnknownProductPath(reaction : Cml.Reaction):
    products = list_without_state(reaction.products)
    return REACTION_DIR + reactionUnknownProductFileName(reaction)