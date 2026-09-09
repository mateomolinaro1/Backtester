# ADR-0013: Final Signal Construction (V1 scope)

Date: 2026-08-13
Status: Accepted

## Context

Next module per the guide's chapter ordering: "Final Signal Construction" (ch. 11),
turning the neutralized signal `s_neutral` into the final investable signal `s_final`
consumed by portfolio construction (ch. 13). The chapter bundles five sub-transforms:
post-neutralization standardization, multiple-signal combination, signal smoothing,
turnover-aware adjustment, and confidence weighting.

## Decision

**Scope, agreed with the user before implementing**: post-neutralization
standardization only.

- **Multiple-signal combination**: not newly built — already effectively covered.
  `combine_scores` (ADR-0007) already runs pre-neutralization on raw scores, and the
  chapter's own algebra shows combination-before-neutralization and
  neutralization-before-combination commute under linear neutralization with fixed
  cross-sectional weights (`M_{B,t}(sum_k alpha_k s_k^raw) = sum_k alpha_k M_{B,t}
  s_k^raw`), which is exactly this pipeline's shape. Nothing new needed.
- **Signal smoothing and turnover-aware adjustment**: deferred — both need the
  *previous* period's final signal as an input (`s_{i,t-1}^final`/`s_{i,t-1}^adj`), a
  temporal dependency no current stage carries. Building it now would mean inventing
  state rather than consuming something the pipeline already produces.
- **Confidence weighting**: deferred — needs a confidence measure (data quality,
  model prediction uncertainty, ensemble disagreement, etc.) that doesn't exist for
  V1's deterministic characteristic-based signals (CLAUDE.md's V1 scope explicitly
  excludes model-based signal construction, ch. 9, for now).

**Mechanism**: post-neutralization standardization is mathematically identical to
raw-score standardization (ADR-0007) — cross-sectional z-score/robust z-score, one
date-group at a time, same degenerate-date (std/MAD == 0 → null, not division by
zero) handling. Rather than reuse `compute_raw_scores` directly (which would tag the
output `{column}_raw_score`), a new, separate function reuses the same
`ScoreTransform` types (`ZScoreTransform`/`RobustZScoreTransform`, unchanged) but
produces a distinctly named `{column}_final` output and its own `FinalSignalReport`/
`FinalSignalDiagnostic` — per CLAUDE.md: "Do not collapse conceptually distinct
stages merely because V1 makes them numerically identical." A neutralized-and-
standardized signal is the guide's `s_final`, not another raw score, even though the
transform math is shared.

- `src/backtester/signals/finalize.py`: `standardize_final_signal(data, transforms,
  date_column="date") -> tuple[DataFrame, FinalSignalReport]`. Every transform's
  `column` must already exist in `data` — typically a `{...}_neutral` column, but not
  enforced; a signal that skipped neutralization can be standardized directly.
- `config.py`: new optional `final_signal` section, `{"standardizations": [{"column":
  ..., "method": "zscore"|"robust_zscore", "direction": 1}]}` — explicit column list,
  independent of `neutralization.signal_columns` (not auto-derived from it), matching
  every other stage's "operates on whatever it's handed" philosophy and correctly
  covering the case where a signal wasn't neutralized. Reuses
  `_score_transform_from_json` verbatim (same shape as `signal_construction.scores`).
- `pipeline.py`: new `finalize()` stage after `neutralize()`, storing
  `self.final`/`self.final_signal_report`. Always runs, even with an empty
  `final_signal` section (no-op copy) — same convention as `treat_outliers`/
  `construct_signals`/`neutralize`.

**`direction` stays in the transform, unrestricted, by default 1.** `ScoreTransform`
already carries a `direction` field from ADR-0007. Economically, a post-neutralization
re-standardization has no reason to flip sign — orientation was already baked in
during raw-score construction — but building a second, direction-less transform type
just to prevent an unlikely misconfiguration was judged not worth the duplication;
the default (1) is what every real config is expected to use.

**`config/backtest.example.json` updated**: adds a `final_signal` section
standardizing `return_treated_raw_score_neutral` via `robust_zscore`. The user also
changed `signal_construction`'s `return_treated` entry from `zscore` to
`robust_zscore`, for coherence between the raw-score and final-signal stages applied
to the same underlying signal.

## Alternatives Considered

- **Reuse `compute_raw_scores` directly for this stage** (same function, just pointed
  at `_neutral` columns): rejected — would tag output columns `{column}_raw_score`,
  conflating two conceptually distinct pipeline stages (raw score vs. final signal)
  that CLAUDE.md explicitly requires kept separate, even where V1 makes them
  numerically identical.
- **Auto-derive `final_signal`'s column list from `neutralization.signal_columns`**:
  rejected — would silently couple two independently optional stages; the chapter
  itself notes "not every strategy requires every transformation," including the case
  where a signal skips neutralization but should still be standardized.
- **Implement all five ch. 11 sub-transforms now**: rejected — smoothing and
  turnover-awareness need temporal state (previous final signal) not yet modeled
  anywhere in the pipeline; confidence weighting needs a confidence input V1's
  deterministic signals don't produce. Both are additive later without requiring a
  redesign of what's built now.

## Consequences

- Verified end-to-end against the full real WRDS panel via `config/backtest.example.json`:
  `return_treated_raw_score_neutral_final` computed for 1,035,237 rows (matches
  neutralization's own `n_valid_rows` exactly, as expected — standardization doesn't
  drop any additional rows beyond what neutralization already excluded), 0 degenerate
  dates, median exactly 0 (expected for a robust z-score) and std ≈ 1.38.
- 12 new tests: `tests/signals/test_finalize.py` (8 — original-column preservation,
  distinct-suffix check, zero-mean, degenerate-date handling, null propagation,
  unknown-column/date-column errors, empty-transforms no-op), `tests/test_config.py`
  (3 — absent-section default, loading, unknown-method error), and
  `tests/test_pipeline.py` (1 new — dedicated standardization test against the
  beta/neutralization fixture). Four existing `tests/test_pipeline.py` tests were
  also extended to cover the new stage: the prerequisite-stage check, `run()`'s
  full-stage-populated assertion, the no-op-without-config case, and the real-data
  end-to-end assertions. Full suite: 163 passed.
- The next stage in the guide (ch. 13, "From Signals to Portfolio Weights") consumes
  `{column}_final` the same way this module consumes `{column}_neutral` — same
  compositional pattern, no coupling.
- If smoothing, turnover-aware adjustment, or confidence weighting are added later,
  each needs its own new pipeline-level state (previous-period final signal for the
  first two; a confidence input source for the third) — additive to this module's
  existing `ScoreTransform`-based mechanism, not a redesign of it.