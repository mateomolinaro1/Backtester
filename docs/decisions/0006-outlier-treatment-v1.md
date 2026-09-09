# ADR-0006: Cross-sectional Outlier Detection and Treatment (V1 scope)

Date: 2026-08-12
Status: Accepted

## Context

Next module per the guide's own chapter ordering (Raw Data → PIT → Universe →
Cleaning → **Outlier Detection and Treatment** → Signal Construction). The guide
warns explicitly that scoring characteristics on untreated data lets a handful of
extreme observations dominate everything — we already have a concrete example of
exactly that risk in our own data (INSPIRATO, `ISPO`, +648% one-day return on
2022-02-17, a de-SPAC-adjacent artifact found during the Data Cleaning work).

## Decision

**Mechanism**: same generic, JSON-configured philosophy as Universe Construction
(ADR-0005) — no hardcoded per-characteristic logic. `src/backtester/outliers/`:

- `QuantileOutlierTreatment(column, lower_quantile, upper_quantile, action)` — bounds
  from the empirical cross-sectional quantiles.
- `MadOutlierTreatment(column, multiplier, action)` — bounds from
  $\text{median} \pm \text{multiplier} \times 1.4826 \times MAD$ (the guide's
  Gaussian-consistency scaling).
- `action` is `"winsorize"` (cap at bound) or `"truncate"` (null the value). Full-row
  removal is not implemented (per the guide's own comparison: winsorization/truncation
  preserve cross-sectional coverage better; removal risks selection effects and isn't
  needed to reduce scope further given how cheap winsorize/truncate were to build
  together).
- `treat_outliers(data, treatments, date_column="date")` groups by `date_column` and
  computes bounds **independently per date** — never pooled across dates, which the
  guide is explicit is a look-ahead trap (thresholds computed from the whole panel
  would let future dates influence a historical date's treatment).

**Audit trail, not in-place mutation**: each treatment adds `{column}_treated` and
`{column}_is_outlier` columns; the original `{column}` is never modified. Directly
per the guide's requirement to preserve $(X^{\text{clean}}, X^{\text{treated}},
O_{i,t}, M^{\text{treatment}})$ side by side, not collapse them.

**MAD degenerate case handled explicitly, not asked about**: the guide states outright
that "a silent division by zero should never determine the resulting signal." When a
date's cross-sectional MAD is exactly 0 (small groups, many tied values), that date is
left untreated rather than computing degenerate bounds — clipping everything to the
median would be actively wrong, not just imprecise. Tracked via
`TreatmentDiagnostic.n_degenerate_dates`.

**Scope, decided with the user before implementing**: both quantile and MAD methods,
and both winsorize and truncate actions, built together in this iteration — the
per-date bounds/action/diagnostics scaffolding is shared, so the marginal cost of
including both was small enough not to warrant separate iterations.

**Architectural boundary**: this module has no knowledge of Universe Construction or
Cleaning — it operates on whatever DataFrame it's given. Whether cross-sectional
bounds get computed over the full cleaned panel or a universe-restricted subset is a
pipeline-composition decision (`clean → build_universe → [caller joins] →
treat_outliers`), not something built into this module. Same pattern as
`build_universe` not knowing about `clean_market_data`.

**Time-series outlier treatment** (comparing a security to its own history rather
than the cross-section) remains deferred, as agreed when this module was proposed.

## Alternatives Considered

- **Full-row removal as a third action**: rejected — not needed given
  winsorize/truncate cover the guide's recommended defaults, and removal has
  selection-effect risk the guide flags explicitly.
- **In-place overwrite of the original column**: rejected — the guide is explicit
  about preserving the raw/treated distinction; overwriting would make it impossible
  to audit what treatment did or compare pre/post.

## Consequences

- Verified against real data: winsorizing `return` at [0.5%, 99.5%] on the full
  cleaned market panel (1,257,968 rows) treats 6,290 rows at each tail, and correctly
  catches the known `ISPO` +648% outlier, capping it to ~6% (that date's 99.5th
  percentile) while leaving the raw `return` column untouched.
- A future Signal Construction module reading `{column}_treated` gets outlier-safe
  values automatically; anything needing the raw value for diagnostics/attribution
  still has `{column}` unchanged.
- If time-series outlier treatment is added later, it's a natural sibling to this
  module (same `OutlierTreatment`-family typing, different bounds computation grouped
  by security instead of by date) rather than a redesign.

**Addendum (2026-08-12):** the initial `outlier_treatment` JSON config had a single
`date_column` shared by its whole `treatments` list, which meant market columns
(needing `date_column="date"`) and fundamentals columns (needing
`date_column="available_date"`) couldn't both be configured in one file — a real gap,
not a hypothetical one, since Signal Construction (the very next module) needs
characteristics from both sources. Fixed by nesting treatments under
`"market"`/`"fundamentals"` keys (mirroring the existing `data_sources` convention),
each an `OutlierTreatmentGroup` with its own `date_column` (defaulting to `"date"` /
`"available_date"` respectively, so the common case never needs to state it) and
`treatments`. `treat_outliers` itself was always fully generic (any DataFrame, any
`date_column`) — only the config loader needed fixing.
`config/backtest.example.json` now demonstrates both groups, treating `return` from
market and `bm` from fundamentals in the same file, verified end-to-end against the
real data.