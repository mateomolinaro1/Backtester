# ADR-0005: Investment Universe Construction (V1 scope)

Date: 2026-08-12
Status: Accepted

## Context

The guide's Investment Universe Construction chapter defines $\mathcal{U}_t =
\{i \in \mathcal{U}_t^{\text{raw}} : E_{i,t}=1\}$: the eligible universe is the raw
point-in-time data (for us, whatever survives Data Cleaning) filtered by eligibility
rules. The user raised two real cases: (1) the supplied dataset already *is* the
intended universe (nothing to filter), and (2) it's a broader panel that needs
filtering down. Discussion clarified this isn't two code paths — it's the same
mechanism with zero vs. non-zero filters configured.

Two further scoping questions came up and were resolved by the user:

1. Whether to support index-membership-table eligibility (a security is in-universe
   because it's a constituent of some external index as of $t$) as a first-class
   mechanism, vs. treating "my data is already index-PIT-filtered" as purely an
   upstream data-supply concern.
2. Whether $\mathcal{U}_t$ should be recomputed daily (mechanical consequence of
   per-row filter evaluation on daily data) or on a periodic schedule with
   entry/exit buffer hysteresis (per the guide's reconstitution-frequency discussion).

## Decision

**Mechanism**: a single, generic, JSON-configured eligibility engine — not a fixed
enum of filter "types" (no separate `MinPriceFilter`/`MinMarketCapFilter` classes).
An `EligibilityFilter` is `(column, operator, value)`; `build_universe(market, filters)`
applies them sequentially (each narrows the previous result, matching the guide's
$\mathcal{U}_t^{(0)} \to \mathcal{U}_t^{(1)} \to \cdots \to \mathcal{U}_t$ pipeline) to
already-cleaned market data, returning a `(security_id, date)` membership table plus a
`UniverseReport` with per-filter funnel diagnostics (rows before/dropped/after).

Supported operators: `==`, `!=`, `>`, `>=`, `<`, `<=`, `in`, `not_in`, `is_null`,
`is_not_null` (the last two covering the guide's "data availability" eligibility
criterion). Every filter's `column` must already exist in the market DataFrame —
no implicit derivation (e.g. no built-in market-cap computation); the caller supplies
whatever columns their eligibility rules need, already present.

**"Already the universe" case**: no special code path. `filters=[]` (or the JSON
`universe` section entirely absent) means every row passes — `build_universe` still
runs, still returns a proper membership table and report, it just doesn't remove
anything. Per CLAUDE.md: "Do not collapse conceptually distinct stages merely because
V1 makes them numerically identical" — $\mathcal{U}_t^{\text{raw}}$ and $\mathcal{U}_t$
staying equal today doesn't mean the code should treat them as the same concept.

**Index-membership eligibility: out of scope for V1.** Same boundary already drawn for
raw data acquisition (project memory: `data-scope-pit`) — if the caller wants an
index-PIT universe, that's the upstream extraction's job; it shows up to us as an
already-filtered dataset (the "Case 1" above), invisible to this module. Adding a
membership-table mechanism later (a PIT constituents table with entry/exit dates,
joined against `security_id`) is additive — another way to compute $E_{i,t}$ feeding
the same $\mathcal{U}_t$ concept — not a redesign of what's built now.

**Reconstitution frequency: daily only for V1.** Filters are evaluated per
`(security_id, date)` row against the daily market panel, so $\mathcal{U}_t$
mechanically varies daily — this isn't a separate feature, it falls out of row-level
evaluation. Periodic reconstitution with entry/exit buffer hysteresis (the guide's
$M_{\text{entry}} > M_{\text{exit}}$ discussion, to reduce mechanical universe
turnover) is deferred.

**Output type**: a `(security_id, date)` membership table, not the market data
filtered down to eligible rows. Universe membership is kept as its own explicit
domain object — downstream modules join against it rather than receiving a pre-merged
frame, consistent with CLAUDE.md's canonical vocabulary keeping "universe" distinct
from "market data."

**Scope**: filters operate on cleaned *market* data only for V1, not a market+funda
join. Funda-based eligibility (e.g. a data-availability requirement on an accounting
characteristic) would need an as-of join between daily market dates and monthly
`available_date`-keyed funda data, which doesn't exist yet — deferred until that join
is actually built.

**Config**: `config.py` gains `UniverseConfig`/`load_universe_config`, reading the
optional `universe.filters` JSON section, following the same pattern as
`data_sources`.

## Alternatives Considered

- **Enumerated filter types** (`MinPriceFilter`, `MinMarketCapFilter`, ...) instead of
  generic column/operator/value: rejected per user's explicit direction — column names
  and thresholds belong in the JSON config, not hardcoded in Python, matching the same
  philosophy already applied to column mappings (ADR-0003).
  Also sidesteps the market-cap-sourcing question entirely: since any column already
  present in cleaned market data can be filtered on, a source providing a precomputed
  `market_cap` pass-through column (like WRDS) just works, with no special-casing in
  this module.
- **Index-membership support now**: rejected as premature scope for this module; no
  PIT constituents data source exists yet to build against.
- **Periodic reconstitution with buffers now**: rejected as premature; daily
  row-level evaluation is simpler and sufficient until an actual rebalance-frequency
  decision is made in Portfolio Construction.

## Consequences

- Verified against the real WRDS data: an `exchcd in [1, 3]` filter correctly drops
  the 1,170 AMEX (`exchcd=2`) rows out of 1,257,968 cleaned market rows, with the
  funnel diagnostic reporting exactly that.
- A future filter needing a column not yet in cleaned market data (e.g. a
  characteristic requiring an as-of join to funda) will raise a clear "unknown
  column" error rather than doing something wrong — the module never derives columns
  implicitly.
- If index-membership eligibility is added later, it likely becomes a second
  mechanism alongside `EligibilityFilter` (e.g. a `MembershipFilter` consuming a PIT
  constituents table) rather than a variant of the column/operator/value shape, since
  it isn't expressible as a per-row column condition on the market panel alone.