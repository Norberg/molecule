"""Generic emitter system.

Provides:
  - BaseEmitter: optional shared logic
  - Emitter registry (name -> factory)
  - spawn_emitter() helper

Existing specialized emitters (e.g. GoldenRainEmitter) should register
themselves via the @register_emitter decorator. To avoid an always-on
side‑effect import (ugly), we do lazy importing: if a requested emitter
isn't registered yet we import a known module path for that name.
"""
from __future__ import annotations

from typing import Callable, Dict, Tuple
from importlib import import_module

# Registry mapping emitter name to a callable factory
_EMITTER_REGISTRY: Dict[str, Callable[..., object]] = {}

# Map emitter registry names to module paths providing their implementation.
# Extend this as new emitters are added without forcing unconditional imports.
_EMITTER_MODULES: Dict[str, str] = {
    "golden_rain": "molecule.GoldenRain",
}


def register_emitter(name: str):
    """Decorator to register an emitter class or factory under a given name."""
    def decorator(factory: Callable[..., object]):
        _EMITTER_REGISTRY[name] = factory
        return factory
    return decorator


def _lazy_import(name: str):
    module_path = _EMITTER_MODULES.get(name)
    if not module_path:
        return
    try:
        import_module(module_path)
    except Exception as e:
        print(f"Warning: failed to lazy import emitter module '{module_path}' for '{name}': {e}")


def spawn_emitter(name: str, batch, position: Tuple[float, float], **kwargs):
    factory = _EMITTER_REGISTRY.get(name)
    if not factory:
        _lazy_import(name)
        factory = _EMITTER_REGISTRY.get(name)
    if not factory:
        print(f"Emitter '{name}' not found. Known: {list(_EMITTER_REGISTRY.keys())}")
        return None
    try:
        return factory(batch, position, **kwargs)
    except TypeError:
        return factory(batch, position)


def list_emitters():
    """List available emitter names.

    Includes both already-registered emitters (modules imported) and the
    lazily loadable ones declared in _EMITTER_MODULES. This allows UIs
    (like the CML editor) to present choices even before the specific
    emitter module has been imported once in this process.
    """
    names = set(_EMITTER_REGISTRY.keys()) | set(_EMITTER_MODULES.keys())
    return sorted(names)