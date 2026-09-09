# ADR-0008: Point-in-time as-of join between market and fundamentals data

Date: 2026-08-12
Status: Accepted

## Context

Universe Construction, Outlier Treatment, and Signal Construction each independently
hit the same missing piece: a security-level characteristic needed for one purpose
(industry eligibility, industry-based outlier grouping, industry-neutralizing a
market-derived score) lives only in funda data, while the module operating needed it
alongside market data. Each time, this was noted and deferred (see memory:
`universe-construction-v1-scope`, `outlier-treatment-v1-scope`,
`signal-construction-v1-scope`). When Signal Neutralization came up — wanting to
neutralize a market-derived raw score against industry — the user chose to build the
join now rather than defer a fourth time.

## Decision

`src/backtester/asof.py`'s `as_of_join(market, fundamentals, ...)` implements the
guide's backward as-of join exactly:
$X_{i,t}^{\text{PIT}} = X_{i,\tau_i^*(t)}$, $\tau_i^*(t) = \max\{\tau :
t_{i,\tau}^{\text{avail}} \le t\}$ — for every `(security_id, date)` market row,
attach the most recent fundamentals row for that security with `available_date <=
date`. Implemented via `pandas.merge_asof(direction="backward")` grouped by
`security_id`, not a hand-rolled loop — this is exactly the operation `merge_asof`
exists for, and it relies on a precondition Cleaning already guarantees: at most one
row per `(security_id, date)` and per `(security_id, available_date)`.

**Default maximum staleness: 93 days (~1 reporting quarter)**, agreed with the user
rather than left unbounded. Our funda source refreshes monthly per security (~31-day
normal cadence between `available_date` rows, confirmed during Data Cleaning), so 93
days gives headroom over normal operation while still catching genuine reporting gaps
— a security with no funda update in over a quarter gets nulled fundamentals rather
than an increasingly stale figure silently carried forward. Configurable via
`max_staleness` (a `pd.Timedelta | None`; `None` disables the limit).

A market row with no eligible fundamentals row (before any funda data exists for that
security, or the nearest one exceeds `max_staleness`) gets nulls in every
fundamentals column rather than being dropped — consistent with every other module in
this codebase never silently discarding rows without an explicit, auditable reason.

Adds `funda_data_age_days` (days between the market date and the matched
`available_date`) to every output row — the guide's own PIT data-age diagnostic,
essentially free to compute given both dates are already in the merged result.

Column collisions (e.g. `ticker`/`cusip`, present in both canonical schemas) are
resolved by keeping market's version unsuffixed and fundamentals' version suffixed
`_funda`.

**Generic, like every other module in this codebase**: operates on whatever two
DataFrames are passed in — no knowledge of Cleaning, Universe Construction, Outlier
Treatment, or Signal Construction. The caller composes
`clean → as_of_join → (universe / outlier treatment / signal construction on the
joined frame)`.

## Alternatives Considered

- **Hand-rolled backward search (e.g. groupby + searchsorted)**: rejected —
  `pandas.merge_asof` is the standard, well-tested tool for exactly this operation
  and already supports grouping (`by=`) and staleness (`tolerance=`) natively.
- **No default staleness limit**: rejected per user decision — a methodological
  choice (how stale is too stale) shouldn't be left implicit; 93 days is a
  reasoned, data-grounded default rather than an arbitrary one, and remains fully
  overridable.

## Consequences

- Verified against the full real dataset: 1,132,007 of 1,257,968 market rows
  (89.9%) matched to a funda row within tolerance; `funda_data_age_days` correctly
  bounded to [0, 91]; a spot check (AAPL, 2020-06-15) matched the expected
  2020-05-31 funda snapshot with the correct GICS sector code.
- Signal Neutralization can now use `as_of_join(cleaned_market, cleaned_funda)`
  before neutralizing a market-derived raw score against industry (from funda's
  `gsector`/`ffi*` columns) or against size sourced from either side — the
  blocker flagged three times previously is resolved.
- This also resolves the same gap for Universe Construction (industry/data-availability
  eligibility referencing funda columns) and Outlier Treatment (industry-grouped
  treatment of a market characteristic), though neither was rebuilt to use it as
  part of this change — both remain scoped to their existing behavior until there's
  a concrete need to extend them.