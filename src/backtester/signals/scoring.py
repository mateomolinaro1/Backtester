"""Cross-sectional raw score construction (guide: "From Firm-Level
Characteristics to Raw Scores").

Operates generically on whatever DataFrame the caller passes in -- same
pattern as Universe Construction and Outlier Treatment: this module has no
knowledge of where its input column came from. In practice the input is
usually a `{column}_treated` column produced by outlier treatment, but that's
a pipeline-composition choice made by the caller, not something enforced
here.

Original columns are never overwritten: each transform adds
``{column}_raw_score`` alongside the untouched input.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from backtester.signals.types import RawScoreReport, ScoreDiagnostic, ScoreTransform


def compute_raw_scores(
    data: pd.DataFrame, transforms: Sequence[ScoreTransform], *, date_column: str = "date"
) -> tuple[pd.DataFrame, RawScoreReport]:
    """Apply cross-sectional score transforms, one date-group at a time.

    Returns a copy of ``data`` with one new column per transform
    (``{column}_raw_score``) plus a diagnostic report. Every transform's
    ``column`` must already exist in ``data``.
    """
    if date_column not in data.columns:
        raise ValueError(
            f"date_column {date_column!r} not found in data; available columns: "
            f"{sorted(data.columns)}"
        )
    unknown_columns = [t.column for t in transforms if t.column not in data.columns]
    if unknown_columns:
        raise ValueError(
            f"score transform references unknown column(s) {unknown_columns}; "
            f"available columns: {sorted(data.columns)}"
        )

    result = data.copy()
    dates = data[date_column]
    diagnostics: list[ScoreDiagnostic] = []

    for t in transforms:
        series = data[t.column]

        raw_score, degenerate = t.compute_raw_score(series, dates)

        result[f"{t.column}_raw_score"] = raw_score
        diagnostics.append(
            ScoreDiagnostic(
                column=t.column,
                method=t.method_name,
                direction=t.direction,
                n_input_rows=len(data),
                n_degenerate_dates=int(dates[degenerate].nunique()),
            )
        )

    return result, RawScoreReport(diagnostics=tuple(diagnostics))
