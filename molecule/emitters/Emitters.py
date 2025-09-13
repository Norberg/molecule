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
# Separate policy map (explicit) instead of introspecting class attributes
_EMITTER_POLICY: Dict[str, bool] = {}

# Map emitter registry names to module paths providing their implementation.
# Extend this as new emitters are added without forcing unconditional imports.
_EMITTER_MODULES: Dict[str, str] = {
    "golden_rain": "molecule.emitters.GoldenRain",
    "fireworks": "molecule.emitters.Fireworks",
}


def register_emitter(name: str, auto_spawn: bool = True):
    """Decorator to register an emitter class/factory.

    Parameters:
      name: registry key used in CML/state definitions.
      auto_spawn: whether this emitter should appear automatically when a
                  reaction creates a molecule whose state references it.
    """
    def decorator(factory: Callable[..., object]):
        _EMITTER_REGISTRY[name] = factory
        _EMITTER_POLICY[name] = auto_spawn
        return factory
    return decorator


def _lazy_import(name: str):
    module_path = _EMITTER_MODULES.get(name)
    if not module_path:
        raise ValueError(f"Emitter '{name}' not found")
    import_module(module_path)


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


def should_autospawn(name: str) -> bool:
    """Return True if an emitter is explicitly marked for auto-spawn.

    Policy is declared when registering the emitter via ``register_emitter``.
    We avoid runtime introspection (no getattr). Unknown emitters default to
    False (cannot decide) until their module is imported, after which the
    registered policy applies. This keeps design explicit and testable.
    """
    if name not in _EMITTER_REGISTRY:
        try:
            _lazy_import(name)
        except Exception:
            return False
    return _EMITTER_POLICY.get(name, True)


def spawn_reaction_emitter(name: str, batch, position: Tuple[float, float], **kwargs):
    """Spawn an emitter as a consequence of a chemical reaction.

    This centralises the auto-spawn policy so game logic (Levels) does not
    need to know which emitters are gated. Returns the emitter instance or
    None if spawning is disallowed or the emitter cannot be constructed.
    """
    if not should_autospawn(name):
        return None
    return spawn_emitter(name, batch, position, **kwargs)