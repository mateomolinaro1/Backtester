# ADR-0003: JSON-driven data source configuration

Date: 2026-08-12
Status: Accepted

## Context

ADR-0002 solved "a new source needs a new `MarketColumnMapping` instance" — but that
instance still had to be constructed in Python code. The user asked for this to be
driven by an external JSON config: pick one of the built-in presets by name, or supply
a fully custom mapping inline, without touching Python.

This JSON file is intended to grow into the seed of a broader backtest configuration
(per CLAUDE.md's "Backtest Identity and Caching" section, which lists strategy, signal,
universe, timing, portfolio, risk, cost, data, model, and random-state identity as the
components a future reproducibility hash must capture) — so the format is designed to
have room for more top-level sections later without restructuring what exists now.

## Decision

`src/backtester/config.py` adds:

- `DataSourcesConfig` — a frozen dataclass holding both sources' resolved paths and
  column mappings.
- `load_data_sources_config(path)` — reads the `data_sources` section of a JSON file.
  Each of `data_sources.market` / `data_sources.fundamentals` must specify a `"path"`
  and **exactly one** of:
  - `"preset": "<name>"` — looks up a `MarketColumnMapping`/`FundamentalsColumnMapping`
    in the new `MARKET_COLUMN_PRESETS`/`FUNDAMENTALS_COLUMN_PRESETS` registries in
    `data/schema.py` (currently only `"wrds"`);
  - `"columns": {...}` — a fully custom mapping, **all** canonical fields required
    (see below for why partial overrides are rejected).
- `read_market_data_from_config` / `read_fundamentals_from_config` — convenience
  wrappers combining a `DataSourcesConfig` with the existing `io.py` readers.

Providing neither `preset` nor `columns`, or both, raises. An unknown preset name
raises listing the available presets. A custom mapping with missing or unknown field
names raises listing exactly which fields are wrong.

The `"return"` JSON key (no trailing underscore, since it's just a string, not a
Python identifier) is aliased internally to the `return_` dataclass field before
constructing `MarketColumnMapping`, so config authors never see the trailing
underscore that's only needed to work around Python's `return` keyword.

## Alternatives Considered

- **Partial custom mappings (missing fields default to WRDS)**: rejected per user
  decision (2026-08-12) — silently inheriting a WRDS column name for a field the user
  forgot to specify, for a source that likely isn't WRDS-shaped at all, would fail
  deep inside cleaning with a confusing error instead of failing loudly at config-load
  time.
- **A single flat JSON per source instead of a `data_sources` top-level key**: rejected
  — would force a restructure once other config sections (universe, signal, ...) are
  added later.

## Consequences

- Two example configs live in `config/`: `backtest.example.json` (uses the `wrds`
  preset, points at the actual files in `data/`) and
  `backtest.custom_source.example.json` (demonstrates the custom-mapping shape for a
  fictitious vendor).
- `tests/test_config.py` includes an integration test that loads the real example
  config and reads+cleans the actual WRDS files end-to-end; it's skipped (not failed)
  in a checkout without the local `data/` files, since those aren't in git.
- Adding a new module's config (e.g. universe eligibility rules) means adding a new
  top-level JSON key and a new `load_*_config` function in `config.py`, following the
  same parse -> validate -> typed-object pattern — not a redesign of this file.