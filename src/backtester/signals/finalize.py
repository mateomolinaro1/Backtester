"""Post-neutralization signal standardization (guide: "Final Signal
Construction", ch. 11 -- standardization sub-section only; combination,
smoothing, turnover-awareness, and confidence weighting are deferred, see
ADR-0013).

Operates generically on whatever DataFrame the caller passes in -- same
pattern as every other module here. Mathematically identical to raw-score
standardization (``scoring.py``'s cross-sectional z-score/robust z-score per
date, same ``ScoreTransform`` types), just applied to an already-neutralized
column instead of a raw characteristic. Kept as a separate stage/function
(distinct output suffix, distinct report type) rather than reusing
``compute_raw_scores`` outright, per CLAUDE.md: "Do not collapse conceptually
distinct stages merely because V1 makes them numerically identical" -- a
neutralized-and-standardized signal is the guide's `s_final`, not another raw
score.

Original columns are never overwritten: each transform adds
``{column}_final`` alongside the untouched input.
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from backtester.signals.types import FinalSignalDiagnostic, FinalSignalReport, ScoreTransform


def standardize_final_signal(
    data: pd.DataFrame, transforms: Sequence[ScoreTransform], *, date_column: str = "date"
) -> tuple[pd.DataFrame, FinalSignalReport]:
    """Apply cross-sectional standardization transforms, one date-group at a time.

    Returns a copy of ``data`` with one new column per transform
    (``{column}_final``) plus a diagnostic report. Every transform's
    ``column`` must already exist in ``data`` -- typically a ``{...}_neutral``
    column produced by ``neutralize_signals``, but that's a pipeline-
    composition choice made by the caller, not enforced here (a signal that
    skipped neutralization can still be standardized directly).
    """
    if date_column not in data.columns:
        raise ValueError(
            f"date_column {date_column!r} not found in data; available columns: "
            f"{sorted(data.columns)}"
        )
    unknown_columns = [t.column for t in transforms if t.column not in data.columns]
    if unknown_columns:
        raise ValueError(
            f"final signal standardization references unknown column(s) {unknown_columns}; "
            f"available columns: {sorted(data.columns)}"
        )

    result = data.copy()
    dates = data[date_column]
    diagnostics: list[FinalSignalDiagnostic] = []

    for t in transforms:
        series = data[t.column]

        final_signal, degenerate = t.compute_raw_score(series, dates)

        result[f"{t.column}_final"] = final_signal
        diagnostics.append(
            FinalSignalDiagnostic(
                column=t.column,
                method=t.method_name,
                direction=t.direction,
                n_input_rows=len(data),
                n_degenerate_dates=int(dates[degenerate].nunique()),
            )
        )

    return result, FinalSignalReport(diagnostics=tuple(diagnostics))