# ADR-0007: Raw Score Construction (V1 scope)

Date: 2026-08-12
Status: Accepted

## Context

Next module per the guide's chapter ordering: "From Firm-Level Characteristics to
Raw Scores" — $s_{i,t}^{(k),\text{raw}} = \mathcal{S}_t^{(k)}(x_{i,t}^{(k)})$, computed
cross-sectionally. The guide treats several transforms (z-score, robust z-score,
rank, percentile, Gaussian rank) as *alternative* scoring conventions, plus an
explicit direction convention and multi-characteristic combination.

## Decision

**Scope, agreed with the user before implementing**: z-score and robust z-score only
(rank-based and Gaussian rank transforms deferred); equal-weighted combination
included in the same iteration.

**Mechanism**: same generic, JSON-configured philosophy as Universe Construction and
Outlier Treatment. `src/backtester/signals/`:

- `ZScoreTransform(column, direction)` — `direction * (x - mean) / std`.
- `RobustZScoreTransform(column, direction)` — `direction * (x - median) / (1.4826 *
  MAD)`.
- `compute_raw_scores(data, transforms, date_column="date")` — groups by
  `date_column`, computes bounds per date independently (never pooled across dates —
  same look-ahead concern as outlier treatment), adds `{column}_raw_score`, never
  touches the original column.
- `combine_scores(data, columns, output_column="composite_raw_score")` — equal-weighted
  average of already-computed raw score columns. Uses pandas' row-wise `.mean(axis=1)`,
  which skips nulls and renormalizes over whatever's available per row — this is
  exactly the guide's "Missing Component Scores" renormalization, not a coincidence;
  no special-casing was needed to get it.

**Shared MAD math extracted, not duplicated**: robust z-score needs the identical
per-date median/MAD computation as `MadOutlierTreatment`. Now that it's needed in two
places (not hypothetically, actually), `cross_sectional_median_mad` and `MAD_SCALE`
moved to a new `src/backtester/stats.py`; `outliers/treat.py` was refactored to use
it (behavior-preserving, verified by its existing test suite passing unchanged).

**Degenerate-date handling applied to z-score too, not just MAD**: the guide's
"never let silent division by zero drive the signal" principle applies equally to
z-score (a date where every security has an identical characteristic value gives
std=0). Both transforms skip such dates, producing null scores rather than inf/NaN
from silent division, tracked via `ScoreDiagnostic.n_degenerate_dates`.

**Config schema learned from the outlier_treatment mistake**: `signal_construction`
is nested under `"market"`/`"fundamentals"` from the start (each with its own
`date_column`, defaulting to `"date"`/`"available_date"`), not a flat list that would
need the same later fix ADR-0006 required.

**Cross-source combination remains out of scope**: combining a market-derived score
with a fundamentals-derived score needs an as-of join between daily market dates and
monthly `available_date`-keyed funda data that doesn't exist yet. `combine_scores`
only operates on columns already present in one DataFrame — same-source combination
only, exactly as scoped with the user before implementing.

## Alternatives Considered

- **Rank-based and Gaussian rank transforms now**: deferred per user's explicit scope
  decision — z-score and robust z-score cover the immediate need; rank-based
  transforms can be added later as siblings to the existing `ScoreTransform` union
  without restructuring what's built now.
- **Weighted (non-equal) combination**: not built — user specifically asked for
  equal-weighted; the guide's performance-based/covariance-aware weighting is
  explicitly more advanced (dynamic, estimated) territory, out of scope here.

## Consequences

- Verified end-to-end against real data: `return_treated` (market, z-score) and
  `bm_treated` (fundamentals, robust z-score) both score cleanly across the full
  panels with zero degenerate dates; `config/backtest.example.json` now demonstrates
  the complete pipeline (`data_sources` → `universe` → `outlier_treatment` →
  `signal_construction`) end-to-end from one file.
- A future Signal Neutralization module (the guide's next chapter) consumes
  `{column}_raw_score` the same way this module consumes `{column}_treated` — same
  compositional pattern, no coupling.
- If rank-based/Gaussian rank transforms are added later, or if the as-of join is
  built and cross-source combination becomes possible, both are additive to this
  module's existing types rather than requiring a redesign.