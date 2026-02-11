# Migration Notes

This document is the canonical migration guide for structural and tooling transitions in this repository.

## 2026-Q1 Upgrade Migration

### Dependency management
- `pyproject.toml` is now the source of truth for dependencies.
- Compatibility files remain for tools that still expect requirements files:
  - `requirements.txt` -> `-e .`
  - `requirements-dev.txt` -> `-e .[dev]`

### Package/module naming
- Canonical import paths use underscore package names:
  - `data_management.*`
  - `python_algorithms.*`
  - `trading_tools.*`
- Legacy hyphenated directories are preserved as source compatibility layers and wrapped by canonical package modules.

### CI and quality gates
- CI now includes enforced lint, type-check, test, and security jobs.
- Dependency review is required on pull requests.

### Archived modernization docs
The following docs are retained as historical references:
- `README_NEW.md`
- `README_OLD.md`
- `TRANSFORMATION_COMPLETE.md`
- `UPGRADE_SUMMARY.md`
