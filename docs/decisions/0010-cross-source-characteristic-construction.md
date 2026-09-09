# ADR-0010: Cross-Source Characteristic Construction

Date: 2026-08-12
Status: Proposed

## Context

ADR-0007 scoped `combine_scores` to same-source combination only, and named the
gap explicitly: "combining a market-derived score with a fundamentals-derived
score needs an as-of join... that doesn't exist yet." ADR-0008/0009 built that
join, but only closed half the gap. `market_fundamentals_joined` lets
`combine_scores` mix an *already-computed* market raw score with an
*already-computed* funda raw score (e.g. average of a momentum z-score and a
quality z-score) — that needs no new code, since `combine_scores` already
operates on any columns in one frame.

It does not cover the guide's own leading example of a firm-level
characteristic (ch. 08, $x_{i,t}^{(k)}$): "valuation ratios... or any other
firm-level quantity." A valuation ratio like book-to-price mixes a market
column (price, daily) with a funda column (book value, monthly-as-of) *before*
either is standardized — it is a new characteristic, not a combination of two
existing scores. There is currently no pipeline stage that constructs a
characteristic from columns spanning both sources.

This also surfaces an ordering wrinkle. The current chain
(`clean -> universe -> treat_outliers -> construct_signals -> as_of_join`,
ADR-0009) runs outlier treatment and scoring on the market and fundamentals
streams *independently*, before the join. A cross-source characteristic can't
exist until after the join, so it structurally cannot go through that same
outlier-treatment/scoring pass — it needs its own pass, scoped to the derived
column(s), running after `join_market_fundamentals`.

## Decision

Not yet made — this ADR is a placeholder scoping the problem, written at the
user's request for later discussion. Sketch only.

**Likely shape**, consistent with every other module in this codebase:

- A new stage, `construct_cross_source_characteristics` (name TBD), runs after
  `join_market_fundamentals`. Input: `market_fundamentals_joined`. Output: the
  same frame with new characteristic column(s) added — never mutates existing
  columns, matching every prior module's convention.
- The derived column(s) then need outlier treatment and scoring like any other
  characteristic. Likely reuses the existing generic `treat_outliers` and
  `compute_raw_scores` (both already operate on "whatever DataFrame and column
  list you hand them" — no cross-source knowledge required) applied to
  `market_fundamentals_joined` rather than building new transform types.
- `combine_scores` then mixes cross-source raw scores with the existing
  per-source ones already sitting in the joined frame — no change needed
  there.
- Resulting stage order:
  `... -> as_of_join -> construct_cross_source_characteristics ->
  treat_outliers (joined) -> compute_raw_scores (joined) -> combine_scores`.

**Vocabulary**: per CLAUDE.md's canonical terms, this is *characteristic
construction* ($x_{i,t}^{(k)}$), a stage upstream of and distinct from *raw
score* construction ($s_{i,t}^{(k),\mathrm{raw}}$) — must not collapse into
`compute_raw_scores` itself even though V1 will likely wire them back-to-back.

**PIT note**: no new look-ahead surface — the stage operates strictly on
`market_fundamentals_joined`, which is already PIT-safe by construction
(ADR-0008's backward as-of join). Worth stating explicitly in the eventual
"Accepted" version rather than leaving it implied.

## Open questions to resolve with the user before implementing

1. **V1 scope of the transform**: simple ratio construction only
   (`output = direction * numerator / denominator`, mirroring the
   z-score/robust-z-score precedent of shipping the narrow case first), or
   general arithmetic expressions? Recommendation: ratio-only for V1 — it
   covers the dominant use case (valuation ratios) and avoids building an
   expression parser before there's a concrete second use case.
2. **Config schema**: new top-level section (e.g. `cross_source_characteristics:
   [{output_column, numerator_column, denominator_column, direction}]`), or
   folded into the existing `signal_construction` section? Existing sections
   are per-source (`market`/`fundamentals`); this is neither.
3. **Division-by-zero / null handling**: same "never silently produce inf/NaN"
   principle as ADR-0007's degenerate-date handling — needs an explicit
   convention (e.g. null denominator or zero denominator -> null characteristic,
   tracked via a diagnostic) before implementation, not decided ad hoc in code.
4. **Does outlier treatment run on the joined frame reuse the existing
   `OutlierTreatmentConfig` structure**, or does the joined-frame pass need its
   own config group alongside `market`/`fundamentals`?

## Alternatives Considered

Not yet evaluated in depth — deferred along with the decision itself. The one
alternative already ruled out implicitly: doing this inside `combine_scores`
(rejected, since that function's contract is "combine already-scored columns,"
not "construct a new characteristic from raw inputs" — conflating the two
would violate the guide's own distinction between characteristics and scores).

## Consequences

None yet — no code changes accompany this ADR. Recorded now so the gap
identified today isn't rediscovered from scratch later, and so implementation
starts from these open questions rather than from an empty page.

**Update (ADR-0011)**: the pipeline reorder that fixed the universe-restriction
bug moved `market_fundamentals_joined` earlier in the chain — it now exists
*before* `treat_outliers`/`compute_raw_scores` run, not after. This is exactly
where a future `construct_cross_source_characteristics` stage would need to
sit, so ADR-0011 settles this ADR's implicit "where does this go" question for
free. The open questions above (ratio-only vs. general expressions, config
schema, null/zero-denominator convention) are otherwise unaffected.