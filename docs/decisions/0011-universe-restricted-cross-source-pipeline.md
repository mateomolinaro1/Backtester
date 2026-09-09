# ADR-0011: Universe-Restricted Fundamentals via Early As-Of Join

Date: 2026-08-13
Status: Accepted

## Context

The user flagged a real methodological bug in the pipeline built by ADR-0009: raw
scores for fundamentals-sourced characteristics were computed cross-sectionally
over the **full, unrestricted funda population**, not the eligible universe.

The guide is explicit that cross-sectional treatment/scoring parameters are a
function of the eligible universe, not the raw population — Outlier Detection
(07): $\theta_t = g(\{X_{j,t} : j \in \mathcal{U}_t\})$; Raw Scores (08):
$s_{i,t}^{(k),\mathrm{raw}} = \mathcal{S}^{(k)}(x_{i,t}^{(k)}; \{x_{j,t}^{(k)} :
j \in \mathcal{U}_t\})$. ADR-0009's pipeline instead ran
`treat_outliers`/`compute_raw_scores` on `fundamentals_clean` directly — every
ineligible security's `bm` still pulled on the median/MAD (or mean/std) that
eligible securities' scores were computed against. `join_market_fundamentals`
(the final stage) correctly kept ineligible securities out of the *output rows*,
but the damage to the *statistics* backing eligible securities' scores was
already done upstream.

This gap was named and deferred three separate times — ADR-0005 ("Funda-based
eligibility... would need an as-of join... deferred"), ADR-0006 ("Whether
cross-sectional bounds get computed over the full cleaned panel or a
universe-restricted subset is a pipeline-composition decision... not something
built into this module"), ADR-0009 ("Restricting fundamentals' own
cross-sectional statistics... would need a reverse as-of eligibility check
(funda rows are monthly, universe membership is daily) that doesn't exist yet").
The user judged, this time, that it should be fixed rather than deferred a
fourth time.

Two fix shapes were discussed:

- **A**: keep today's stage order; add a reverse as-of eligibility lookup that
  restricts `fundamentals_clean` to securities eligible as of their
  `available_date`, before `treat_outliers`/`compute_raw_scores` run at their
  current monthly grain.
- **B**: move `as_of_join` earlier — right after `build_universe` — so
  fundamentals characteristics get treated/scored on the same daily,
  eligibility-restricted panel market characteristics already use.

The user chose **B**.

## Decision

**New stage order** (supersedes ADR-0009's order for this part of the chain):

```
clean → build_universe → as_of_join(market_universe, fundamentals_clean)
      → treat_outliers (market + funda columns, one call, on the joined frame)
      → compute_raw_scores (market + funda columns, one call, same frame)
      → combine_scores (same-source or cross-source, same frame)
```

**Why moving the join doesn't change market-side numbers**: `as_of_join`
preserves every `market_universe` row 1:1 (ADR-0008 only attaches or nulls
fundamentals columns; it never drops or duplicates a market row). Grouping
market columns by `date` on the joined frame is therefore numerically identical
to grouping on `market_universe` directly — this reorder is a pure fix for the
funda side, not a behavior change for the market side.

**Why this fixes the funda side**: only rows that survived `build_universe`
(i.e. $\mathcal{U}_t$) ever reach the joined frame. Grouping funda columns by
`date` on that frame gives $\theta_t = g(\{X_{j,t} : j \in \mathcal{U}_t\})$
exactly, for every characteristic regardless of source — matching the guide's
formula instead of approximating it.

**Single pass, not two**: `treat_outliers`/`compute_raw_scores` now run once
each, over both market- and funda-sourced columns together, instead of once per
source. Neither function changed — both were already fully generic ("whatever
DataFrame and column list you hand them," ADR-0006/0007) — only the pipeline's
call sites collapsed from two calls to one.

**`date_column` is no longer a config knob for these two stages — it's
hardcoded to `"date"`**, the canonical market date field (`data/schema.py`
guarantees this name after column mapping; `asof.py` already defaults to it).
This was a deliberate rejection of "make it configurable": the joined frame
also carries `available_date` (the matched funda vintage) as a pass-through
column, and grouping by it *looks* valid but isn't — a funda value stays
matched across up to 93 days of daily rows (`max_staleness`, ADR-0008), so
grouping by `available_date` on this frame would pool multiply-duplicated
observations (one per day the vintage stayed current, not one per security),
silently corrupting the cross-sectional statistics. Removing the config option
removes the footgun; there was no real use case for it once the join happens
before treatment.

**Config schema flattened**: `outlier_treatment` and `signal_construction` drop
the `market`/`fundamentals` sub-grouping entirely — one `treatments`/`scores`
list each. The grouping existed only to give each source its own
`date_column` (ADR-0006's addendum); now that both sources share one frame and
one hardcoded `date_column`, the split added structure without adding
flexibility.

**Pipeline attributes collapse accordingly**: `market_treated`/
`fundamentals_treated` → one `treated`; `market_scored`/`fundamentals_scored` →
one `scored`; `market_outlier_report`/`fundamentals_outlier_report` → one
`outlier_report`; same for the score report. `market_fundamentals_joined` now
appears *before* `treat_outliers` in the chain rather than as the final stage.

## Alternatives Considered

- **Option A (reverse as-of eligibility check, keep monthly grain)**: rejected
  by the user. Smaller diff, but doesn't match the guide's $t$-indexed
  $\mathcal{U}_t$ as directly (still pools eligibility decisions taken at
  different real calendar times under one `available_date` label), and leaves
  ADR-0010's cross-source characteristic construction gap unresolved for a
  future iteration. Option B closes both at once.
- **Leaving `date_column` configurable on the joined frame**: rejected — see
  Decision above. A theoretically-valid-looking option that silently produces
  wrong statistics is worse than no option.
- **Keeping the market/fundamentals config split "for documentation"**:
  rejected by the user as redundant once both groups share a frame and a
  `date_column` — the source of a column is still visible from the column name
  itself (`bm_treated` vs `return_treated`), so the split wasn't carrying
  unique information.

## Consequences

- Funda-sourced raw scores are now computed against the correct reference
  population — a real behavior change for any existing backtest using
  fundamentals characteristics, not just a refactor. Anyone who already ran
  results against the old code should treat them as superseded, not
  reproducible from the new code path.
- Funda cross-sectional statistics now get recomputed once per trading day
  (~252/year) instead of once per `available_date` (~12/year) — a real compute
  cost increase, accepted per CLAUDE.md's "optimize only after correctness is
  established." Verified end-to-end against the full real WRDS panel via
  `config/backtest.example.json`: `run()` completes through all six stages over
  1,257,968 market rows with zero degenerate dates for either `return` or `bm`;
  `as_of_join_report` reproduces ADR-0008's exact previously-verified match
  count (1,132,007 / 1,257,968), confirming the earlier join point didn't
  change matching behavior, only what runs after it. No bottleneck observed at
  this scale.
- ADR-0010 (Cross-Source Characteristic Construction, Proposed/deferred) now
  has an obvious home: right between `as_of_join` and `treat_outliers`, since
  that's already where both sources are unified before any statistics are
  computed. Its own open questions (ratio-only vs. general expressions,
  null/zero-denominator convention) are unaffected by this change.
- ADR-0009's six-stage order (`... → compute_raw_scores → as_of_join`) is
  superseded by the order in this ADR; ADR-0009's other content (stepwise
  object design, config-parsing-via-four-loaders choice, market-only universe
  restriction rationale) still stands.
- `config/backtest.example.json` and both other example configs, `config.py`,
  `pipeline.py`, and their test suites all needed updating to the flattened
  schema and new stage order — verified via the existing unit/integration
  tests plus a new test asserting funda raw scores actually differ between the
  old (unrestricted) and new (universe-restricted) reference populations.