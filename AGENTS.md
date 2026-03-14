# Agent Instructions for This Repository

This file defines how coding agents should work in this project.
If these rules conflict with generic defaults, follow this file.
Also read `.github/copilot-instructions.md` for architecture and gameplay-specific guidance.

## Project Context
- Stack: Python 3.12, `pyglet`, `pymunk`, `unittest`, `mypy`.
- Core domains: `libcml` (CML parse/write), `libreact` (reaction engine), `molecule` (game runtime).
- Data-driven gameplay: behavior should primarily come from CML data, not ad-hoc hardcoded logic.

## Design Preferences (Important)
- Prioritize concrete typing over `Any`/`object` wherever practical.
- Do not use string-based forward references in type annotations.
- Avoid introducing custom wrapper types/protocol layers unless explicitly requested.
- Keep changes pragmatic and low-risk; prefer incremental refactors over rewrites.
- Do not add compatibility scaffolding unless explicitly requested.

## Typing Rules
- When replacing `Any`/`object`, use existing concrete runtime types first (`pyglet`, `pymunk`, domain models).
- Keep dynamic boundaries dynamic only where necessary (for example plugin registries, untyped external payloads).
- Avoid `cast`, `getattr`, `hasattr`, and broad `isinstance` branching unless there is no cleaner typed alternative.

## Error Handling and Logging
- Prefer explicit exceptions for invalid internal state instead of silent fallback.
- Avoid broad defensive `try/except` unless requested.
- Keep debug prints behind `Config.current.DEBUG` when they are internal diagnostics.

## Code Change Style
- Keep implementations simple and readable; avoid over-engineering.
- Follow existing naming/style patterns in touched modules.
- Keep gameplay behavior unchanged unless change is explicitly requested.
- Keep comments short and only where they add clarity.

## Validation Before Done
- Run:
  - `python3 -m mypy`
  - `python3 -m unittest discover`
- If either fails, fix or clearly report what remains.

## Scope Priorities for Technical Debt
1. Runtime/game code (`molecule/*`) and parser/reactor (`libcml/*`, `libreact/*`).
2. GUI typing consistency (`molecule/gui/*`, HUD/menu/effects integration).
3. Optional editor (`cmleditor/*`) last, unless explicitly requested.
