# ADR-0014: Direct Pure Alpha Portfolio Construction (V1 scope)

Date: 2026-08-13
Status: Accepted

## Context

Next module per the guide's chapter ordering: "From Signals to Portfolio Weights"
(ch. 13), specifically its "Direct Pure Alpha Construction" path -- turning the
final signal `s_final` into portfolio weights without a numerical optimizer. The
user supplied a much more detailed specification than the guide chapter alone,
`docs/backtesting/12.2_direct_pure_alpha_construction.md`, which itself contains
two successive drafts: an initial six-stage sketch (mapping -> dollar-neutral ->
exposure-normalized -> beta-neutral -> reconciliation -> isovol) and a later,
authoritative "Recommended Closed-Form Approach" section that supersedes it.

## Decision

**Scope, agreed with the user before implementing**: signal-to-weight mapping,
joint dollar+beta-neutral projection, gross-exposure restoration, and the two
diagnostic checkpoints from the six-stage sketch (kept, not skipped, per the
user's explicit request). Isovol (portfolio-level volatility targeting) is
out of scope -- deferred to its own iteration (see below).

**The authoritative construction is a single joint Euclidean exposure
projection, not two-scalar long/short leg rescaling.** The doc's own "Why
Two-Scalar Leg Rescaling Is Not the Default" section proves this: with only
two free parameters (one multiplier per leg), at most two of
{dollar-neutral, beta-neutral, gross-exposure} can be hit exactly. The user
explicitly required both dollar and beta neutrality preserved, which rules
out leg rescaling as the default mechanism. The closed-form projection has
`N` degrees of freedom (one per security) instead of 2:

```
A_t = [1, beta_t]                                    (intercept + beta, N x 2)
w^BN = w~ - A_t (A_t'A_t)^-1 A_t' w~ = M_A w~         (closed-form projection)
w^PA = G * w^BN / ||w^BN||_1                          (gross restored, one scalar)
```

Because `A_t'w = 0` is a homogeneous (zero-target) constraint, the subsequent
scalar gross-normalization cannot disturb it -- `w^PA` satisfies
`1'w^PA=0`, `beta'w^PA=0`, and `||w^PA||_1=G` all exactly (up to floating
point), not approximately. Verified: see Consequences.

**This closed-form projection is exactly what `neutralize_signals` already
computes.** `A(A'A)^-1A'w` residualized is the identical OLS normal-equations
math as `gamma = lstsq(B, y); residual = y - B@gamma`, with the same
always-included intercept, same per-date grouping, and same rank-deficiency/
degenerate-date null handling already tested in ADR-0012. So the "Beta
Neutralization" stage is implemented as a direct, unmodified call to
`neutralize_signals`, treating the raw mapped weight column as if it were a
"signal" being neutralized against `[intercept, beta]` (or any other
configured exposures) -- no new regression/projection math was written.
`neutralize.py`'s previously-private `_build_exposure_matrix` was promoted to
a public `build_exposure_matrix` (renamed, `INTERCEPT_COLUMN` un-prefixed
too) since this module's invariant diagnostics need the identical matrix
to verify the same exposures are actually zero in the final weights.

**A security with missing beta that date is excluded (null -> effectively no
position), not an error.** Matches `neutralize_signals`'s existing
complete-case convention exactly, inherited for free by reusing it unmodified
-- consistent with beta's own real gaps (insufficient rolling history) from
ADR-0012.

**The two diagnostic checkpoints (`dollar_neutral`, `exposure_normalized`)
are computed, per the user's explicit request, but do NOT feed into the
authoritative construction.** They're derived directly and independently
from `raw_mapped` (simple demeaning; symmetric long/short leg
normalization), in parallel with the joint projection -- not chained through
each other. The doc is explicit that chaining (demean -> normalize legs ->
beta-adjust -> tolerate resulting net drift) would reintroduce exactly the
disturbance the closed-form projection avoids ("the mathematically
authoritative Pure Alpha construction should not perform [that chain] when
the actual objective is exact zero net, exact zero beta, and fixed gross
exposure"). They exist purely for inspection/debugging/research, matching
`construct_pure_alpha_portfolio`'s docstring.

**Signal-to-weight mapping: `linear` (identity) and `tanh` for V1**,
deferred: rank-based, quantile, threshold, power, exponential/softmax,
conviction-weighted (guide ch. 13 lists all of these as alternatives; user
picked the two simplest -- a cardinal baseline plus the bounded mapping they
specifically asked about). `LinearWeightMapping` exposes no scaling
parameter since any constant would cancel out at gross-normalization.
`TanhWeightMapping(kappa)` defaults `kappa=1.0`.

**Isovol deferred to its own iteration.** `sigma_hat_PA,t = sqrt(w'Sigma_t w)`
needs a full covariance forecast `Sigma_t`, which doesn't exist yet (ch. 14,
Portfolio Risk Model, still "not yet built" per ADR-0012); the alternative
(estimating `sigma_hat_PA,t` from the Pure Alpha portfolio's own trailing
realized returns) needs portfolio return construction (ch. 21/22, also not
built) and would turn this from a single-pass cross-sectional stage into a
path-dependent one. `construct_pure_alpha_portfolio` produces the pre-isovol
structural Pure Alpha portfolio (`w^PA`) only.

**New `src/backtester/portfolio/` subpackage** (mirrors `cleaning/`/
`outliers/`/`signals/`): `types.py` (`WeightMapping` ABC +
`LinearWeightMapping`/`TanhWeightMapping`, `PureAlphaReport` -- a single flat
dataclass, not a per-column tuple like `NeutralizationReport`, since there's
one Pure Alpha book per run, not one per signal column) and `construct.py`
(`construct_pure_alpha_portfolio`). `config.py` gained an optional
`pure_alpha` section (absent -> `None`, same "whole stage skipped" convention
as `beta`, not the "empty list means no-op" convention used by
`neutralization`/`final_signal`, since `signal_column` has no sensible
default once the section exists at all). `pipeline.py` gained a
`construct_pure_alpha()` stage after `finalize()`.

## Alternatives Considered

- **Two-scalar long/short leg rescaling as the default beta-neutralization
  mechanism**: rejected -- proven in the source doc (and re-derived
  independently during discussion) to be unable to hit dollar-neutral,
  beta-neutral, and gross-exposure simultaneously with only two degrees of
  freedom. Kept as a diagnostic-only checkpoint (`exposure_normalized`), not
  the authoritative mechanism.
- **Skip the `dollar_neutral`/`exposure_normalized` diagnostic checkpoints
  for V1 minimalism** (the assistant's initial proposal): rejected by the
  user -- useful diagnostics, kept.
- **Auto-derive `pure_alpha`'s exposures from `neutralization.exposures`**:
  not done -- `pure_alpha` has its own independent `exposures` list in
  config (V1 example config uses `beta` only, not `gsector`, matching the
  source doc's own "V1 Implementation Decision": "include intercept/net
  exposure; market beta" as the default, with industry/country/style
  explicitly named as a later generalization, not a required V1 default).
- **Build a minimal single-factor isovol proxy now** (raised in an earlier
  discussion turn): superseded by the user's explicit decision to defer
  isovol entirely to its own iteration once a real risk-model approach is
  chosen.

## Consequences

- Verified exactness on synthetic data and against the full real WRDS panel
  via `config/backtest.example.json` (`return_treated_raw_score_neutral_final`
  mapped via `tanh`, projected against `beta`, `gross_exposure=2.0`):
  `n_valid_rows` = 1,035,237 (identical to the upstream neutralize stage's own
  count -- expected, since beta-nullness was already baked into the signal's
  own null pattern by that earlier stage), `max_abs_net_exposure` ~= 4e-16,
  `max_abs_projected_exposure` ~= 4.5e-16, `max_gross_exposure_error` ~= 9e-16
  -- all effectively exact, confirming the closed-form projection's proof.
- `neutralize.py`'s `_build_exposure_matrix`/`_INTERCEPT_COLUMN` are now
  public (`build_exposure_matrix`/`INTERCEPT_COLUMN`), exported from
  `backtester.signals`. Any future module needing the same per-date exposure
  matrix (e.g. a future portfolio-constraint or risk-model module) can reuse
  it the same way this one does.
- 23 new tests: `tests/portfolio/test_construct.py` (13 -- exact dollar/beta/
  gross invariants, no-exposures dollar-neutral-only case, diagnostic
  checkpoints computed correctly and independently of the authoritative
  path, missing-beta exclusion, degenerate-date handling, tanh bounding,
  input validation, multi-date independence), `tests/portfolio/test_types.py`
  (4 -- mapping correctness), `tests/test_config.py` (5 -- absent/loaded/
  unknown-method/missing-required-key cases), and `tests/test_pipeline.py`
  (1 new -- dedicated construction test against the beta/neutralization
  fixture, real-data end-to-end assertions folded into the existing
  end-to-end test). Two existing `tests/test_pipeline.py` tests were also
  extended (prerequisite-stage check, no-op-without-config case). Full
  suite: 186 passed.
- When the Portfolio Risk Model module (ch. 14) or portfolio return
  construction (ch. 21/22) eventually lands, isovol becomes additive --
  `w^PA -> w^PA,iso = lambda_t * w^PA`, a further scalar stage that (per the
  same homogeneous-constraint argument used throughout this ADR) provably
  preserves the neutrality already established here.