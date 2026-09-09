# ADR-0012: Beta Computation and Signal Neutralization Pipeline Wiring

Date: 2026-08-13
Status: Accepted

## Context

`signals/neutralize.py` (`neutralize_signals`, `Exposure`/`ContinuousExposure`/
`CategoricalExposure`) and `timeseries.py`'s `rolling_beta` — pulled forward from
the Portfolio Risk Model chapter (14) because Signal Neutralization (ch. 10) needs
beta as an input exposure now — were already implemented as standalone, generic
functions, each with `config.py` loaders (`BetaConfig`/`load_beta_config`,
`NeutralizationConfig`/`load_neutralization_config`) already written and
documented in `config.py`'s module docstring, referencing this ADR by number
ahead of time. What was missing: neither function was ever called from
`BacktestPipeline`, and neither had a test suite.

This ADR covers closing that gap: wiring both into the pipeline (ADR-0009's
"standalone function, composition is the caller's job" pattern, same as every
prior module) and the tests that came with it. It also documents one real
data-quality issue the wiring surfaced.

## Decision

**Two new optional pipeline stages**, `compute_beta` and `neutralize`, added to
the existing chain (ADR-0011):

```
clean -> compute_beta -> build_universe -> as_of_join
      -> treat_outliers -> compute_raw_scores/combine_scores -> neutralize
```

**`compute_beta` runs on `market_clean`, before `build_universe` restricts to
eligible rows** — not on the joined/eligibility-restricted frame. A security's
rolling beta should reflect its actual return history; restricting to eligible
dates first would introduce artificial gaps into the rolling window every time
the security was temporarily ineligible, corrupting the covariance/variance
estimate (this rationale was already written into `timeseries.py`'s module
docstring before this ADR; the pipeline wiring just honors it). The computed
`beta` series is `.assign()`-ed onto `market_clean` as an ordinary column, then
flows through every later stage exactly like `price`/`volume`/`return`: inner-
joined by `build_universe`, preserved 1:1 by `as_of_join`. No special-casing was
needed downstream.

**`neutralize` runs last**, after `construct_signals`, operating on `scored` —
the already-scored, joined frame — exactly matching `config.py`'s documented
`neutralization` section (signal columns to neutralize, against a list of
`continuous`/`categorical` exposures).

**Both stages are optional, and absence means "does nothing," not an error** —
consistent with every other optional config section in this pipeline:

- `compute_beta`: if `config.beta` is `None` (section absent), it's a no-op —
  `market_clean` never gets a `beta` column, `beta_report` stays `None`.
- `neutralize`: always runs, even with an empty `neutralization` section —
  matching `treat_outliers`/`construct_signals`'s existing convention that an
  empty treatment/score list degenerates to a no-op copy rather than being
  skipped outright.
- An exposure referencing a column that was never computed (e.g. `{"type":
  "continuous", "column": "beta"}` with no `beta` config section present) is
  *not* special-cased — it surfaces as `neutralize_signals`'s own existing
  "unknown exposure column" `ValueError`, which is already a clear, correct
  error. Verified by test
  (`test_neutralization_raises_clear_error_when_beta_exposure_configured_without_beta_section`).

**Risk-free data has duplicate dates with conflicting rates — resolved by
keeping the last occurrence.** Running the wired pipeline end-to-end against the
real WRDS data (`data/risk_free_returns.parquet`) surfaced a genuine upstream
data-quality defect: 355 dates appear twice with different rates (e.g.
`2001-08-20`: 0.000097 and 0.000101), which crashes `rolling_beta`'s reindex
against a non-unique index. Raw data acquisition is out of this project's scope
(see project memory), so this isn't something to fix at the source here — but
`read_risk_free_returns` needed *some* deterministic behavior rather than a
crash. The user chose: keep the last occurrence of each duplicated date, dropping
the rest — an explicit, documented tie-break rather than a silent one. Implemented
as `rf[~rf.index.duplicated(keep="last")]` in `data/io.py`, covered by
`test_read_risk_free_returns_keeps_last_value_on_duplicate_dates`. The benchmark
file (`russell_returns.parquet`) has no duplicates today; `read_benchmark_returns`
was left unchanged rather than adding a safeguard for a problem it doesn't have.

**Benchmark and risk-free loading forward-fill short gaps, bounded by a
`max_ffill` row-count limit (default 5).** Distinct from the duplicate-dates
issue above: the real benchmark file (`russell_returns.parquet`) has 221 rows
where the level itself is `NaN` on an otherwise-present date (a missing vendor
print, not a duplicate) — pre-fill, each one poisoned two return rows (`t` and
`t+1`) via `pct_change`, and both got silently dropped by the trailing
`dropna()`. `read_benchmark_returns` and `read_risk_free_returns` each gained
an independent `max_ffill: int | None = 5` parameter (`BetaConfig`'s
`benchmark_max_ffill`/`risk_free_max_ffill`, both defaulting to 5), and:

- the benchmark fills the *level*, before `pct_change` — a filled day gets a
  0% (flat) return, and the following day's return correctly spans the full
  move from the last known level, rather than losing both days to `NaN`;
- risk-free has no level to fill, so it forward-fills the rate series
  directly — carrying a short-term rate forward across a short gap is the
  standard practical assumption, and today's file has zero raw gaps to fill
  anyway (this just guards against a future vendor extract that does);
- both use `Series.ffill(limit=max_ffill)` — a row-count limit, matching
  pandas' own `limit` semantics directly, not a calendar-day tolerance like
  `as_of_join`'s `max_staleness` (raised and rejected as an alternative: no
  existing gap-length calculation to reuse here, and the two loaders operate
  on already-daily, already-deduplicated series where a row-count reads more
  directly than a `Timedelta`);
- gaps longer than the limit are left as `NaN` past the cutoff — dropped by
  the benchmark's existing trailing `dropna()` (unchanged behavior for
  long gaps), left `NaN` in the risk-free series (unchanged too — callers
  already reindex against it and tolerate missing dates, see
  `rolling_beta`);
- `max_ffill=None` (or `0`) disables filling for that source, recovering the
  exact pre-`max_ffill` behavior.

Verified against real data: the benchmark recovers from 6,194 usable return
rows (no fill) to 6,635 (`max_ffill=5`, effectively the full 6,636-row panel
minus the one unrecoverable leading `NaN` from `pct_change` itself) — every
gap in the file today is short enough to fill. Risk-free is unaffected (0 raw
gaps today). This shifts the exact real-data figures quoted under
Consequences below (computed before `max_ffill` existed) slightly upward;
they were not re-measured after this change; the qualitative behavior they
describe (partial `beta` coverage, complete-case neutralization drop) still
holds.

**`rolling_beta` gained a second, independent fill stage against market's own
date calendar (`benchmark_calendar_max_ffill`/`risk_free_calendar_max_ffill`,
both defaulting to 5) — added later, while investigating ADR-0015's isovol
warm-up period.** *(Superseded by ADR-0016: this logic was extracted out of
`rolling_beta` into a standalone `calendar.py`/pipeline stage once a second
consumer was expected. `rolling_beta` no longer has these parameters —
`BetaConfig`'s fields of the same name and the underlying behavior are
unchanged, just relocated. The rest of this paragraph is kept as the
original record of why the fill exists at all.)* Distinct from the `max_ffill` above: that fill only ever
sees rows the benchmark/risk-free source *actually has* — it fills `NaN`
*values* at *existing* index positions, so a date that's entirely absent as a
row (not merely null) passes through it completely untouched, no matter how
large `max_ffill` is set. Verified directly against `risk_free_returns.parquet`:
`2020-01-02`/`2020-01-03` (real NYSE trading days, present in the benchmark
file) are simply missing rows in the risk-free file — `2019-12-31` is
followed immediately by `2020-01-06` — so `read_risk_free_returns`'s own
`max_ffill=5` has nothing to act on there. The new stage reindexes
`benchmark_returns`/`risk_free_returns` onto `market`'s own unique date
calendar *inside* `rolling_beta` (turning "row doesn't exist" into "row
exists and is null," which `ffill` can then act on), before either is
subtracted or subtracted from. The two components are filled **independently,
then combined** — not the other way around — because risk-free rates move
slowly (forward-filling one is a reasonable proxy) while benchmark returns
don't (filling the *combined* excess return risks silently carrying forward a
stale value on a day the market actually moved); verified by a dedicated test
constructing a case where the two fills would disagree
(`test_components_filled_independently_not_the_combined_difference`). Real
data was systematically affected, not an isolated incident: 16 risk-free
dates missing this way in just the first ~7 months of the panel, clustered at
the start of nearly every calendar month. `RollingBetaReport` gained
`n_benchmark_calendar_dates_filled`/`n_risk_free_calendar_dates_filled` to
make the fill's real bite visible.

**Rows with a NaN exposure are dropped (complete-case), not filled.** For each
date/signal-column pair, `neutralize_signals` builds the exposure matrix `B_t`
(intercept + every exposure's own column(s)) and keeps only rows where every
exposure column and the signal column are non-null
(`complete_exposures & block[column].notna()`); excluded rows get a null
`{column}_neutral` rather than a fabricated one. This is the same complete-case
convention `neutralize_signals` already used pre-wiring — the beta exposure
just makes it visible in real data, since `beta` is null for ~17% of rows
(insufficient rolling history, or missing benchmark/rf coverage on early
dates; see Consequences below), and every one of those rows drops out of that
date's cross-sectional regression entirely.

**Industry neutralization added as a second exposure: `gsector` (GICS sector),
via the already-generic `CategoricalExposure`.** No code change was needed —
`neutralize_signals` already accepted a mix of continuous/categorical
exposures in one call, and `gsector` (10 GICS sector codes, ~1.9% null)
already flows untouched from `read_fundamentals` through every intervening
stage (each stage `.copy()`s and adds columns, never drops one), all the way
to `scored`. This was purely a config addition:
`{"type": "categorical", "column": "gsector"}` alongside the existing `beta`
exposure. Taxonomy choice (GICS sector vs. a Fama-French industry scheme,
also present in the funda extract as `ffi5`/`ffi10`/`ffi12`/`ffi17`/`ffi30`/
`ffi38`/`ffi48`/`ffi49`) was raised with the user; `gsector` was chosen for its
coarser groups (fewer, larger per-date groups → less rank-deficiency exposure
than e.g. `ffi48`'s much finer split).

**`config/backtest.example.json` updated** to include a `beta` section (real
`data/russell_returns.parquet`/`data/risk_free_returns.parquet` paths, defaults
for everything else) and a `neutralization` section neutralizing
`return_treated_raw_score` against both `beta` and `gsector` — giving the
example config full end-to-end coverage of every stage now in the pipeline.
Re-verified against real data with both exposures configured: `n_valid_rows`
drops from beta-only's 1,047,177 to 1,035,237 (gsector's own ~1.9% null rate
excludes additional rows on top of beta's gaps — expected, not a bug, since a
row now needs *both* exposures complete), `n_degenerate_dates` is 139 (vs.
144 beta-only), and `mean_r_squared` rises to ≈0.202 (vs. ≈0.093) — sector
dummies explain materially more of the raw score's cross-sectional variation
than beta alone, as expected.

## Alternatives Considered

- **Compute beta on the eligibility-restricted `market_universe` instead of
  `market_clean`**: rejected — already ruled out by `timeseries.py`'s own
  docstring before this ADR (would corrupt the rolling covariance/variance
  estimate with artificial gaps on ineligible dates); the wiring just had to
  respect that, not re-litigate it.
- **Skip a stage (raise or silently drop the exposure) when a `neutralization`
  section references an uncomputed column like `beta`**: rejected — the
  existing `neutralize_signals` "unknown column" error is already exactly the
  right behavior (config.py's docstring already promised this: "any
  neutralization exposure referencing it will fail with a clear 'unknown
  column' error"). Adding a pipeline-level special case would just be a second,
  redundant way to say the same thing.
- **Duplicate risk-free dates: average the conflicting rates** or **skip
  real-data verification and leave the gap undocumented**: both raised with the
  user; keep-last was chosen as the simplest deterministic rule that doesn't
  require deciding which of two vendor observations is "more correct."
- **Fill NaN exposures cross-sectionally (e.g. cross-sectional mean/median on
  that date) instead of dropping the row**: considered, deferred rather than
  rejected outright. A fill would let a row with a missing exposure (e.g. beta
  not yet estimable from insufficient history) keep a neutralized score instead
  of losing it, at the cost of imputing an exposure value that was never
  observed — a real methodological choice (which fill statistic, computed over
  which population) that changes the neutralized signal, not a free efficiency
  win. Complete-case drop was already the existing, tested behavior of
  `neutralize_signals` going into this ADR; wiring beta in was not treated as
  license to revisit it silently. Revisit if dropped-row volume from beta's
  early-history gaps proves too costly to downstream portfolio construction.
- **Calendar-fill the combined `market_excess` difference directly, instead
  of filling `benchmark_returns`/`risk_free_returns` independently first**:
  rejected — proven wrong on a constructed case
  (`test_components_filled_independently_not_the_combined_difference`):
  filling the combined difference after a gap would carry forward the *prior
  day's whole excess return* rather than combining today's real benchmark
  move with a reasonable risk-free proxy, silently blurring an actual market
  move on the filled day.

## Consequences

- Verified end-to-end against the full real WRDS panel via
  `config/backtest.example.json`: `run()` completes through all eight stages
  over 1,257,968 market rows. `beta` is computed for 1,047,177 rows (the rest
  null from insufficient history or missing benchmark/rf coverage on early
  dates — expected, not a bug); `neutralize`'s diagnostic for
  `return_treated_raw_score` shows `n_valid_rows == 1,047,177` (matches the beta
  count exactly, as expected since beta is the only exposure) and
  `mean_r_squared ≈ 0.093` across 144 degenerate (skipped) dates out of the full
  date range. (Pre-calendar-fill figures; see below.)
- **Re-verified after the calendar-fill addendum**: `n_beta_computed` rises
  from 1,047,177 to 1,070,454 (`n_risk_free_calendar_dates_filled=112`,
  `n_benchmark_calendar_dates_filled=0` — confirming the real gap was
  entirely on the risk-free side); `n_rows_missing_benchmark_or_rf` drops
  from ~114,000 to 2,000 (the residual being gaps longer than the 5-day
  tolerance, correctly still left null, not fabricated past that limit).
  Downstream, the beta warm-up period (first date with *any* non-null beta)
  tightens from day 139 to day 127 — within 1 of the theoretical 126
  (`min_periods`), the remaining 1-day gap being expected numerical/indexing
  slack rather than a further data issue. 4 new tests added to
  `tests/test_timeseries.py` covering the fill itself (within-tolerance,
  beyond-tolerance, independent-not-combined-fill, and disabled-via-`None`
  cases); `tests/test_config.py`'s existing beta config tests extended for
  the two new fields. Full suite: 213 passed.
- 30 new tests added (at the time of the original wiring, pre-calendar-fill):
  `tests/test_timeseries.py` (7, `rolling_beta` unit tests —
  analytic correctness, insufficient history, zero-variance degeneracy, aged-out
  missing benchmark data, per-security independence, risk-free subtraction,
  input validation), `tests/signals/test_neutralize.py` (12, `neutralize_signals`
  unit tests — closed-form OLS match, categorical-exposure demeaning, per-date
  independence, missing-exposure/missing-signal row exclusion, rank-deficiency
  degeneracy, multi-column independence, input validation), `tests/test_config.py`
  (6, `load_beta_config`/`load_neutralization_config`), `tests/data/test_io.py`
  (4, `read_benchmark_returns`/`read_risk_free_returns` including the duplicate-
  date tie-break), and `tests/test_pipeline.py` (5, stage wiring, the config-
  absent no-op case, beta flowing through to `scored`, the missing-exposure
  error, and the real-data end-to-end check). Full suite: 144 passed.
- Anyone already using `read_risk_free_returns` directly (nothing in this repo
  yet besides `compute_beta`) gets silently-deduplicated output from now on —
  a real behavior change for that function, not just a refactor, but there was
  no correct non-crashing prior behavior to preserve.
- The Portfolio Risk Model module (ch. 14, not yet built) can extend
  `timeseries.py` (e.g. `rolling_volatility`) using the same rolling-window
  mechanics `rolling_beta` already established, per that file's own docstring.
