"""Compatibility wrapper for legacy `python-algorithms` fetch utilities."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_LEGACY_MODULE_PATH = (
    Path(__file__).resolve().parents[2]
    / "python-algorithms"
    / "utils"
    / "fetch_data.py"
)
_SPEC = spec_from_file_location("_legacy_fetch_data", _LEGACY_MODULE_PATH)
if _SPEC is None or _SPEC.loader is None:
    msg = f"Unable to load legacy module from {_LEGACY_MODULE_PATH}"
    raise ImportError(msg)

_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

fetch_and_save = _MODULE.fetch_and_save
fetch_multiple_symbols = _MODULE.fetch_multiple_symbols

# Backward-compatible alias used by current tests.
fetch_data = fetch_and_save

__all__ = ["fetch_and_save", "fetch_multiple_symbols", "fetch_data"]
