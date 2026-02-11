"""Compatibility wrapper for legacy `trading-tools` analysis module."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_LEGACY_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "trading-tools"
    / "analysis"
    / "simple_analysis.py"
)
_SPEC = spec_from_file_location("_legacy_simple_analysis", _LEGACY_MODULE_PATH)
if _SPEC is None or _SPEC.loader is None:
    msg = f"Unable to load legacy module from {_LEGACY_MODULE_PATH}"
    raise ImportError(msg)

_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

__all__ = [name for name in dir(_MODULE) if not name.startswith("_")]

for _name in __all__:
    globals()[_name] = getattr(_MODULE, _name)
