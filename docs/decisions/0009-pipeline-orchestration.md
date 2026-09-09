# ADR-0009: Pipeline Orchestration

Date: 2026-08-12
Status: Superseded by ADR-0011 (stage order and outlier/signal call sites only;
stepwise-object design, config-parsing approach, and market-only universe
restriction rationale below still stand)

## Context

Every module built so far (cleaning, universe construction, outlier treatment,
signal construction, the as-of join) is a standalone function operating on whatever
DataFrame it's handed, deliberately, with no knowledge of the others. Composing them
into the actual chronological chain was explicitly left unbuilt each time it came up:
ADR-0006 named it outright ("whether cross-sectional bounds get computed over the
full cleaned panel or a universe-restricted subset is a pipeline-composition
decision... not something built into this module"), and ADR-0005 said universe
membership is "a `(security_id, date)` membership table, not the market data filtered
down to eligible rows... downstream modules join against this table." Concretely,
`clean_market_data`/`clean_fundamentals` were never invoked outside their own tests —
nothing in `config.py` or elsewhere read raw data and cleaned it before handing it to
universe/outlier/signal construction, despite every one of those modules' docstrings
assuming "cleaned market data" as their input.

The user raised this explicitly before Signal Neutralization (the guide's next
module): Neutralization needs both market- and fundamentals-sourced exposures
together (e.g. neutralizing a market-derived score against industry, which lives in
funda's `gsector`/`ffi*` columns) — exactly the composition gap that's been deferred
three times.

## Decision

**`BacktestPipeline`** (`src/backtester/pipeline.py`), a stepwise orchestrator built
via `BacktestPipeline.from_config(path)`, running the actual chronological chain:

```
read data sources
    -> clean (market, fundamentals independently)
    -> build_universe (market only, v1)
    -> treat_outliers (market: universe-restricted; fundamentals: full population)
    -> compute_raw_scores + combine_scores (market, fundamentals independently)
    -> as_of_join (market scores + fundamentals scores -> one PIT-safe joined frame)
```

**Stepwise object with inspectable per-stage attributes, not a pure function.**
Every stage (`load_data`, `clean`, `build_universe`, `treat_outliers`,
`construct_signals`, `join_market_fundamentals`) stores its result(s) as attributes
named after the stage — `market_clean`, `market_universe`, `market_treated`,
`market_scored`, `market_fundamentals_joined`, each paired with its existing report
type (`CleaningReport`, `UniverseReport`, `OutlierTreatmentReport`, `RawScoreReport`,
`AsOfJoinReport`) — left `None` until that stage runs. `run()` executes the full
chain; any stage can also be called individually to inspect intermediate state,
per CLAUDE.md's "I want to understand every important line of code." Each stage
validates its own prerequisite ran first, raising `PipelineStateError` rather than
failing on a `None` attribute somewhere downstream with a confusing traceback.

**Universe eligibility restricts the market stream only, not fundamentals** — agreed
with the user as the v1 scope. `market_universe` is `market_clean` inner-joined
against the universe membership table on `(security_id, date)`; `treat_outliers` and
`compute_raw_scores` then run on `market_universe`. The fundamentals stream is
cleaned and treated over its *full* cross-section, unrestricted. This is not a
silent leak: `join_market_fundamentals` (the pipeline's final stage) is driven from
`market_scored` rows via `as_of_join`, so a security absent from `market_universe`
never appears in `market_fundamentals_joined` either — eligibility is enforced at the
join, not by pre-filtering fundamentals' own statistics. Restricting fundamentals'
outlier bounds/z-scores to eligible securities too would need a reverse as-of
eligibility check (funda rows are monthly, universe membership is daily) that doesn't
exist yet — deferred, same boundary ADR-0005 already drew for funda-based
eligibility filters.

**Config parsed via the existing four `load_*_config` loaders, unchanged.**
`PipelineConfig`/`load_pipeline_config(path)` calls `load_data_sources_config`,
`load_universe_config`, `load_outlier_treatment_config`, and
`load_signal_construction_config` against the same path (each already handles its
own section being absent). This re-reads and re-parses the same small JSON file four
times rather than parsing once and threading a dict through — an explicit "local
implementation detail with no observable methodological consequence" per CLAUDE.md's
own carve-out (the file is tiny; the cost is a few extra syscalls, not a correctness
or architecture concern), traded for zero changes to four already-tested loader
functions.

**`market_fundamentals_joined` is exposed as a pipeline stage in its own right**,
not built as part of Signal Neutralization. Cross-source score combination itself
remains out of scope (ADR-0007) — this only produces the joined frame; whatever
Neutralization does with it (pulling `gsector`/size/beta as exposure columns) is that
module's own concern, decoupled from this orchestrator.

## Alternatives Considered

- **Pure function `run_pipeline(config) -> PipelineResult`** (immutable dataclass of
  every intermediate): rejected per user's explicit direction — a stateful object
  that can be stopped and inspected mid-chain fits this project's research/debugging
  workflow better than an all-or-nothing call.
- **Restrict fundamentals by universe too**: rejected for v1 — more methodologically
  correct per the guide, but requires infrastructure (reverse daily-to-monthly
  eligibility lookup) that doesn't exist yet, and eligibility is already correctly
  enforced by the time data reaches a joined frame.
- **Parse the JSON config once, refactor the four loaders to accept a dict**:
  rejected as unnecessary risk for this iteration — no methodological consequence,
  and it touches four working, tested functions for a savings of a few file reads.

## Consequences

- Verified end-to-end against the real WRDS data via `config/backtest.example.json`:
  `run()` completes through all six stages; `as_of_join_report` reproduces
  ADR-0008's exact previously-verified numbers (1,132,007 / 1,257,968 matched rows),
  confirming the orchestration didn't change any individual module's behavior.
- `clean_market_data`/`clean_fundamentals` are no longer orphaned — every module
  built so far is now reachable from one JSON config file through one object.
- Signal Neutralization can now be built directly against
  `pipeline.market_fundamentals_joined`, which already carries both market- and
  fundamentals-derived raw scores plus every funda pass-through column (`gsector`,
  etc.) needed for exposure construction — the composition gap flagged three times
  is resolved.
- If fundamentals-side universe restriction is added later, it's additive: a new
  `fundamentals_universe` attribute/stage slotting in before `treat_outliers`,
  without changing the market-side behavior already verified here.
