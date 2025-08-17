"""Python package for OpenCPN bridge utilities."""

from importlib import import_module

try:  # pragma: no cover - optional native extension
    _native = import_module("opencpn_bridge._bridge")
    for _name in getattr(_native, "__all__", dir(_native)):
        if not _name.startswith("_"):
            globals()[_name] = getattr(_native, _name)
except ModuleNotFoundError:  # pragma: no cover
    pass

__all__ = [name for name in globals() if not name.startswith("_")]
