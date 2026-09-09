"""Splitting a single stacked/concatenated multi-dataset file into per-dataset
canonical DataFrames.

Supports the "stacked" shape produced by a SQL/Spark ``UNION ALL`` (or
equivalent): each row belongs to exactly one dataset, identified by an
explicit discriminator column the caller supplies
(e.g. ``SELECT *, 'market' AS dataset FROM ... UNION ALL SELECT *,
'fundamentals' AS dataset FROM ...``).

This is deliberately *not* inferred from which business columns happen to be
null on a row -- several canonical fields (``return``, ``ticker``) are
legitimately null on genuine rows, so a null-pattern heuristic would
misclassify them. An explicit discriminator sidesteps that entirely, and also
sidesteps raw column-name collisions between the two sources: each block's
column mapping is only ever applied to that block's own rows.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from backtester.data.io import read_fundamentals, read_market_data
from backtester.data.schema import FundamentalsColumnMapping, MarketColumnMapping


def read_combined_data(
    path: str | Path,
    *,
    dataset_column: str,
    market_columns: MarketColumnMapping,
    market_dataset_value: str,
    fundamentals_columns: FundamentalsColumnMapping,
    fundamentals_dataset_value: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read one stacked file and split it into ``(market, fundamentals)`` DataFrames.

    Every row's ``dataset_column`` value must equal exactly one of
    ``market_dataset_value`` / ``fundamentals_dataset_value``; an unrecognized
    or null value raises, since there is no rule for what such a row belongs
    to.
    """
    market = read_market_data(path, columns=market_columns)
    fundamentals = read_fundamentals(path, columns=fundamentals_columns)

    if dataset_column not in market.columns:
        raise ValueError(
            f"{path} is missing its dataset discriminator column {dataset_column!r}"
        )

    _check_dataset_column_coverage(
        market[dataset_column],
        recognized_values={market_dataset_value, fundamentals_dataset_value},
        source=str(path),
        dataset_column=dataset_column,
    )

    market_rows = market.loc[market[dataset_column] == market_dataset_value]
    fundamentals_rows = fundamentals.loc[
        fundamentals[dataset_column] == fundamentals_dataset_value
    ]
    return market_rows.reset_index(drop=True), fundamentals_rows.reset_index(drop=True)


def _check_dataset_column_coverage(
    values: pd.Series, *, recognized_values: set[str], source: str, dataset_column: str
) -> None:
    actual_values = set(values.dropna().unique())
    unrecognized = actual_values - recognized_values
    n_null = int(values.isna().sum())
    if unrecognized or n_null:
        raise ValueError(
            f"{source} has rows in {dataset_column!r} that don't match a recognized "
            f"dataset value {sorted(recognized_values)}: {sorted(unrecognized)} "
            f"unrecognized value(s), {n_null} null value(s)"
        )
