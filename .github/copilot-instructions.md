# Copilot Instructions for the Molecule Project

Concise guide for AI coding agents working in this repository. Focus on existing patterns; avoid inventing new architecture.
The game and all code is written in English.

## Core Purpose
A 2D chemistry puzzle game (pyglet + pymunk) where molecules react physically and chemically. Three main domains:
1. `libcml/` Parse & validate CML (molecule/reaction/level) files (uses `xmlschema`).
2. `libreact/` Reaction engine: given reactant formulas + environmental effects, returns Reaction objects.
3. `molecule/` Game runtime: physics (pymunk), rendering/UI (pyglet + pyglet-gui), gameplay logic (levels, inventory, effects, HUD).
Optional: `cmleditor/` GTK+ editor & RDKit integration (only when editor deps installed).

## Entry Points
- Run game: `python start.py [--level=N] [--fullscreen] [--width W --height H] [-d]` (parses into `molecule.Config.current`).
- Tests: `python3 -m unittest discover` (PyPI `pytest` not required; don't rewrite tests to pytest).

## Runtime Architecture (High-Level Flow)
Level load:
`start.py` -> `Game` (in `molecule/Game.py`) -> constructs `Levels.Level` using parsed `libcml.Cml.Level` -> sets up `pymunk.Space`, HUD, effects, elements (atoms/molecules) via `Universe.create_elements`.
During play loop (`pyglet.app.run()`):
- Physics tick: `Level.update()` steps space, updates elements/effects.
- Collision handlers determine reactions (`Universe.universe.react`).
- Inventory and Victory conditions tracked through HUD effect objects (`Effects.Inventory`, `Effects.VictoryInventory`).

## Key Directories & Responsibilities
- `molecule/Universe.py`: Factory + global `Universe.universe` used for reaction resolution.
- `molecule/Levels.py`: Level lifecycle, collision handling, reaction triggering, element/effect dwell logic.
- `molecule/Effects.py`: Effect types (heat, mining, inventory, victory inventory). Effects declare supported capabilities ("reaction", "action", "put", etc.).
- `molecule/HUD.py`: Two HUD panels (horizontal progress + info, vertical status + inventory) using `pyglet_gui` containers.
- `libcml/`: Defines domain models (`Molecule`, `Atom`, `Bond`, `Reactions`, `Reaction`, `Level`, `State`) with parsing + serialization (`.parse/.write`). Ensure new attributes are persisted consistently.
- `libreact/`: Reaction pattern matching logic. When extending reactions, update tests or add new CML reaction definitions.
- `data/levels/*.cml`, `data/reactions/*.cml`, `data/molecule/*.cml`: Content layer. Schema validated in tests (`tests/test_libcml.py`). Changing schema requires updating corresponding `*.xsd` under `data/levels` or `data/reactions`.

## Collision & Reactions
- Physics shapes carry `collision_type` from `molecule/CollisionTypes`.
- Level sets handlers for:
  - Element/Element collisions -> potential multi-molecule reaction (query area expands for large clusters).
  - Element/Effect collisions -> dwell-time gate (requires ~1s continuous contact before effect-triggered reaction).
- Reaction selection: `Universe.universe.react(reactant_formulas, affecting_effects)` returns a `Reaction` model with products.

## Inventory & Victory
- Inventory UI auto-syncs with internal OrderedDict. When modifying `Effects.Inventory.reload_gui`, avoid mutating the container mid-layout; rebuild or carefully replace to keep pyglet_gui vertex arrays stable.
- Victory progress computed from `VictoryInventory.progress_text()`; HUD polls this to update progress label.

## Testing Patterns
- Run with standard library unittest only: `python3 -m unittest discover`.
- Tests rely on deterministic molecule ordering (`atoms_sorted`) and schema validation via `xmlschema` (ensure test data stays valid or update schema and tests together).
- Adding new molecules: must include at least one state; tests fail if `data/molecule/*.cml` lacks state info.
- Reaction duplication detection: `tests/test_reaction_duplicates.py` scans all reaction collections; ensure new reactions are unique across files.

### Quick Test Run (Python game)
Minimal loop while iterating on core logic (ensure correct Python env first):
0. (Once) create env if missing: `pyenv virtualenv 3.12 venv-molecule`
0. Activate env each session: `pyenv activate venv-molecule` (or `pyenv shell venv-molecule`).
1. From repo root `molecule/`: `python3 -m unittest discover -v` (49 tests, ~1–2s).
2. To run a single test file: `python3 -m unittest tests.test_libreact`.
3. To run a single test case or method: `python3 -m unittest tests.test_libreact.TestReact.testSimpleReaction`.

### Quick Test Run (lab book frontend `/molecule-lab-book`)
If you need to touch the separate Vite/React lab book project:
1. `cd molecule-lab-book`
2. Install deps once: `npm install` (creates `node_modules/`).
3. Run tests: `npm test` (Jest watches) or one-off CI style: `npx jest --runInBand`.
4. Run dev server: `npm run dev` (Vite).

Targeted frontend test example: `npx jest src/utils/formulaUtils.test.tsx -t "renders ions"`.

### Fast Feedback Tips
- Use `-k` style filtering via unittest's dotted path (above) instead of editing test files.
- Add new lightweight tests near existing ones; keep runtime <2s.
- When adding new reaction data, first run only `tests/test_libreact.py` to validate thermodynamics before full suite.
- Schema changes: run just schema validations: `python3 -m unittest tests.test_libcml.TestCML.test_reactions_files_schema tests.test_libcml.TestCML.test_levels_files_schema`.

## Conventions
- Global mutable config: `molecule/Config.current` (do not replace object; mutate attributes).
- CML parsing side effects: `.parse()` populates object fields directly; after editing parse logic update corresponding write logic and tests that round-trip (`testWriteAndParse*`).
- Reactions & molecules referenced by string formulas with optional state suffix `(s)`, `(g)`, `(aq)`, `(l)` etc.
- GUI text uses inline HTML-like tags processed by pyglet (`pyglet.text.decode_html`). Use `Gui.formula_to_html` / `Gui.find_and_convert_formulas` for embedding formulas.

## External Dependencies (Game Runtime)
- `pyglet` for windowing/rendering.
- `pymunk` for physics
- `pyglet_gui` for HUD & inventory layout; avoid deep modification unless necessary.
- `xmlschema` for validating CML data sets.

## Adding Content
1. New atom: Add SVG in `img/` (follow README color note), export PNGs, add `.cml` file under `data/molecule/` with states.
2. New reaction: Extend `data/reactions/*.cml` (ensure uniqueness) then add or adjust tests if semantic behavior changes.
3. New level: Add `data/levels/NN-Name.cml` (schema validated) with inventory, effects, molecules, victory condition.

## Safe Change Checklist (Before PR / Commit)
- Run: `python3 -m unittest discover` (expect ~1–2s, 49 tests).
- If editing CML schemas or adding content: re-run tests to catch schema or duplication issues.
- If touching collision/reaction code: verify no performance regression in large reactions (tests include broad reaction scenarios).

## Common Pitfalls for Agents
- Installing pytest or refactoring to pytest is unnecessary; keep unittest.
- Don’t remove or rename `Config.current`; code expects the singleton instance.
- Avoid in-place GUI container mutations during layout callbacks; schedule after or rebuild.
- Keep reaction and molecule identifiers consistent; tests depend on exact string match.

## When Unsure
Prefer reading related existing implementations (e.g., add new Effect by following structure of `Effects.Inventory` + add support flag) over introducing new patterns. Keep changes minimal and schema/data-driven where possible.