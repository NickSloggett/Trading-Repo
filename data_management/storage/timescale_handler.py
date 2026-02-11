"""Compatibility wrapper for legacy `data-management` storage module."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_LEGACY_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "data-management"
    / "storage"
    / "timescale_handler.py"
)
_SPEC = spec_from_file_location("_legacy_timescale_handler", _LEGACY_MODULE_PATH)
if _SPEC is None or _SPEC.loader is None:
    msg = f"Unable to load legacy module from {_LEGACY_MODULE_PATH}"
    raise ImportError(msg)

_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

TimescaleHandler = _MODULE.TimescaleHandler
get_timescale_handler = _MODULE.get_timescale_handler

__all__ = ["TimescaleHandler", "get_timescale_handler"]
