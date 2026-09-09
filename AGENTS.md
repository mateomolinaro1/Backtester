# Backtester

## Role

Act as a senior quantitative researcher and software engineer.

The objective is to build a modular, correct, scalable, high-performance
backtesting engine suitable for quantitative research and production
deployment.

Correctness and methodological integrity take priority over implementation
speed.

## Authoritative Methodological Specification

The backtesting methodology is stored under:

`docs/backtesting/`

Start with:

`docs/backtesting/INDEX.md`

The index identifies which methodological specification files are relevant to each topic.

### Context policy

Do NOT read `docs/BACKTESTING_GUIDE.md` in full during normal development.

For each task:

1. Read `docs/backtesting/INDEX.md`.
2. Identify the methodological topics affected by the task.
3. Read only the corresponding specification files.
4. Read adjacent/dependent specification files only when required.
5. If necessary, search `BACKTESTING_GUIDE.md` for a specific concept,
   but never load the entire document simply for reference.

The backtesting methodology takes precedence over implementation convenience.

Do not silently deviate from it.

If implementation requirements conflict with the methodology, surface the conflict before modifying either the methodology or the code.
0

## Non-Negotiable Principles

- No look-ahead bias.
- All historical decisions must be point-in-time.
- Preserve the distinction between signal, target portfolio, current portfolio,
  implemented portfolio, trades, and realized returns.
- Prefer correctness and clarity before optimization.
- Design for extension,
- V1 must remain understandable line by line.
- Every module must have tests.
- Backtest results must be reproducible from code, data, configuration, model,
  and random-state identities.

## Decision Policy

Do not silently make methodological or architectural assumptions.

Ask before implementing choices that materially affect:
- economic behavior;
- portfolio weights;
- return or P&L calculation;
- point-in-time logic;
- signal construction;
- risk estimation;
- execution assumptions;
- transaction costs;
- statistical inference;
- public APIs;
- persisted schemas;
- core architecture.

For local implementation details with no observable methodological consequence,
use the simplest readable solution consistent with the existing architecture.

## Development Process

We build the backtester incrementally.

For every major module:

1. Read the relevant section of `docs/BACKTESTING_GUIDE.md`.
2. Explain the proposed mathematical-to-software mapping.
3. Identify unresolved methodological or architectural choices.
4. Discuss those choices with me before implementation.
5. Define the public interface.
6. Implement the smallest complete version.
7. Add unit tests.
8. Add or update integration tests.
9. Run tests before moving to the next module.

Do not implement several major modules at once unless explicitly requested.

I want to understand every important line of code.

## V1 Scope

V1 should implement the smallest complete end-to-end backtesting pipeline.

Initial implementation:
- Python;
- pandas;
- local Parquet data;
- equities first;
- deterministic characteristic-based signals first;
- scheduled rebalancing first;
- simple portfolio construction;
- simple proportional transaction costs;
- single-process execution.

Architecture must remain compatible with future:
- Polars;
- multiple asset classes;
- multiple countries and currencies;
- multiple data sources;
- event-driven strategies;
- model-based signals;
- live trading;
- API/SaaS deployment.

Do not implement those future capabilities unless required by the current task.

## Core Architectural Principles

- Composition over deep inheritance.
- Explicit domain objects.
- Small interfaces.
- Pure functions where practical.
- Avoid hidden mutable global state.
- Separate domain logic from I/O.
- Separate backtest methodology from data-source implementations.
- Separate signal generation from the backtesting engine.
- Keep research and production code paths as close as possible.
- Optimize only after correctness is established and measured.

## Simulation Architecture

The core simulation model must be compatible with event-driven execution.

Scheduled rebalances are one event type, not the fundamental definition of the
engine.

V1 may implement only scheduled rebalance events.

## Signal Provider Boundary

The backtester consumes point-in-time signals through a narrow abstraction.

The backtester does not own the full econometric / ML / NLP training pipeline.

A future signal provider may resolve model versions point-in-time:

`model_registry.get_as_of(date)`

Historical dates must never access future model versions.

## Strategy Types

The architecture must support:
- univariate strategies;
- composite/pillar strategies;
- meta-pillar/multifactor strategies;
- cross-sectional signals;
- time-series signals;
- combinations of both.

Composite signal weights may eventually be estimated dynamically and
out-of-sample.

## Calendars and Time

Calendar logic is a first-class domain concern.

Eventually support:
- different market calendars;
- holidays;
- time zones;
- trading sessions;
- rules such as "last open Friday of the month".

Do not hard-code generic calendar-day assumptions into core strategy logic.

## Canonical Domain Vocabulary

Use terminology consistent with the guide:

- raw data;
- point-in-time data;
- universe;
- characteristics;
- raw signal;
- neutralized signal;
- final signal;
- target weights;
- final weights;
- current / pre-rebalance weights;
- implemented weights;
- orders;
- trades;
- gross returns;
- net returns;
- NAV.

Do not collapse conceptually distinct stages merely because V1 makes them
numerically identical.

## Backtest Identity and Caching

The engine should support an optional deterministic backtest identity hash.

The identity must capture every input that can materially change the result,
including:
- strategy configuration;
- signal configuration;
- universe configuration;
- timing configuration;
- portfolio construction;
- risk model;
- costs;
- data identity;
- model identity;
- random state;
- relevant schema/code version.

Configurations must be canonicalized before hashing.

Never reuse cached results when an economically relevant identity component has
changed. Using cached results should be a user-controlled option, not a default.

## Performance

Performance and memory efficiency matter, but optimize only after correctness.

For V1:
- use pandas;
- prefer vectorized operations where they preserve clarity;
- avoid unnecessary copies;
- avoid loading unused columns or dates;
- load data lazily/by required range where practical;
- measure bottlenecks before introducing complexity.

A future Polars backend should not require rewriting the economic domain logic.

## Research and Production

The backtester must support both research and live production.

Core economic functions should be shared between backtest and live systems.

Outputs should eventually include sufficient information for an execution
engine, including:
- timestamped target positions;
- trades/orders;
- quantities;
- reference/execution prices;
- portfolio state;
- diagnostics;
- logs.

## Testing

Every module must have tests.

Prefer mathematical invariants and analytically solvable toy examples.

Tests should include:
- unit tests;
- integration tests;
- point-in-time / no-look-ahead tests;
- accounting reconciliation tests;
- deterministic reproducibility tests.

A module is not complete until its tests pass.

## Architecture Decisions

Material architecture decisions should be documented under:

`docs/decisions/`

Before changing an existing decision, read the relevant ADR.

## Coding Style

Prefer explicit, typed, readable Python.

Public APIs should be small and stable.

Use docstrings to explain contracts and economic meaning, not obvious Python
syntax.
