"""Cross-sectional outlier detection and treatment.

Operates generically on whatever DataFrame the caller passes in -- this module
has no knowledge of Universe Construction or Cleaning. Whether the
cross-sectional bounds get computed over the full cleaned panel or only a
universe-restricted subset is a pipeline-composition choice made by the
caller before calling `treat_outliers`, not something built in here.

Original columns are never overwritten: each treatment adds
``{column}_treated`` and ``{column}_is_outlier`` alongside the untouched
input, preserving the audit trail the guide asks for (raw vs. treated vs.
outlier flag).
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from backtester.outliers.types import OutlierTreatment, OutlierTreatmentReport, TreatmentDiagnostic


def treat_outliers(
    data: pd.DataFrame, treatments: Sequence[OutlierTreatment], *, date_column: str = "date"
) -> tuple[pd.DataFrame, OutlierTreatmentReport]:
    """Apply cross-sectional outlier treatments, one date-group at a time.

    Returns a copy of ``data`` with two new columns per treatment
    (``{column}_treated``, ``{column}_is_outlier``) plus a diagnostic report.
    Every treatment's ``column`` must already exist in ``data``. Each
    treatment computes its own bounds (``t.compute_bounds(...)``) -- this
    function doesn't know or care which concrete treatment it's holding.
    """
    if date_column not in data.columns:
        raise ValueError(
            f"date_column {date_column!r} not found in data; available columns: "
            f"{sorted(data.columns)}"
        )
    unknown_columns = [t.column for t in treatments if t.column not in data.columns]
    if unknown_columns:
        raise ValueError(
            f"outlier treatment references unknown column(s) {unknown_columns}; "
            f"available columns: {sorted(data.columns)}"
        )

    result = data.copy()
    dates = data[date_column]
    diagnostics: list[TreatmentDiagnostic] = []

    for t in treatments:
        series = data[t.column]

        lower, upper, degenerate_mask = t.compute_bounds(series, dates)
        outlier_mask = ~degenerate_mask & ((series < lower) | (series > upper))
        action_result = _apply_action(series, lower, upper, outlier_mask, t.action)
        # Degenerate-bounds dates (e.g. MAD == 0) keep their original values.
        treated_series = series.where(degenerate_mask, action_result)

        result[f"{t.column}_treated"] = treated_series
        result[f"{t.column}_is_outlier"] = outlier_mask

        diagnostics.append(
            TreatmentDiagnostic(
                column=t.column,
                method=t.method_name,
                action=t.action,
                n_input_rows=len(data),
                n_treated_lower=int((outlier_mask & (series < lower)).sum()),
                n_treated_upper=int((outlier_mask & (series > upper)).sum()),
                n_degenerate_dates=int(dates[degenerate_mask].nunique()),
            )
        )

    return result, OutlierTreatmentReport(diagnostics=tuple(diagnostics))


def _apply_action(
    series: pd.Series,
    lower: pd.Series,
    upper: pd.Series,
    outlier_mask: pd.Series,
    action: str,
) -> pd.Series:
    if action == "winsorize":
        return series.clip(lower=lower, upper=upper)
    return series.mask(outlier_mask)