"""Equal-weighted combination of already-computed raw score columns into one
composite score.

V1 scope: same-source combination only (all ``columns`` must exist in the one
DataFrame passed in). Combining scores derived from different sources (e.g. a
market-derived momentum score with a funda-derived valuation score) needs an
as-of join between daily market dates and monthly funda `available_date`s
that doesn't exist yet -- deferred until that join is built.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd


def combine_scores(
    data: pd.DataFrame, columns: Sequence[str], *, output_column: str = "composite_raw_score"
) -> pd.DataFrame:
    """Equal-weighted average of ``columns``, added as ``output_column``.

    Uses pandas' row-wise mean, which skips nulls and renormalizes over
    whatever columns are non-null for that row -- matching the guide's
    "Missing Component Scores" renormalization, not a coincidence.
    """
    unknown_columns = [c for c in columns if c not in data.columns]
    if unknown_columns:
        raise ValueError(
            f"score combination references unknown column(s) {unknown_columns}; "
            f"available columns: {sorted(data.columns)}"
        )

    result = data.copy()
    result[output_column] = data[list(columns)].mean(axis=1)
    return result
