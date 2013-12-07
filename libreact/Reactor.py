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
from libreact import Reaction

class Reactor:
    def __init__(self, reactions):
        self.reactions = reactions

    def find_reactions(self, reactants):
        """ check if all elements needed for a reaction exists in
             in the reacting elements. 
            Return the reaction if it exist otherwise None
        """
        reactants = Reaction.list_without_state(reactants)
        for reaction in self.reactions:
            if sublist_in_list(reaction.reactants, reactants):
                return reaction
        return None

    def react(self, reactants, K = 298):
        """ check if all elements needed for the reaction exists in
             in the reacting elements and that the reaction is spontaneous
            in the given temperature. 
            Return the reaction if it will occur otherwise None
        """
        reactionCml = self.find_reactions(reactants)        
        if reactionCml is None:
            return None
        reaction = Reaction.Reaction(reactionCml, reactants)
        if reaction.isSpontaneous(K):
            return reaction
        else:
            return None



def sublist_in_list(sublist, superlist):
    for e in sublist:
        if sublist.count(e) > superlist.count(e):
            return False
    return True
