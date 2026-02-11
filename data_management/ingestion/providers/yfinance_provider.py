"""Compatibility wrapper for legacy `data-management` Yahoo Finance provider."""

from pathlib import Path

_LEGACY_MODULE_PATH = (
    Path(__file__).resolve().parents[3]
    / "data-management"
    / "ingestion"
    / "providers"
    / "yfinance_provider.py"
)

_NAMESPACE: dict[str, object] = {
    "__name__": "data_management.ingestion.providers._legacy_yfinance_provider",
    "__package__": "data_management.ingestion.providers",
    "__file__": str(_LEGACY_MODULE_PATH),
}
exec(compile(_LEGACY_MODULE_PATH.read_text(), str(_LEGACY_MODULE_PATH), "exec"), _NAMESPACE)

YFinanceProvider = _NAMESPACE["YFinanceProvider"]

__all__ = ["YFinanceProvider"]
