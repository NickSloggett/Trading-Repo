# Trading-Repo Upgrade Baseline (2026-Q1)

**Captured:** 2026-02-10

## Dependency State

- **Primary path:** pyproject.toml (setuptools)
- **Duplicate sources:** requirements.txt, requirements-dev.txt (manual sync)
- **Lock strategy:** None (no Poetry/uv lockfile)

## CI State

- **Workflows:** None under `.github/workflows`
- **PRs:** No CI checks

## Tooling

- **Pre-commit:** Black + Ruff + isort + MyPy + Bandit + Safety
- **Overlap:** Black, isort, Ruff all handle formatting/imports — redundant

## Package Layout

- **pyproject:** trading_repo, python_algorithms, data_management, trading_tools
- **Directories:** data-management, python-algorithms, trading-tools, trading_tools (naming drift)
