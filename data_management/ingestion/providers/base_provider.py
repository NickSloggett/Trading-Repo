"""Compatibility wrapper for legacy `data-management` provider base module."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_LEGACY_MODULE_PATH = (
    Path(__file__).resolve().parents[3]
    / "data-management"
    / "ingestion"
    / "providers"
    / "base_provider.py"
)
_SPEC = spec_from_file_location("_legacy_base_provider", _LEGACY_MODULE_PATH)
if _SPEC is None or _SPEC.loader is None:
    msg = f"Unable to load legacy module from {_LEGACY_MODULE_PATH}"
    raise ImportError(msg)

_MODULE = module_from_spec(_SPEC)
_SPEC.loader.exec_module(_MODULE)

TimeFrame = _MODULE.TimeFrame
AssetType = _MODULE.AssetType
ProviderCapabilities = _MODULE.ProviderCapabilities
OHLCData = _MODULE.OHLCData
BaseDataProvider = _MODULE.BaseDataProvider

__all__ = [
    "TimeFrame",
    "AssetType",
    "ProviderCapabilities",
    "OHLCData",
    "BaseDataProvider",
]
