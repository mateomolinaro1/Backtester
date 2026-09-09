# ADR-0001: Project scaffolding

Date: 2026-08-12
Status: Accepted

## Context

The repository starts with only `CLAUDE.md` and `docs/BACKTESTING_GUIDE.md`. Before any
economic logic is written, the project needs a package layout, dependency manager, and
baseline tooling that will hold up as modules are added incrementally per CLAUDE.md's
Development Process.

## Decision

- Dependency management: **uv**, with `pyproject.toml` + `uv.lock` as the source of truth.
- Package layout: **src layout** (`src/backtester/`), importable as `import backtester`.
  Tests live under `tests/`, mirroring the package structure as modules are added.
- Package name: `backtester` (matches the repo).
- Core runtime dependencies: `pandas`, `numpy`, `pyarrow` (local Parquet I/O), per V1 scope.
- Dev tooling: `pytest` (testing), `ruff` (lint + import sort, replacing separate
  flake8/isort), `mypy` in `strict` mode + `pandas-stubs` (CLAUDE.md asks for explicit,
  typed, readable Python).
- Raw/intermediate data (`data/`) is git-ignored; only `data/.gitkeep` is tracked. Datasets
  are not versioned in git — this will be revisited when the backtest-identity/data-versioning
  module is built (per CLAUDE.md's "Backtest Identity and Caching").

## Alternatives Considered

- **Flat layout** (package at repo root): simpler, but risks accidentally importing the
  package from the working directory instead of the installed one, which matters once
  research notebooks/scripts sit alongside the package.
- **pip + requirements.txt / Poetry**: uv was explicitly requested; it also gives a single
  fast tool for venv + dependency resolution + lockfile.
- **ruff-only (no mypy)**: rejected — CLAUDE.md explicitly calls for typed code, and static
  typing helps enforce the domain-object distinctions (signal vs. weights vs. trades) the
  guide requires.

## Consequences

- Every new module goes under `src/backtester/<module>/` with a mirrored `tests/<module>/`.
- `uv sync` reproduces the environment exactly from `uv.lock`; `uv run pytest` /
  `uv run ruff check` / `uv run mypy src` are the standard commands.
- Strict mypy from day one means later modules can't quietly introduce untyped surfaces —
  this may need revisiting if a dependency lacks type stubs.