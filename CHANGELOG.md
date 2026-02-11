# Changelog

All notable changes to this repository are documented in this file.

## 2026-02-10

### Added
- Added baseline GitHub Actions workflows for CI and dependency review:
  - `.github/workflows/ci.yml`
  - `.github/workflows/dependency-review.yml`
- Introduced canonical package namespaces for Python imports:
  - `data_management`
  - `python_algorithms`
  - `trading_tools`

### Changed
- Made `pyproject.toml` the canonical dependency source.
- Converted `requirements.txt` and `requirements-dev.txt` to compatibility shims that defer to `pyproject.toml`.
- Converged tooling to Ruff-first by removing Black/isort hooks and configuration.
- Updated packaging discovery to include canonical module namespaces.

### Fixed
- Corrected invalid TOML regex escaping in coverage exclusions.
- Aligned Docker command examples with canonical module paths.
