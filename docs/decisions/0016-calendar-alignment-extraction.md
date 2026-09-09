# ADR-0016: Extract Calendar Alignment as a Standalone Stage

Date: 2026-08-16
Status: Accepted

## Context

ADR-0012's addendum embedded a market-calendar forward-fill directly inside
`timeseries.py`'s `rolling_beta` (`benchmark_calendar_max_ffill`/
`risk_free_calendar_max_ffill` parameters): reindex `benchmark_returns`/
`risk_free_returns` onto market's own unique date calendar, then forward-fill
gaps up to a limit, before computing beta. Immediately after that landed, the
user asked whether this alignment work belonged in data cleaning instead of
inside `rolling_beta` specifically. Discussion concluded it wasn't "cleaning"
in this codebase's sense (`cleaning/market.py`/`cleaning/fundamentals.py` are
single-source validation, independent of any other source; cross-source date
alignment already has its own established home, `asof.py`'s `as_of_join`) --
but the user was confident a future consumer besides beta would need the same
market-calendar-aligned benchmark/risk-free series, and asked to extract it
as its own reusable piece rather than leave it duplicated inside whichever
function needed it next.

## Decision

**New `src/backtester/calendar.py`**, mirroring `asof.py`'s role for a
different alignment technique: `align_to_calendar(series, calendar, *,
max_ffill=5) -> tuple[pd.Series, CalendarAlignmentReport]`. Generic --
reindexes any date-indexed series onto an explicit target calendar and
forward-fills gaps up to `max_ffill`, with no knowledge of benchmark,
risk-free, or beta specifically. Distinguished explicitly in its docstring
from `as_of_join` (backward-looking, staleness-tolerant, two-DataFrame join
on different date semantics) since the two solve visibly different problems
despite both being "alignment."

**`rolling_beta` reverted to its pre-ADR-0012-addendum form** -- no
`*_calendar_max_ffill` parameters, no internal alignment logic. It now
expects `benchmark_returns`/`risk_free_returns` already aligned if that's
wanted, per ADR-0009's "standalone function, composition is the caller's
job," applied more strictly than the addendum had it: alignment is a
pipeline-composition concern, not a rolling-beta concern, even though beta
happens to be the only current consumer needing it.

**New pipeline stage, `align_benchmark_and_risk_free`, runs between `clean`
and `compute_beta`.** Reads benchmark/risk-free (via the existing
`read_benchmark_returns`/`read_risk_free_returns`, unchanged), computes
market's own unique date calendar from `market_clean`, and calls
`align_to_calendar` for each, storing the results as `benchmark_aligned`/
`risk_free_aligned` (plus their own `CalendarAlignmentReport`s) as ordinary
pipeline attributes -- inspectable and reusable by any later stage without
recomputing the alignment, which is the whole point of this ADR.
`compute_beta` now just consumes `self.benchmark_aligned`/
`self.risk_free_aligned` directly.

**Both new pipeline attributes follow the established "None means skipped"
ambiguity-avoidance pattern.** `align_benchmark_and_risk_free` is gated by
`config.beta is None` (the only config section owning benchmark/risk-free
paths today) exactly like the old inline version was. `compute_beta`'s own
prerequisite check still points at `market_clean` (unambiguous, set by
`clean`), not at `benchmark_aligned` directly (ambiguous between "alignment
stage hasn't run" and "it ran but was configured to skip") -- same pattern
already established for `construct_pure_alpha`'s check against `final`
rather than against `neutralize`'s own state. A second, explicit check
(`self._require(self.benchmark_aligned is not None, "align_benchmark_and_risk_free")`)
inside the `config.beta is not None` branch gives a precise
`PipelineStateError` if a caller invokes `compute_beta` out of order in
manual step-by-step usage, matching `apply_isovol`'s equivalent guard for
`estimate_portfolio_volatility`.

## Alternatives Considered

- **Fold alignment into `clean()`/`cleaning/`**: rejected -- this codebase's
  "cleaning" is specifically single-source validation/dedup, run
  independently for market and funda (neither depends on the other's
  output). Benchmark/risk-free alignment needs `market_clean`'s own date
  calendar as an input, which would introduce an order dependency today's
  cleaning stages don't have, and conflates two already-distinct concerns
  (source-level data quality vs. cross-source date alignment) that this
  codebase already keeps separate elsewhere (`cleaning/` vs. `asof.py`).
- **Keep the alignment inline in `rolling_beta`** (the ADR-0012 addendum's
  original shape): superseded -- reasonable when beta was the only consumer,
  but the user was confident enough that a second consumer is coming to
  extract it now rather than duplicate the same reindex-and-ffill logic
  later.
- **Add `*_calendar_max_ffill` to a new, non-beta-specific config section**:
  not done -- `BetaConfig` still owns the only configured benchmark/
  risk-free paths, so its existing `benchmark_calendar_max_ffill`/
  `risk_free_calendar_max_ffill` fields were left in place unchanged. A
  future consumer needing independent paths/tolerances would need its own
  config section then, not preemptively now.

## Consequences

- Purely a refactor, verified behavior-preserving against the full real WRDS
  panel: `n_beta_computed` (1,070,454), `n_rows_missing_benchmark_or_rf`
  (2,000), and `portfolio_volatility_report`'s `n_volatility_computed`
  (1,131)/`n_degenerate_no_holdings` (127) are all bit-for-bit identical to
  the pre-extraction numbers. The new `CalendarAlignmentReport` also exposes
  a diagnostic the old `RollingBetaReport` fields couldn't
  (`n_missing_after_fill` -- gaps that exceeded the tolerance, distinct from
  `n_filled`): risk-free had 114 calendar-missing dates, 112 filled, 2
  genuinely left null.
- 10 new tests: `tests/test_calendar.py` (9 -- within/beyond-tolerance
  filling, fill-from-last-available-value, no-prior-value-to-fill-from,
  `max_ffill=None`/`0` disabling, already-fully-covered no-op, input
  validation) and `tests/test_pipeline.py` (1 new, dedicated to the new
  stage -- alignment output matches market's calendar exactly, `compute_beta`
  actually consumes it). `tests/test_timeseries.py`'s calendar-fill-specific
  tests (added in the ADR-0012 addendum) were removed from there and are
  superseded by `test_calendar.py`'s; its one test that depended on the
  *absence* of calendar filling (window-aging-past-history) reverted to
  calling plain `rolling_beta()` with no fill parameters, since there's
  nothing to disable anymore. Full suite: 219 passed.
- Any future module needing benchmark/risk-free (or any other date-indexed
  series) aligned to market's calendar reuses `align_to_calendar` directly,
  or reads `pipeline.benchmark_aligned`/`risk_free_aligned` if it's a
  pipeline stage running after `align_benchmark_and_risk_free` -- no
  duplicated reindex-and-ffill logic, which was the entire point.