# ADR-0015: Isovol Volatility Targeting via Historical Xw (V1 scope)

Date: 2026-08-14
Status: Accepted

## Context

Deferred at the end of ADR-0014: the Pure Alpha portfolio (`w^PA`) needs an optional
final risk-scaling step, `w^PA,iso = lambda_t * w^PA`, `lambda_t = sigma*/sigma_hat_PA,t`.
This needs an ex-ante portfolio volatility estimate, which needs *some* risk model --
and at the time, none existed (`timeseries.py` only had single-factor rolling beta).

The user initially wanted three risk models for V1 (single-factor, historical sample
covariance, Ledoit-Wolf shrinkage) as a proper `risk/` module extending ch. 14 (Portfolio
Risk Model). Two more detailed specs surfaced during discussion --
`docs/backtesting/12.3_isovol.md` (the generic `sigma_hat = sqrt(w'Sigma w)` scaling
interface) and `docs/backtesting/12.3_historical_portfolio_volatility_xw.md` (a specific,
much cheaper way to compute the historical estimator's volatility without ever
materializing `Sigma_t`) -- after which the user rescoped V1 down to *only* the
historical `Xw` estimator, deferring single-factor and Ledoit-Wolf entirely.

## Decision

**V1 implements exactly one risk model: the historical `Xw` estimator.** Per
`12.3_historical_portfolio_volatility_xw.md`: for the *current* Pure Alpha weights
`w_t^PA`, held fixed, apply them retroactively to the trailing `L`-day return panel
`X_t` and take the sample standard deviation of the resulting hypothetical return
series -- `sigma_hat_PA,t = Std(X_t w_t^PA, ddof=1)`. This is algebraically identical
to `sqrt(w'Sigma_t w)` for the historical sample covariance estimator (proven in the
doc via `Var(X_t w) = w'[(1/(L-1))(X_t^c)'X_t^c]w`), but needs no `N_t x N_t` matrix,
no missing-data-driven positive-semi-definiteness problem, and no per-pair covariance
at all -- only a weighted sum of returns per historical date.

**New `src/backtester/risk/` subpackage** (`historical.py`,
`historical_portfolio_volatility`), separate from `portfolio/`: this is risk
*estimation*, not weight construction. Deliberately generic-interface-compatible with
`12.3_isovol.md`'s explicit ask ("the portfolio volatility estimator should consume
[risk] without requiring knowledge of how it was estimated") even though V1 has only
one implementation -- `portfolio/isovol.py`'s `apply_isovol_scaling` takes a
precomputed date-indexed volatility `pd.Series` as input and has no import of, or
knowledge of, `risk.historical`. A future single-factor or Ledoit-Wolf estimator (both
explicitly deferred, not rejected) would only touch `risk/`, never `portfolio/isovol.py`.

**Missing-data policy: per-security exclusion, not per-date row-dropping.** The doc
leaves this genuinely open ("must define explicitly... configurable and tested
independently"). The first implementation used row-dropping -- a historical date
included in `X_t` only if *every* currently-held security had a return that day. This
was **verified wrong against real data**, not just theorized: real Pure Alpha books
hold ~925 securities per date on average, and requiring zero gaps across the *entire*
held set over a 252-day window made 1,118 of 1,258 real dates degenerate
(`n_degenerate_insufficient_history`), i.e. one gappy name among hundreds killed
nearly the whole panel. Fixed to per-security exclusion instead: a held security with
*any* gap in the window is dropped from the estimate specifically (still holding its
normal portfolio weight elsewhere); every other held security, and every one of the
`window` trading dates, is retained in full. Re-verified: 1,119 of 1,258 dates get a
computed volatility, mean security coverage ~77%. Never fabricates a 0% return for a
gap either way (the doc's explicit "Missing Return != 0% Return" requirement holds
under both policies) -- only the unit of exclusion changed, from "date" to "security."
`n_dates_with_excluded_securities`/`mean_security_coverage` in the report make the
policy's real-world bite visible rather than silent.

**The remaining 139 uncomputed real dates were also silently uncounted, until asked
about and traced.** `n_volatility_computed` (1,119) didn't equal `n_dates` (1,258),
and none of the three degenerate counters accounted for the gap -- because `held.empty`
(no security holds a nonzero weight that date at all) fell straight to a bare `NaN`
with no counter incremented. Traced to the pipeline's own beta warm-up: `beta` needs
`min_periods=126` trading days before it exists at all, so `pure_alpha` has zero
nonzero-weight securities on every date before that (verified directly: 0 held
securities on the last uncomputed date, 2020-07-21; first computed date is 2020-07-22,
immediately after). Not a bug in the estimator's *math* -- but a real gap in the
report's own stated purpose (make degenerate-date reasons visible, not silent). Split
into two new counted fields: `n_degenerate_no_holdings` (this case) and
`n_degenerate_date_not_in_market` (a weights/market date mismatch, not expected in
normal pipeline use but structurally distinct). Re-verified: `n_degenerate_no_holdings`
now accounts for exactly the 139-date gap.

**`ddof=1` needs >= 2 observations, enforced regardless of a smaller configured
`min_periods`.** `np.std(x, ddof=1)` on a single-observation window is a 0/0 that numpy
warns about and returns `NaN` for -- surfaced by a test fixture using `min_periods=1`
(deliberately, to fit a 3-row toy panel) and fixed by checking against
`max(min_periods, 2)`, not `min_periods` directly.

**Zero-variance check needs a tolerance, not exact equality.** Unlike `rolling_beta`'s
`var == 0.0` check (a direct `.var()` call on raw data, which pandas computes exactly
for constant input), `sigma` here comes from a matrix-vector product (`X @ w`), so
genuinely-constant hypothetical returns land near but not exactly at `0.0` after
floating-point rounding through the multiply-and-sum. Caught via `sigma < 1e-12`
(~1e10 below any real daily-return volatility) instead.

**Target volatility: annualized in config, de-annualized internally.** Per the user's
explicit choice: `target_volatility_annualized` (e.g. `0.10` for 10%/year) divided by
`sqrt(periods_per_year)` before comparing to the daily `sigma_hat_PA,t`.
`periods_per_year: null` (default) auto-detects from the market panel's own date
column -- median distinct trading dates per calendar year -- rather than hardcoding
252, per CLAUDE.md's "calendar logic is a first-class concern, don't hard-code
generic assumptions." An explicit value overrides auto-detection.

**Optional leverage cap**, per the user's explicit choice: `lambda_t = min(sigma*_daily
/ sigma_hat_PA,t, max_leverage)`. `max_leverage: null` (default) is uncapped.

**Two separate pipeline stages, one combined config section.** `estimate_portfolio_volatility()`
(risk estimation) and `apply_isovol()` (generic scaling) are distinct methods/attributes
-- per CLAUDE.md, "no two conceptually distinct stages collapsed into one" -- even
though both are gated by the single `isovol` JSON section (V1 has only one estimator,
so a separate `portfolio_risk` section would be premature). `estimate_portfolio_volatility`
requires `config.pure_alpha` to also be present (raises a clear `ValueError` otherwise
-- isovol has no portfolio to estimate risk for without one), distinct from the
"prerequisite stage not called yet" `PipelineStateError`.

## Alternatives Considered

- **Three risk models (single-factor, historical, Ledoit-Wolf)**: the user's initial
  ask, rescoped down after reading `12.3_historical_portfolio_volatility_xw.md` showed
  the historical estimator alone needs no `N x N` matrix at all for V1's purposes.
  Single-factor and Ledoit-Wolf are deferred, not rejected -- both remain additive to
  `risk/` later, per the generic-interface decision above.
- **Materializing a full `N_t x N_t` sample or Ledoit-Wolf-shrunk covariance matrix**:
  considered (and partially scoped -- missing-data pairwise-vs-listwise tradeoffs,
  `sklearn.covariance.LedoitWolf` for the shrinkage intensity) before the `Xw` doc
  surfaced. Rejected for V1 once the algebraically-equivalent, much cheaper `Xw`
  shortcut was confirmed sufficient for isovol's actual need (a scalar, not a matrix).
- **Row-dropping missing-data policy** (drop a whole historical date if any held
  security lacks a return): implemented first, then replaced after real-data
  verification showed it degenerate on ~89% of dates. Kept as a documented lesson in
  this ADR rather than silently rewritten, since it was a real, measured failure, not
  a hypothetical one.
- **Exact `sigma == 0.0` degenerate check** (matching `rolling_beta`'s convention):
  rejected after a test caught it missing real floating-point-noise cases; replaced
  with a `1e-12` tolerance.

## Consequences

- Verified exact-arithmetic correctness against a hand-computed `Xw` on synthetic data,
  and end-to-end against the full real WRDS panel via `config/backtest.example.json`
  (`target_volatility_annualized=0.10`, `max_leverage=4.0`, `window=252`,
  `min_periods=126`): 1,119 of 1,258 dates get a computed volatility (139 early-panel
  dates match exactly between the risk-estimation and isovol reports as
  "insufficient calendar history"), mean security coverage ~77%, leverage cap binds on
  11 dates, mean scale factor ~2.3x.
- 23 new tests: `tests/risk/test_historical.py` (10 -- exact `Xw` match, zero-weight
  exclusion from the coverage requirement, per-security gap exclusion, all-held-gappy
  degeneracy, insufficient calendar history, zero-variance tolerance, input validation,
  multi-date independence), `tests/portfolio/test_isovol.py` (8 -- scale-factor math,
  leverage cap, missing/null forecast volatility, same-lambda-per-date invariant,
  frequency auto-detection, input validation), `tests/test_config.py` (4 -- absent/
  loaded/overridden/missing-required-key cases), and `tests/test_pipeline.py` (1 new --
  dedicated isovol test against the beta/neutralization fixture). Three existing
  `tests/test_pipeline.py` tests were also extended (prerequisite-stage check, no-op-
  without-config case, real-data end-to-end assertions). Full suite: 209 passed.
- `risk/` now exists as its own subpackage with room to grow -- a future single-factor
  or Ledoit-Wolf estimator adds a sibling module there, unifies with
  `historical_portfolio_volatility` only through `apply_isovol_scaling`'s
  already-generic `forecast_volatility: pd.Series` parameter, and touches no code in
  `portfolio/`.
- The `w^PA,iso` output is pre-isovol-diagnostic-preserving: `pipeline.pure_alpha`
  (pre-scaling) and `pipeline.isovol` (post-scaling) both remain inspectable
  attributes, matching `12.2_direct_pure_alpha_construction.md`'s "preserve both
  structural and risk-scaled Pure Alpha weights" requirement.