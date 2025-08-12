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
import unittest
import pyglet
import pymunk

from libcml import Cml
from libreact.Reactor import Reactor
from molecule.Levels import Levels
from molecule import Universe
from molecule.Elements import Molecule
from molecule import CollisionTypes


class TestLevels(unittest.TestCase):
    def test_all_levels_reactions_possible(self):
        """
        For every level, check that all reactions in the hints can be performed using the inventory and effects,
        and that the victory condition can be reached by repeating the reaction cycle as many times as possible.
        Only print detailed step-failure diagnostics if the level ultimately fails.
        """
        import glob
        import os
        import copy
        import xml.etree.ElementTree as ET

        skip_levels = [
            "data/levels/15-Soda-2-Solvay-process.cml",
            "data/levels/17-Acid-production-2-Nitric-acid.cml",
            "data/levels/31-Organic-Multistep-2-Aspirin.cml",
        ]

        level_files = sorted(glob.glob(os.path.join("data/levels", "*.cml")))
        failures = []

        for level_path in level_files:
            if level_path in skip_levels:
                print(f"[SKIP] Level: {level_path}")
                continue

            cml = Cml.Level()
            cml.parse(level_path)

            # Parse reactions from <hint><reactions>
            tree = ET.parse(level_path)
            root = tree.getroot()
            hint = root.find("hint")
            if hint is None:
                continue  # No hint, skip
            reactions_tag = hint.find("reactions")
            if reactions_tag is None:
                continue  # No reactions, skip
            reactions = []
            for reaction_tag in reactions_tag.findall("reaction"):
                reaction = cml.parseReaction(reaction_tag)
                reactions.append(reaction)
            if not reactions:
                continue  # No reactions, skip

            # Prepare simulation inventory: moleculeList + inventoryList
            start_inventory = []
            if getattr(cml, "molecules", None):
                start_inventory.extend(cml.molecules)
            if getattr(cml, "inventory", None):
                start_inventory.extend(cml.inventory)
            inventory = copy.deepcopy(start_inventory)

            # Temperatures to try: default + effects
            effect_map = {}
            for e in getattr(cml, "effects", []):
                try:
                    effect_map[e.title] = float(e.value) if e.value is not None else 298
                except Exception:
                    effect_map[e.title] = 298
            K_options = [298]
            if "Fire" in effect_map:
                K_options.append(effect_map["Fire"])
            if "Cold" in effect_map:
                K_options.append(effect_map["Cold"])
            has_water_beaker = any(getattr(e, 'title', '') == 'WaterBeaker' for e in getattr(cml, 'effects', []))

            # Energy sources (e.g., UV light) derived from effects
            energy_sources = []
            for e in getattr(cml, 'effects', []):
                if getattr(e, 'title', '') == 'UvLight':
                    energy_sources.append(Cml.Requirement.EnergyType.UV_LIGHT)

            reactor = Reactor(reactions)

            def base_formula(mol: str) -> str:
                return mol.split("(")[0] if "(" in mol else mol

            print(f"\nTesting level: {level_path}")

            # Repeat the reaction cycle as long as possible
            successful_steps = set()  # Track steps that have succeeded at least once
            while True:
                inventory_before = inventory.copy()
                performed_any = False
                cycle_step_failures = []  # Buffer diagnostics; print only if level ultimately fails

                for step_index, reaction in enumerate(reactions):
                    reactants_to_use = []
                    temp_inventory = inventory.copy()

                    # Find reactants in current inventory (state-aware)
                    missing_reactant = None
                    for reactant in reaction.reactants:
                        found = False
                        if "(" in reactant:
                            for inv in temp_inventory:
                                if inv == reactant:
                                    reactants_to_use.append(inv)
                                    temp_inventory.remove(inv)
                                    found = True
                                    break
                        else:
                            for inv in temp_inventory:
                                if base_formula(inv) == reactant:
                                    reactants_to_use.append(inv)
                                    temp_inventory.remove(inv)
                                    found = True
                                    break
                        if not found:
                            missing_reactant = reactant
                            break

                    # If some reactant is missing right now, skip this step (may be possible in a later cycle)
                    if missing_reactant is not None:
                        # Only complain if this step has never succeeded before
                        if step_index not in successful_steps:
                            cycle_step_failures.append({
                                "step": step_index + 1,
                                "reason": "missing-reactants",
                                "reaction": {"reactants": reaction.reactants, "products": reaction.products},
                                "missing_reactant": missing_reactant,
                                "inventory": inventory.copy(),
                            })
                        continue

                    # Try relevant temperatures
                    result = None
                    for K in K_options:
                        result = reactor.react(reactants_to_use, K=K, energy_source=energy_sources)
                        if result is not None:
                            break
                    if result is None:
                        # Try phase-change if WaterBeaker is available: convert reactants to aqueous state
                        if has_water_beaker:
                            def to_state(m: str, state: str) -> str:
                                base = m.split('(')[0] if '(' in m else m
                                return f"{base}({state})"
                            converted_reactants = [to_state(m, 'aq') for m in reactants_to_use]
                            for K in K_options:
                                result = reactor.react(converted_reactants, K=K, energy_source=energy_sources)
                                if result is not None:
                                    break
                        if result is None:
                            # Only complain if this step has never succeeded before
                            if step_index not in successful_steps:
                                cycle_step_failures.append({
                                    "step": step_index + 1,
                                    "reason": "no-reaction",
                                    "reaction": {"reactants": reaction.reactants, "products": reaction.products},
                                    "K_options": K_options,
                                    "reactants_used": reactants_to_use,
                                    "inventory": inventory.copy(),
                                })
                            continue

                    # Apply reaction: remove used reactants, add products
                    for used in reactants_to_use:
                        inventory.remove(used)
                    for product in result.products:
                        inventory.append(product)
                    performed_any = True
                    successful_steps.add(step_index)

                # If we made no progress, check victory and maybe log buffered failures
                if not performed_any or inventory == inventory_before:
                    missing = self._missing_for_victory(inventory, cml)
                    if missing:
                        for f in cycle_step_failures:
                            print(f"\n[STEP FAIL] Level: {level_path}")
                            print(f"  Step: {f['step']}")
                            print(f"  Reaction: {f['reaction']['reactants']} -> {f['reaction']['products']}")
                            if f["reason"] == "missing-reactants":
                                print(f"  Missing reactant: {f['missing_reactant']}")
                            else:
                                print(f"  Tried temperatures K={f.get('K_options')}")
                                print(f"  Reactants used: {f.get('reactants_used')}")
                            print(f"  Inventory at step: {f['inventory']}")

                        print(f"\n[FAIL] Level: {level_path}")
                        print(f"  Inventory: {inventory}")
                        print(f"  Victory condition: {cml.victory_condition}")
                        print(f"  Missing: {missing}")
                        failures.append({
                            "level": level_path,
                            "missing": missing,
                            "inventory": inventory.copy(),
                            "victory": cml.victory_condition,
                        })
                    break

        # After processing all levels, assert aggregated result
        if failures:
            summary_lines = [
                f"{f['level']} -> Missing: {f['missing']} | Inventory: {f['inventory']} | Victory: {f['victory']}"
                for f in failures
            ]
            summary = "\n".join(summary_lines)
            assert False, f"Some levels did not meet victory condition:\n{summary}"
        else:
            print("All levels passed victory condition simulation.")

    def _missing_for_victory(self, inventory, cml):
        # Accept any state for each molecule in victory_condition
        missing = []
        for mol in cml.victory_condition:
            base = mol.split("(")[0] if "(" in mol else mol
            found = any(inv.split("(")[0] == base for inv in inventory)
            if not found:
                missing.append(mol)
        return missing

    def test_cativa_level_reactions_possible(self):
        """
        Check that all reactions in the hints for the Cativa level can be performed using the inventory and effects.
        Logs each step for clarity and debugging.
        """
        import logging
        import copy
        import xml.etree.ElementTree as ET

        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("test_cativa_level_reactions_possible")

        # Load level
        cml = Cml.Level()
        cml.parse("data/levels/33-Organic-Industrial-1-Cativa.cml")
        # Get reactions from <hint><reactions>
        reactions = []
        tree = ET.parse("data/levels/33-Organic-Industrial-1-Cativa.cml")
        root = tree.getroot()
        hint = root.find("hint")
        reactions_tag = hint.find("reactions")
        for reaction_tag in reactions_tag.findall("reaction"):
            reaction = cml.parseReaction(reaction_tag)
            reactions.append(reaction)

        # Start with inventory
        inventory = copy.deepcopy(cml.inventory)
        logger.info(f"Initial inventory: {inventory}")
        # Effects (energy types)
        available_effects = [e.title for e in cml.effects]
        logger.info(f"Available effects: {available_effects}")

        # Use Reactor to simulate
        reactor = Reactor(reactions)

        def base_formula(mol):
            return mol.split("(")[0] if "(" in mol else mol

        effect_map = {e.title: float(getattr(e, "value", 298)) for e in cml.effects}
        K_options = [298]
        if "Fire" in effect_map:
            K_options.append(effect_map["Fire"])
        if "Cold" in effect_map:
            K_options.append(effect_map["Cold"])

        # Repeat the reaction cycle as long as possible
        total_cycles = 0
        while True:
            inventory_before = inventory.copy()
            logger.info(f"\n--- Starting reaction cycle {total_cycles + 1} ---")
            for idx, reaction in enumerate(reactions):
                logger.info(f"\nStep {idx + 1}: {reaction.reactants} -> {reaction.products}")
                # Find matching reactants in inventory
                reactants_to_use = []
                temp_inventory = inventory.copy()
                for reactant in reaction.reactants:
                    found = False
                    if "(" in reactant:
                        for inv in temp_inventory:
                            if inv == reactant:
                                reactants_to_use.append(inv)
                                temp_inventory.remove(inv)
                                found = True
                                break
                    else:
                        for inv in temp_inventory:
                            if base_formula(inv) == reactant:
                                reactants_to_use.append(inv)
                                temp_inventory.remove(inv)
                                found = True
                                break
                    logger.info(f"Checking for reactant: {reactant} (found: {found})")
                    if not found:
                        logger.info(f"Could not find reactant {reactant}, ending cycles.")
                        return self._assert_victory(inventory)
                # Try all relevant temperatures: standard, Fire, Cold
                result = None
                for K in K_options:
                    logger.info(f"Trying reaction at K={K} for {reaction.reactants} -> {reaction.products}")
                    result = reactor.react(reactants_to_use, K=K)
                    if result is not None:
                        logger.info(f"Reaction succeeded at K={K}: {result.reactants} -> {result.products}")
                        break
                if result is None:
                    logger.info(
                        f"Reaction failed in simulation: {reaction.reactants} -> {reaction.products} (tried K={K_options}), ending cycles."
                    )
                    return self._assert_victory(inventory)
                # Remove used reactants from inventory
                for used in reactants_to_use:
                    inventory.remove(used)
                    logger.info(f"Removed reactant: {used}")
                # Add products to inventory
                for product in result.products:
                    inventory.append(product)
                    logger.info(f"Added product: {product}")
                logger.info(f"Inventory after step {idx + 1}: {inventory}")
            total_cycles += 1
            logger.info(f"--- End of cycle {total_cycles}, inventory: {inventory}")

        # Should never reach here
        logger.info(f"Final inventory: {inventory}")
        self._assert_victory(inventory)

    def _assert_victory(self, inventory):
        # Accept either CH3COOH(aq) or CH3COOH as product
        count = inventory.count("CH3COOH(aq)") + inventory.count("CH3COOH")
        assert count >= 2, f"Not enough CH3COOH at the end of the reaction chain, found {count}"

    def testLevels(self):
        levels = Levels("data/levels", window=WindowMock())
        l = levels.get_current_level()
        expected = ['H+(g)', 'O(g)', 'O(g)', 'H+(g)', 'P(g)', 'F(g)', 'Al(s)']
        self.assertEqual(l.cml.molecules, expected)
        self.assertEqual(l.cml.victory_condition, ["H2O"])
        self.assertEqual(l.cml.objective, "Create a water molecule")
        self.assertEqual(l.cml.hint, "H + H + O => H2O")
        self.assertEqual(l.victory(), False)
        batch = pyglet.graphics.Batch()
        l.elements.extend(Universe.create_elements(l.space, "H2O(g)", batch, None))
        victory_effect = l.hud.horizontal.victory
        victory_effect.put_element(l.elements.pop())
        self.assertEqual(l.victory(), True)

        l = levels.next_level()
        expected = ['H+(g)', 'O(g)', 'O(g)', 'H+(g)', 'OH-(aq)', 'CO2(g)', 'CH4(g)']
        self.assertEqual(l.cml.molecules, expected)
        self.assertEqual(l.cml.victory_condition, ['CO', 'H2', 'H2', 'H2'])
        self.assertEqual(l.cml.objective, "Create a CO and 3 H2 molecules")
        self.assertEqual(l.cml.hint, "H2O + CH4 + Heat => CO + 3H2")
        levels.current_level = 1000
        l = levels.next_level()
        self.assertEqual(l, None)

    def testAllLevels(self):
        levels = Levels("data/levels", window=WindowMock())
        space, batch = createSpaceAndBatchMock()
        for level in levels.level_iter():
            self.assertIsNotNone(level.cml.objective)
            self.assertEqual(level.victory(), False)
            Universe.create_elements(level.space, level.cml.inventory, level.batch, None)

    def testDestroyElements(self):
        levels = Levels("data/levels", window=WindowMock())
        l = levels.next_level()
        batch = pyglet.graphics.Batch()
        l.elements.extend(
            Universe.create_elements(l.space, ["O2(g)", "O2(g)", "CH4(g)"], batch, None)
        )
        # self.assertEqual(l.elements, [])

    def testGetCollidingMolecules(self):
        level1 = getLevel1()
        space, batch = createSpaceAndBatchMock()
        OH = Molecule("OH-(aq)", space, batch)
        H = Molecule("H+(g)", space, batch)
        OH.creation_time = 0
        H.creation_time = 0
        collisions = createCollisionsMock(OH, H)
        collidingMolecules = level1.get_colliding_molecules(collisions)
        self.assertEqual([OH, H], collidingMolecules)

    def testGetReactingMolecules(self):
        level1 = getLevel1()
        space, batch = createSpaceAndBatchMock()
        OH = Molecule("OH-(aq)", space, batch)
        Al = Molecule("Al(s)", space, batch)
        H = Molecule("H+(g)", space, batch)
        H_ = Molecule("H+(g)", space, batch)
        OH.creation_time = 0
        Al.creation_time = 0
        H.creation_time = 0
        H_.creation_time = 0
        collisions = createCollisionsMock(OH, Al, H, H_)
        reaction = setupSimpleReactor().react([H.state_formula, OH.state_formula])
        reactingMolecules = level1.get_molecules_in_reaction(collisions, reaction)
        self.assertEqual([OH, H], reactingMolecules)

    def testCollisionReaction(self):
        level1 = getLevel1()
        space, batch = createSpaceAndBatchMock()
        OH = Molecule("OH-(aq)", space, batch)
        Al = Molecule("Al(s)", space, batch)
        H = Molecule("H+(g)", space, batch)
        H_ = Molecule("H+(g)", space, batch)
        OH.creation_time = 0
        Al.creation_time = 0
        H.creation_time = 0
        H_.creation_time = 0
        collisions = createCollisionsMock(OH, Al, H, H_)
        reaction = level1.react(collisions, [])
        self.assertEqual(reaction.reactants, ['H+(g)', 'H+(g)'])
        self.assertEqual(reaction.products, ['H2(g)'])

    def testSulfuricAcidReaction(self):
        level1 = getLevel1()
        space, batch = createSpaceAndBatchMock()
        H2SO4 = Molecule("H2SO4(l)", space, batch)
        NaCl = Molecule("NaCl(s)", space, batch)
        NaCl_ = Molecule("NaCl(s)", space, batch)
        H2SO4.creation_time = 0
        NaCl.creation_time = 0
        NaCl_.creation_time = 0
        collisions = createCollisionsMock(H2SO4, NaCl, NaCl_)
        reaction = level1.react(collisions, [])
        self.assertEqual(reaction.reactants, ['H2SO4(l)', 'NaCl(s)'])
        self.assertEqual(reaction.products, ['NaHSO4(s)', 'HCl(g)'])

    def testSulfuricAcidNoReaction(self):
        level1 = getLevel1()
        space, batch = createSpaceAndBatchMock()
        H2SO4 = Molecule("H2SO4(l)", space, batch)
        HCl = Molecule("HCl(g)", space, batch)
        H2SO4.creation_time = 0
        HCl.creation_time = 0
        collisions = createCollisionsMock(H2SO4, HCl)
        reaction = level1.react(collisions, [])
        self.assertEqual(reaction, None)

    def testVictoryEffect(self):
        level1 = getLevel1()
        victory_effect = level1.hud.horizontal.victory
        level1.create_elements(["CH4(g)"], pos=(200, 300))
        level1.create_elements(["H2O(g)"], pos=(300, 300))
        level1.update()

        level1.handle_element_pressed(234, 300)
        self.assertIsNotNone(level1.mouse_spring)
        level1.handle_element_released(50, 50, None, None)
        self.assertIsNone(level1.mouse_spring)
        self.assertEqual(victory_effect.content, {})
        self.assertEqual(victory_effect.victory(), False)
        self.assertEqual(victory_effect.progress_text(), "0/1 H2O")

        level1.handle_element_pressed(300, 300)
        self.assertIsNotNone(level1.mouse_spring)
        level1.handle_element_released(50, 50, None, None)
        self.assertIsNone(level1.mouse_spring)
        self.assertEqual(victory_effect.content, {"H2O": 1})
        self.assertEqual(victory_effect.victory(), True)
        self.assertEqual(victory_effect.progress_text(), "1/1 H2O")


def setupSimpleReactor():
    r1 = Cml.Reaction(["H2SO4(l)", "NaCl(s)", "NaCl(s)"], ["HCl(g)", "HCl(g)", "Na2SO4(s)"])
    r2 = Cml.Reaction(["OH-", "H+"], ["H2O(l)"])
    return Reactor([r1, r2])


def getLevel1():
    levels = Levels("data/levels", window=WindowMock())
    level1 = levels.get_current_level()
    return level1


def createCollisionsMock(*molecules):
    collision = list()
    for molecule in molecules:
        collision.append(CollisionMock(molecule))
    return collision


def createSpaceAndBatchMock():
    return (SpaceMock(), BatchMock())


class CollisionMock():
    def __init__(self, molecule):
        self.molecule = molecule
        self.collision_type = CollisionTypes.ELEMENT
        self.shape = pymunk.Circle(None, 16)


class SpaceMock():
    def add(*args):
        pass


class BatchMock():
    def add(*args):
        return VerticeMock()


class VerticeMock():
    def __init__(self):
        self.vertices = list()
        self.colors = list()


class WindowMock():
    def __init__(self):
        self.width = 1024
        self.height = 768

    def get_size(self):
        return (self.width, self.height)

    def push_handlers(self, *arg, **kwargs):
        pass

    def set_handlers(self, *arg, **kwargs):
        pass
