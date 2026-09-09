"""Cross-sectional signal neutralization (guide: "Signal Neutralization", ch. 10).

Operates generically on whatever DataFrame the caller passes in -- same
pattern as every other module here. Joint OLS only (guide's `s_neutral =
M_B,t s_raw`); weighted (WLS) neutralization is deferred.

Original columns are never overwritten: each signal column gets a new
``{column}_neutral`` column, the input left untouched -- same raw/treated
audit-trail convention as outlier treatment and raw scoring.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from backtester.signals.types import Exposure, NeutralizationDiagnostic, NeutralizationReport

INTERCEPT_COLUMN = "intercept"


def neutralize_signals(
    data: pd.DataFrame,
    signal_columns: Sequence[str],
    exposures: Sequence[Exposure],
    *,
    date_column: str = "date",
) -> tuple[pd.DataFrame, NeutralizationReport]:
    """Cross-sectional OLS neutralization, one date-group at a time.

    For each date, builds the exposure matrix B_t (an intercept plus every
    exposure's own column(s), per ``Exposure.build_columns``), restricts to
    rows with a complete-case exposure matrix, and regresses each signal
    column on B_t. The residual is the neutralized score
    (``s_neutral = M_B,t s_raw``); a row excluded by incomplete exposures, or
    on a date where B_t is rank-deficient (e.g. too few complete-case rows
    for the number of exposures), gets a null neutral score rather than a
    silently wrong one.

    Returns a copy of ``data`` with one new column per signal column
    (``{column}_neutral``) plus a diagnostic report.
    """
    if date_column not in data.columns:
        raise ValueError(
            f"date_column {date_column!r} not found in data; available columns: "
            f"{sorted(data.columns)}"
        )
    unknown_signal_columns = [c for c in signal_columns if c not in data.columns]
    if unknown_signal_columns:
        raise ValueError(
            f"neutralization references unknown signal column(s) {unknown_signal_columns}; "
            f"available columns: {sorted(data.columns)}"
        )
    unknown_exposure_columns = [e.column for e in exposures if e.column not in data.columns]
    if unknown_exposure_columns:
        raise ValueError(
            f"neutralization references unknown exposure column(s) {unknown_exposure_columns}; "
            f"available columns: {sorted(data.columns)}"
        )

    result = data.copy()
    for column in signal_columns:
        result[f"{column}_neutral"] = np.nan

    # Per-date accumulators, reduced into one diagnostic per signal column at the end.
    n_valid_rows: dict[str, int] = dict.fromkeys(signal_columns, 0)
    n_degenerate_dates: dict[str, int] = dict.fromkeys(signal_columns, 0)
    r_squared_by_column: dict[str, list[float]] = {column: [] for column in signal_columns}
    exposure_columns_seen: dict[str, set[str]] = {column: set() for column in signal_columns}

    for _, date_index in data.groupby(date_column).groups.items():
        block = data.loc[date_index]
        exposure_matrix = build_exposure_matrix(block, exposures)
        complete_exposures = exposure_matrix.notna().all(axis=1)

        for column in signal_columns:
            valid = complete_exposures & block[column].notna()
            n_valid = int(valid.sum())

            if n_valid <= exposure_matrix.shape[1]:
                n_degenerate_dates[column] += 1
                continue

            b_matrix = exposure_matrix.loc[valid].to_numpy(dtype=float)
            y = block.loc[valid, column].to_numpy(dtype=float)

            if np.linalg.matrix_rank(b_matrix) < b_matrix.shape[1]:
                n_degenerate_dates[column] += 1
                continue

            gamma, *_ = np.linalg.lstsq(b_matrix, y, rcond=None)
            residual = y - b_matrix @ gamma

            result.loc[block.index[valid], f"{column}_neutral"] = residual
            n_valid_rows[column] += n_valid
            exposure_columns_seen[column].update(exposure_matrix.columns)

            ss_total = float(((y - y.mean()) ** 2).sum())
            if ss_total > 0:
                ss_residual = float((residual**2).sum())
                r_squared_by_column[column].append(1.0 - ss_residual / ss_total)

    diagnostics = tuple(
        NeutralizationDiagnostic(
            column=column,
            exposure_columns=tuple(sorted(exposure_columns_seen[column])),
            n_input_rows=len(data),
            n_valid_rows=n_valid_rows[column],
            n_degenerate_dates=n_degenerate_dates[column],
            mean_r_squared=(
                float(np.mean(r_squared_by_column[column]))
                if r_squared_by_column[column]
                else None
            ),
        )
        for column in signal_columns
    )
    return result, NeutralizationReport(diagnostics=diagnostics)


def build_exposure_matrix(block: pd.DataFrame, exposures: Sequence[Exposure]) -> pd.DataFrame:
    """The exposure matrix B_t for one date-group: an intercept column plus
    every exposure's own column(s) (per ``Exposure.build_columns``).

    Public because ``portfolio/construct.py``'s Pure Alpha invariant
    diagnostics need the identical matrix ``neutralize_signals`` builds
    internally, to verify the same exposures are actually zero in the
    final portfolio weights -- not a hypothetically-shared helper, an
    actually-reused one (see ADR-0014).
    """
    columns: dict[str, pd.Series] = {INTERCEPT_COLUMN: pd.Series(1.0, index=block.index)}
    for exposure in exposures:
        columns.update(exposure.build_columns(block))
    return pd.DataFrame(columns, index=block.index)