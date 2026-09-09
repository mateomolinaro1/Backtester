# ADR-0004: Combined (stacked) data source support

Date: 2026-08-12
Status: Accepted

## Context

The user wants to support supplying market and fundamentals data as a single
DataFrame/file (a researcher merging them upstream via Spark/SQL before handing it to
the backtester), in addition to today's two-separate-files case, and eventually as a
SaaS/API where a user picks among catalogued datasets (explicitly out of scope for now).

The first design considered — classify each row by checking whether all of a block's
canonical fields are non-null — was rejected before implementation: `return` (market)
and `ticker` (fundamentals) are legitimately null on genuine rows (a security's first
observation; the funda dual-company case from ADR/memory `funda-duplicate-gvkey-links`),
so that heuristic would misclassify real rows as belonging to neither block and crash
the load. There is no automatic/inferred approach that reliably avoids this — every
version of "guess from which columns are populated" reduces to the same problem in some
form.

The user also raised two related questions: does `security_id` appearing in both blocks
cause a collision, and how would this extend to more datasets later (estimates, alt
data)?

## Decision

Require an explicit discriminator column instead of inferring anything: the combined
file must carry one column (default name `"dataset"`, configurable) whose value on each
row names which dataset that row belongs to (default values `"market"` /
`"fundamentals"`, also configurable) — the natural output of a SQL/Spark
`SELECT *, 'market' AS dataset FROM ... UNION ALL SELECT *, 'fundamentals' AS dataset
FROM ...`.

`data/combined.py`'s `read_combined_data` reads the file once via the existing
`read_market_data`/`read_fundamentals` (each renames its own required columns to
canonical, unaffected by the other block's rows being present), then filters each
result by the discriminator value. Any row whose discriminator value isn't exactly one
of the two recognized values (including null) raises — the same "no defensible rule,
don't guess" policy used throughout cleaning.

Processing rows *before* applying either mapping — rather than transforming both
mappings globally then trying to reconcile them — is what resolves the collision
question for free: `security_id` appearing in both blocks is expected (it's the shared
join key spanning the whole stacked table); even a hypothetical accidental collision on
an unrelated raw column name resolves correctly, since each block's mapping is only ever
applied to that block's own row subset.

`config.py` gained a `CombinedDataSourcesConfig` alongside the existing
`SeparateDataSourcesConfig`, unioned as `DataSourcesConfig`. `data_sources` may specify
`"combined"`, or both `"market"` and `"fundamentals"`, but not an invalid mix — a
`"combined"` key present alongside `"market"`/`"fundamentals"` takes `"combined"` as
authoritative and raises `AmbiguousDataSourceConfigWarning` naming exactly what was
ignored, per the user's explicit request to make that precedence loud rather than
silent. `"combined": null` is treated identically to the key being absent.
`read_market_data_from_config`/`read_fundamentals_from_config` were replaced by a single
`read_data_sources(config) -> (market_df, fundamentals_df)` that dispatches on the config
type, so callers don't need to know which shape they're holding.

A single categorical discriminator column (not one 0/1 flag column per dataset, an
earlier version of the user's proposal) was chosen specifically for the N-dataset
future: adding e.g. `"estimates"` later is a third recognized value and a third key in
`data_sources`, not a new flag column and a new "did exactly one flag fire" check. This
mechanism doesn't know or care that today's two datasets are called market/fundamentals,
which also means it needs no changes to support a future asset class's combined source.

`AmbiguousDataSourceConfigWarning` lives in a new `src/backtester/exceptions.py`, not
inline in `config.py` -- the start of a single, stable place for custom exception/warning
types as more modules gain their own (point-in-time violations, universe infeasibility,
etc. per CLAUDE.md's Testing section). Everything else still raises plain `ValueError`;
a type only moves there once something actually needs to catch or filter it by name, not
preemptively for every validation failure.

## Alternatives Considered

- **Null-pattern classification** (all of a block's required fields non-null): rejected
  — breaks on `return`/`ticker`, the exact nullable-field cases already known to occur
  in the real data.
- **Two independent 0/1 flag columns** (the user's initial proposal): workable, but
  doesn't scale as cleanly past two datasets and allows representable-but-invalid states
  (both flags set, neither set) that a single categorical column rules out structurally.
- **Silently prefer one config shape without a warning**: rejected per explicit user
  request — an ignored `market`/`fundamentals` key should never be silently dropped.

## Consequences

- `tests/data/test_combined.py` includes a regression test
  (`test_handles_legitimately_nullable_fields_without_misclassifying_rows`) that would
  fail under the rejected null-pattern design — it directly encodes why the
  discriminator-column approach was chosen.
- A combined source still gets fully validated by the same `clean_market_data`/
  `clean_fundamentals` afterward — splitting only decides which rows go where, it
  performs no cleaning itself.
- S3/catalog-backed dataset selection for a SaaS deployment remains explicitly
  out of scope; nothing here precludes it, since it would be a new config shape (e.g. a
  `"catalog"` entry) resolved the same way `"combined"` vs `"market"`/`"fundamentals"` is
  today.