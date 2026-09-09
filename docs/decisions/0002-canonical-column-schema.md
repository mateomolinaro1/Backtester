# ADR-0002: Canonical column schema at the data I/O boundary

Date: 2026-08-12
Status: Accepted

## Context

`cleaning/market.py` and `cleaning/fundamentals.py` were originally written against WRDS's
native column names (`permno`, `prc`, `vol`, `shrout`, `ret`, `gvkey`, `adate`, `qdate`,
`public_date`). The user asked what would happen with a DataFrame from a different source
with different column names — the honest answer was "it breaks," since the names were
hardcoded throughout the cleaning logic.

## Decision

Introduce a canonical column schema (`data/schema.py`) that domain logic — cleaning today,
universe/signal/portfolio modules later — always operates on, regardless of source:

- Market: `security_id`, `date`, `price`, `volume`, `return`.
- Fundamentals: `security_id`, `company_id`, `annual_report_date`, `quarterly_report_date`,
  `available_date`, `ticker`, `cusip`.

Each source gets a `MarketColumnMapping` / `FundamentalsColumnMapping` (frozen dataclass:
canonical name -> that source's actual column name), passed to `read_market_data` /
`read_fundamentals` in `data/io.py`, which rename to canonical immediately after loading.
`WRDS_MARKET_COLUMNS` / `WRDS_FUNDAMENTALS_COLUMNS` are the default mappings for the WRDS
extracts already in `data/` (today's source names already equal the WRDS canonical
defaults, so existing behavior is unchanged).

Cleaning functions keep hardcoding column names — now the canonical ones. That's
intentional, not a remaining instance of the same problem: they operate on a well-defined
domain object (the canonical schema), the same way a function operating on a typed object
hardcodes an attribute name.

Only the columns cleaning actually touches are canonicalized. The ~90 other fundamentals
columns (`roa`, `bm`, `pe_op_basic`, ...) pass through under their source name unchanged;
per-source characteristic mapping is deferred to Signal Construction, where a strategy
declares which raw column maps to which characteristic — canonicalizing all 98 columns now
would be speculative given nothing downstream uses them yet.

## Alternatives Considered

- **Parameterize every cleaning function with column-name arguments** (e.g.
  `clean_market_data(raw, price_col="prc", ...)`): rejected — clutters every function
  signature, doesn't scale past a handful of columns, and pushes the same mapping decision
  down to every call site instead of making it once at the I/O boundary.
- **Canonicalize all 98 funda columns now**: rejected as premature/speculative per
  CLAUDE.md; nothing downstream reads those columns yet.

## Consequences

- A new data source (a different vendor, a different WRDS query with renamed columns) needs
  only a new `MarketColumnMapping`/`FundamentalsColumnMapping` instance passed to the
  reader — zero changes to cleaning or later modules.
- `data/io.py`'s "missing column" check now reports missing *source* columns (before
  renaming), which is more actionable for a source-specific bug than a canonical-name error
  would be.
- `CleaningReport.dropped_reasons` key `duplicate_dual_gvkey_quarantined_rows` was renamed
  to `duplicate_dual_company_quarantined_rows` to match the canonical vocabulary (any caller
  reading that key needs the new name).

**Addendum (2026-08-12):** `shares_outstanding` was removed from the canonical market
schema — `clean_market_data` never had a real methodological need for it (it was only used
for a `> 0` structural sanity check), and requiring every market data source to supply it
isn't a clear prerequisite for what "market data" means: some sources won't carry it in the
same file, and other asset classes don't have the concept at all (notional/face value for
bonds, open interest for futures). A source's raw shares-outstanding column (e.g. WRDS's
`shrout`) still passes through unchanged under its original name — it's just no longer part
of the fixed canonical vocabulary every source is forced to provide. If a later module (e.g.
market-cap-based universe eligibility) needs it, that module defines its own requirement
rather than it being baked into generic market-data cleaning.