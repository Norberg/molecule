# Level File Guide

This document summarizes the conventions for `data/levels/*.cml` level definition files, based on recent work adding structured reaction hints.

## File Structure (levels.xsd)
A level file `<level>` contains these ordered child elements:
1. `<moleculeList>` (required) – starting molecules on the board; every `molecule` must have a state `(g|l|s|aq)`.
2. `<inventoryList>` (optional) – extra molecules not initially spawned but available to place (also stateful).
3. `<effectList>` (required) – environmental effects (Fire, Cold, Mining, WaterBeaker, UvLight, etc.). Some effects have a numeric `value` (temperature surrogate) used by tests to try multiple K values.
4. `<victoryCondition>` (required) – list of target molecules; states optional here.
5. `<objective text="..."/>` (required) – player-facing description.
6. `<hint text="...">` (required) – always present; may optionally embed a `<reactions>` block with zero or more `<reaction>` entries (the *reaction hint* sequence).

Order matters and must match the schema. Adding extra XML outside these elements will break validation.

## Molecule Title Conventions
- Stateful entries (in `moleculeList`, `inventoryList`, `effect` internal molecules, and products of hint reactions) must end with `(g|l|s|aq)`.
- Reactants inside hint `<reaction>` blocks are stateless (no parentheses). Products must be stateful.
- Victory condition molecules can be stateless or stateful.

## Effects
Typical effect titles and meaning:
- `Fire` / `Cold`: Provide alternative temperatures (their `value` is added to the temperature candidate list the test harness tries).
- `Mining`: Spawns internal source molecules (nested `<molecule>` tags) intermittently.
- `WaterBeaker` / `HotplateBeaker`: Enable ionic dissociation logic in tests (auto-satisfy missing ionic reactants from solvation states).
- `UvLight`: Enables energy source flag so photochemical reactions (with UV requirement) can proceed.

## Hint Text vs Structured Reaction Hints
- `hint` always has an attribute `text` (human-readable summary or mnemonic).
- Optional structured chemistry steps go inside `<hint><reactions> ... </reactions></hint>`.
- A level **without** `<reactions>` still passes; tests ignore reaction feasibility for that level.
- If `<reactions>` is present, automated tests verify:
  1. Each reaction step can be executed using only current inventory + spawned / produced molecules and effects (looping until no progress).
  2. Victory condition can be satisfied by repeating the sequence.
  3. (Custom test) Reactant order of each hint reaction matches at least one dataset reaction order (see `tests/test_reaction_hint_order.py`).

### Reaction Hint Authoring Rules
1. Use *exact reactant ordering* from the canonical dataset (`data/reactions/*.cml`) to ensure the skeletal reaction image file name exists.
   - Image file naming pattern: `img/skeletal/reaction/` + `Reactant1_Reactant2_..._to_Product1_Product2_... .png`
   - Generator uses the dataset order; it does **not** sort.
2. Reactants (hint) = stateless formulas. Products (hint) = stateful formulas matching an existing state of the molecule.
3. If a multi-step industrial sequence is represented in the dataset as multiple reactions (e.g. Mannheim process), split into those individual steps; do **not** compress them into a single net reaction if you include structured hints.
4. Only include steps that exist (exact stoichiometry) in `data/reactions`. If you need pedagogy beyond existing reactions, put it in `hint text` instead of `<reaction>` entries.
5. Do **not** add energy/requirement blocks inside level hint reactions except where supported (currently only UV handled). Heat/temperature is inferred from effects; adding `requirementList` for generic heat will be ignored / may break tests.
6. If a level conceptually requires a transformation not present in dataset reactions (e.g., approximate dissolution or precipitation not encoded), prefer leaving out structured reactions for that level.

### When To Omit Structured Reactions
- Prototype or placeholder levels.
- Steps rely on reactions not yet in `data/reactions`.
- Puzzle intentionally leaves mechanism undisclosed (use a concise `hint text` instead).

## Adding a New Level – Checklist
1. Copy an existing level as a template.
2. Provide starting molecules (`moleculeList`) and any `inventoryList` items.
3. Add relevant `effectList` entries (Fire/Cold/Mining/WaterBeaker/UvLight) with positions and values.
4. Define `victoryCondition` with the precise target counts.
5. Write a clear `objective text` (imperative, concise).
6. Decide on hint strategy:
   - Simple: only `hint text`.
   - Structured: add `<reactions>` ensuring dataset alignment and execution feasibility.
7. Run `python -m unittest tests.test_levels.TestLevels.test_all_levels_reactions_possible` to confirm structured hints work and victory is reachable.
8. Run full suite: `python -m unittest discover` (target ~1–2 s) before committing.
9. (Optional) Render skeletal images if new reactions were added: `python utils/rdkit_render.py --render-all`.

## Common Pitfalls
| Issue | Cause | Fix |
|-------|-------|-----|
| Schema validation fail | Element order or missing `text` attr | Follow schema order; ensure `hint` has `text`. |
| Reaction hint test fails (missing reactant) | Not enough starting material or intermediate not produced earlier | Add required starting molecules or include preceding reaction steps. |
| Image missing (RuntimeError) | Reactant order mismatch with dataset | Reorder hint reactants to match dataset reaction order. |
| NH4+ victory not achieved | Dataset uses NH4OH intermediate | Either omit structured reaction or adjust victory if design allows. |
| CaCO3 formation hint fails | Reaction not present in dataset | Remove structured reaction (text only) or add reaction to dataset with proper stoichiometry + tests. |
| State error (e.g. H2SO4(s)) | State not defined in molecule file | Use an existing state (Liquid, Aqueous, etc.). |

## Ordering & Skeletal Image Generation
The RDKit renderer (`utils/rdkit_render.py`) iterates over *dataset* reactions and writes files using the exact reactant & product order present. Level hint ordering must therefore match dataset ordering to reuse those images. The dedicated test `test_reaction_hint_order` enforces this.

## Ionic Dissolution Support
If `WaterBeaker` (or `HotplateBeaker`) is present, tests simulate ionic sourcing: missing reactants can be satisfied by dissociating aqueous states described in each molecule's `states` block (ions list). This allows hint steps to reference ions without explicitly listing salt dissolution steps in the reaction hint.

## Updating Dataset Reactions
When adding or modifying reactions in `data/reactions`:
1. Keep reactant order stable if levels already reference the reaction in hints (to avoid breaking image links and hint order test). If you must change order, also update affected levels.
2. Run duplication test `tests/test_reaction_duplicates.py` to ensure uniqueness.
3. Re-render skeletal images if new reactions or new ordering introduced: `python utils/rdkit_render.py --render-all`.

## Strategy For Complex Mechanisms
For multi-stage processes (iron reduction, Mannheim, nitration / reduction sequences):
- Represent each discrete dataset reaction as one hint reaction entry.
- Provide a succinct pathway summary in `hint text`.
- Avoid adding extraneous steps not present in dataset (keep alignment tight to ensure tests pass and images exist).
