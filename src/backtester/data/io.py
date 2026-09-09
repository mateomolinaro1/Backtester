"""Schema-checked readers for the local Parquet data sources.

Raw data acquisition and point-in-time construction happen upstream of this
repository (see docs/decisions and project memory); these functions load an
already-extracted Parquet file and rename it to this backtester's canonical
column schema (see schema.py) using a per-source column mapping. Domain logic
downstream (cleaning and beyond) never sees a source's native column names.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from backtester.data.schema import (
    WRDS_FUNDAMENTALS_COLUMNS,
    WRDS_MARKET_COLUMNS,
    FundamentalsColumnMapping,
    MarketColumnMapping,
)


def read_market_data(
    path: str | Path, columns: MarketColumnMapping = WRDS_MARKET_COLUMNS
) -> pd.DataFrame:
    """Read a daily market data Parquet file and rename it to canonical columns."""
    df = pd.read_parquet(path)
    return _rename_to_canonical(df, columns.source_to_canonical(), source=str(path))


def read_fundamentals(
    path: str | Path, columns: FundamentalsColumnMapping = WRDS_FUNDAMENTALS_COLUMNS
) -> pd.DataFrame:
    """Read a fundamentals Parquet file and rename it to canonical columns."""
    df = pd.read_parquet(path)
    return _rename_to_canonical(df, columns.source_to_canonical(), source=str(path))


def _rename_to_canonical(
    df: pd.DataFrame, source_to_canonical: dict[str, str], *, source: str
) -> pd.DataFrame:
    missing = [src_col for src_col in source_to_canonical if src_col not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing expected source columns: {missing}")
    return df.rename(columns=source_to_canonical)


def read_benchmark_returns(
    path: str | Path, *, level_column: str = "Russell 1000", max_ffill: int | None = 5
) -> pd.Series:
    """Read a benchmark index-level Parquet file (date-indexed) and return its
    daily return series (``level.pct_change()``), indexed by date.

    Unlike market/fundamentals data, this isn't given a full column-mapping
    object -- there's exactly one field of interest (which level column to use),
    not a multi-field vendor schema, so a single ``level_column`` name is enough.

    The vendor extract has isolated NaN levels (a missing print on an
    otherwise-traded day -- a known upstream data-quality issue; raw
    acquisition is out of this project's scope). Filling is done on the
    *level*, before ``pct_change``, up to ``max_ffill`` consecutive missing
    rows: a filled day gets a 0% return (flat price -- the last known level
    carried forward), and the following day's return correctly spans the full
    move from that last known level, rather than the two NaN returns
    (``t`` and ``t+1``) a raw ``pct_change`` over a missing level would
    otherwise produce. Gaps longer than ``max_ffill`` are left unfilled and
    dropped by the trailing ``dropna()``, same as before this parameter
    existed. Pass ``max_ffill=None`` (or ``0``) to disable filling entirely.
    """
    levels = pd.read_parquet(path)[level_column]
    levels.index = levels.index.rename("date")
    if max_ffill:
        levels = levels.ffill(limit=max_ffill)
    returns = levels.pct_change().rename("benchmark_return")
    return returns.dropna()


def read_risk_free_returns(
    path: str | Path, *, rate_column: str = "rf_returns", max_ffill: int | None = 5
) -> pd.Series:
    """Read a risk-free daily return Parquet file (date-indexed), already in
    return form (no ``pct_change`` needed, unlike the benchmark's price levels).

    The vendor extract behind this file has duplicate dates with slightly
    conflicting rates (a known upstream data-quality issue -- raw acquisition
    is out of this project's scope). Rather than raise on a downstream reindex
    against a non-unique index, this keeps the *last* occurrence of each
    duplicated date and drops the rest -- a deliberate, documented tie-break
    (ADR-0012), not a silent one.

    Isolated NaN rates (none currently in the real file, but not guaranteed by
    the vendor) are forward-filled directly -- there's no price level here to
    fill instead, and carrying a short-term rate forward across a single
    missing day is the standard practical assumption -- up to ``max_ffill``
    consecutive missing rows. Rates left unfilled past that limit stay NaN
    (unlike the benchmark, this function doesn't drop rows -- callers reindex
    against this series and already handle missing dates, see
    ``timeseries.rolling_beta``). Pass ``max_ffill=None`` (or ``0``) to
    disable filling entirely.
    """
    rf = pd.read_parquet(path)[rate_column]
    rf.index = rf.index.rename("date")
    rf = rf[~rf.index.duplicated(keep="last")]
    if max_ffill:
        rf = rf.ffill(limit=max_ffill)
    return rf.rename("risk_free_return")
