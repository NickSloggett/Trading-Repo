"""Minimal ingestion scheduler entrypoint for container/runtime alignment."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def main() -> int:
    """Start ingestion scheduler stub."""
    logger.info("Ingestion scheduler entrypoint initialized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
