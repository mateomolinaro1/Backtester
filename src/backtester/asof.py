"""Point-in-time as-of join between daily market data and fundamentals data.

Implements the guide's backward as-of join:
``X_{i,t}^PIT = X_{i,tau*(t)}``, ``tau*(t) = max{tau : t_avail <= t}`` -- for
every ``(security_id, date)`` row in market data, attach the most recent
fundamentals row for that security whose ``available_date <= date``. Never
forward: a fundamentals row with ``available_date > date`` is never visible
to that market row, regardless of how close.

Implemented via ``pandas.merge_asof(direction="backward")``, grouped by
security. This relies on Cleaning already having enforced
``(security_id, date)`` and ``(security_id, available_date)`` uniqueness on
each side -- merge_asof assumes at most one match per key.

Generic like the rest of this pipeline: operates on whatever two DataFrames
are passed in (typically cleaned market and cleaned fundamentals, but that's
a pipeline-composition choice made by the caller, not enforced here).
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

#: Default maximum staleness: ~1 reporting quarter. Our funda source refreshes
#: monthly per security (~31-day normal cadence between available_date rows),
#: so this gives headroom over normal operation while still catching genuine
#: reporting gaps (delisting, distress, data pipeline issues) -- a security
#: with no funda update in over a quarter is treated as having none, rather
#: than silently carrying forward increasingly stale figures.
DEFAULT_MAX_STALENESS = pd.Timedelta(days=93)


@dataclass(frozen=True)
class AsOfJoinReport:
    n_market_rows: int
    n_matched_rows: int
    n_unmatched_rows: int
    max_staleness: pd.Timedelta | None


def as_of_join(
    market: pd.DataFrame,
    fundamentals: pd.DataFrame,
    *,
    market_date_column: str = "date",
    fundamentals_date_column: str = "available_date",
    security_id_column: str = "security_id",
    max_staleness: pd.Timedelta | None = DEFAULT_MAX_STALENESS,
) -> tuple[pd.DataFrame, AsOfJoinReport]:
    """Attach each market row's most recent as-of-available fundamentals row.

    The output is sorted by ``market_date_column`` (a `merge_asof` requirement),
    not necessarily in the input's original row order. Adds
    ``funda_data_age_days`` (days between the market date and the matched
    fundamentals' ``available_date``, per the guide's data-age diagnostic).
    A market row with no eligible fundamentals row (none exists yet, or the
    nearest one is older than ``max_staleness``) gets nulls in every
    fundamentals column rather than being dropped.

    Columns present in both inputs (e.g. ``ticker``, ``cusip`` pass-through
    columns) keep market's version unsuffixed and fundamentals' version
    suffixed ``_funda``.
    """
    for label, df, column in (
        ("market", market, market_date_column),
        ("fundamentals", fundamentals, fundamentals_date_column),
    ):
        if column not in df.columns:
            raise ValueError(
                f"{label} is missing date column {column!r}; available columns: "
                f"{sorted(df.columns)}"
            )
        if security_id_column not in df.columns:
            raise ValueError(
                f"{label} is missing {security_id_column!r}; available columns: "
                f"{sorted(df.columns)}"
            )

    market_sorted = market.sort_values(market_date_column)
    fundamentals_sorted = fundamentals.sort_values(fundamentals_date_column)

    result = pd.merge_asof(
        market_sorted,
        fundamentals_sorted,
        left_on=market_date_column,
        right_on=fundamentals_date_column,
        by=security_id_column,
        direction="backward",
        tolerance=max_staleness,
        suffixes=("", "_funda"),
    ).reset_index(drop=True)

    result["funda_data_age_days"] = (
        result[market_date_column] - result[fundamentals_date_column]
    ).dt.days

    n_matched = int(result[fundamentals_date_column].notna().sum())
    report = AsOfJoinReport(
        n_market_rows=len(market),
        n_matched_rows=n_matched,
        n_unmatched_rows=len(market) - n_matched,
        max_staleness=max_staleness,
    )
    return result, report
