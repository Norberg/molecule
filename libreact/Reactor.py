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
from __future__ import annotations

from collections.abc import Sequence
from typing import Iterable, Iterator

from libcml import Cml
from libreact import Reaction
from libreact.MultiMap import MultiMap, MultiMapEntry

class ReactionEntryMapper:
    def __init__(self, cml_reaction: Cml.Reaction) -> None:
        self.keys = cml_reaction.reactants
        self.value = cml_reaction


class Energy:
    def __init__(self, type: Cml.Requirement.EnergyType) -> None:
        self.type = type


class Reactor:
    def __init__(self, cml_reactions: Iterable[Cml.Reaction]) -> None:
        self.reactions = list(cml_reactions)
        self.reaction_map = MultiMap[str | None, Cml.Reaction, Cml.Reaction](
            self.reactions,
            lambda reaction: MultiMapEntry(reaction.reactants, reaction),
        )
 
    def find_all_reactions(self, reactants: list[str]) -> Iterator[Cml.Reaction]:
        normalized_reactants: list[str | None] = list(Reaction.list_without_state(reactants))
        if len(normalized_reactants) == 1:
            # Add a None to the end of the list to make sure that the next loop
            # will find all reactions that only have one reactant
            normalized_reactants.append(None)

        for reactant in normalized_reactants[:-1]:
            try:
                rs = self.reaction_map[reactant]
            except KeyError:
                continue

            for r in rs:
                if sublist_in_list(r.reactants, normalized_reactants):
                    yield r

    def find_reactions(self, reactants: list[str]) -> set[Cml.Reaction]:
        """ check if all elements needed for a reaction exists in
             in the reacting elements. 
            Return the reactions, or empty set if none exists
        """
        return set(self.find_all_reactions(reactants))

    def react(
        self,
        reactants: list[str],
        K: float = 298,
        trace: bool = False,
        energy_source: list[Cml.Requirement.EnergyType] | None = None,
        ph: float | None = None,
    ) -> Reaction.Reaction | None:
        """ check if all elements needed for the reaction exists in
             in the reacting elements and that the reaction is spontaneous
            in the given temperature. 
            Return the reaction if it will occur otherwise None
        """
        if energy_source is None:
            energy_source = []
        reactionCmls = self.find_reactions(reactants)

        if len(reactionCmls) == 0 and trace:
            print("No reaction found for this reactants")
        elif len(reactionCmls) == 0:
            return None

        reactions: list[tuple[float, Reaction.Reaction]] = []

        for reactionCml in reactionCmls:
            requirements = reactionCml.requirements or []
            additional_energy = 0.0
            requirements_met = True
            for req in requirements:
                if req.type == Cml.Requirement.EnergyType.PH_MIN:
                    if ph is None or ph < req.value:
                        requirements_met = False
                        break
                    continue
                if req.type == Cml.Requirement.EnergyType.PH_MAX:
                    if ph is None or ph > req.value:
                        requirements_met = False
                        break
                    continue
                if req.type not in energy_source:
                    requirements_met = False
                    break
                additional_energy += req.value
            if not requirements_met:
                if trace:
                    print(
                        f"Reaction {reactionCml.reactants} -> {reactionCml.products} "
                        f"requires {requirements} to occur where only {energy_source} and pH={ph} are available."
                    )
                continue
            if len(requirements) > 0 and trace:
                print(
                    f"additional_energy = {additional_energy} for reaction "
                    f"{reactionCml.reactants} -> {reactionCml.products} with requirements {requirements}"
                )

            r = Reaction.Reaction(reactionCml, reactants)
            reactions.append((r.energyChange(K) - additional_energy, r))
        
        if len(reactions) == 0:
            return None

        # Choose the reaction with the lowest free energy; break ties deterministically on energy only
        free_energy, reaction = min(reactions, key=lambda t: t[0])

        if len(reactions) > 1 and trace:
            print("Multiple possible reactions:")
            for t in reactions:
                r = t[1]
                energy = t[0]
                print("Reactants:", r.reactants,
                      "Products:", r.products,
                      "Energy:", energy)

        if Reaction.isSpontaneous(free_energy):
            if trace:
                print(f"\nfree_energy is {free_energy} for reaction at {K}K !")
                reaction.trace = True
                reaction.isSpontaneous(K)
            return reaction
        elif trace:
            print(f"\nfree_energy is not enough for reaction at {K}K !")
            reaction.trace = True
            reaction.isSpontaneous(K)
            return None
        else:
            return None



def sublist_in_list(sublist: Sequence[object], superlist: Sequence[object]) -> bool:
    for e in sublist:
        if sublist.count(e) > superlist.count(e):
            return False
    return True
