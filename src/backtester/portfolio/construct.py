"""Direct Pure Alpha portfolio construction (guide ch. 13;
docs/backtesting/12.2_direct_pure_alpha_construction.md's "Recommended
Closed-Form Approach"; ADR-0014).

Operates generically on whatever DataFrame the caller passes in -- same
pattern as every other module here.

The authoritative construction is a single joint Euclidean exposure
projection (``w^BN = [I - A(A'A)^-1 A'] w~``, A = [intercept, exposures...]),
computed by reusing ``neutralize_signals`` unmodified: that function's OLS
residual against an always-included intercept *is* this projection --
dollar neutrality (residual sums to zero) and beta/other exposure neutrality
(residual orthogonal to every included exposure) both fall out of the same
already-tested normal-equations solve. This is exactly the "closed form
formula" the spec recommends over two-scalar long/short leg rescaling: with
only two leg multipliers, at most two of {dollar-neutral, beta-neutral,
gross-exposure} can be hit exactly, whereas the joint projection (N degrees
of freedom) hits all three -- gross exposure via one scalar renormalization
afterward, exact because dollar/beta neutrality are homogeneous (zero-target)
constraints that scalar multiplication can't disturb.

Two additional checkpoints (``dollar_neutral``, ``exposure_normalized``) are
computed directly from ``raw_mapped`` in parallel, purely as inspectable
diagnostics -- per the spec, they must NOT feed into the authoritative
``beta_neutral``/``pure_alpha`` construction (chaining through them would
reintroduce exactly the two-step disturbance the closed-form projection
avoids).
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd

from backtester.portfolio.types import PureAlphaReport, WeightMapping
from backtester.signals import INTERCEPT_COLUMN, Exposure, build_exposure_matrix, neutralize_signals


def construct_pure_alpha_portfolio(
    data: pd.DataFrame,
    signal_column: str,
    mapping: WeightMapping,
    exposures: Sequence[Exposure],
    *,
    gross_exposure: float,
    date_column: str = "date",
) -> tuple[pd.DataFrame, PureAlphaReport]:
    """Construct a dollar-neutral, exposure-neutral Pure Alpha long-short
    portfolio directly from a final signal column, without a numerical
    optimizer.

    Returns a copy of ``data`` with five new columns (all prefixed
    ``{signal_column}_``): ``raw_mapped`` (g(s_final)), ``dollar_neutral``
    and ``exposure_normalized`` (diagnostic-only checkpoints, not chained
    into the construction), ``raw_mapped_neutral`` (the authoritative joint
    dollar+exposure-neutral projection -- the guide's "beta_neutral_weights"
    checkpoint), and ``pure_alpha`` (the final structural Pure Alpha weights,
    gross-exposure-restored, pre-isovol). Isovol scaling is out of scope
    (ADR-0014).
    """
    if date_column not in data.columns:
        raise ValueError(
            f"date_column {date_column!r} not found in data; available columns: "
            f"{sorted(data.columns)}"
        )
    if signal_column not in data.columns:
        raise ValueError(
            f"pure alpha construction references unknown signal column {signal_column!r}; "
            f"available columns: {sorted(data.columns)}"
        )

    result = data.copy()
    dates = data[date_column]

    raw_mapped_col = f"{signal_column}_raw_mapped"
    dollar_neutral_col = f"{signal_column}_dollar_neutral"
    exposure_normalized_col = f"{signal_column}_exposure_normalized"
    pure_alpha_col = f"{signal_column}_pure_alpha"

    result[raw_mapped_col] = mapping.map(data[signal_column])

    # Diagnostic checkpoint: simple demeaning. Inspection only.
    result[dollar_neutral_col] = _demean(result[raw_mapped_col], dates)

    # Diagnostic checkpoint: symmetric long/short leg gross normalization,
    # applied to the demeaned weights above. Inspection only.
    result[exposure_normalized_col] = _normalize_long_short_legs(
        result[dollar_neutral_col],
        dates,
        gross_long=gross_exposure / 2,
        gross_short=gross_exposure / 2,
    )

    # Authoritative construction: joint dollar+exposure projection, applied
    # directly to raw_mapped (NOT chained through the diagnostics above).
    result, neutralization_report = neutralize_signals(
        result, [raw_mapped_col], exposures, date_column=date_column
    )
    beta_neutral_col = f"{raw_mapped_col}_neutral"

    # Gross-exposure restoration: a single scalar per date. Exact because
    # dollar/exposure neutrality are homogeneous constraints.
    realized_gross_by_row = result.groupby(date_column)[beta_neutral_col].transform(
        lambda s: s.abs().sum()
    )
    result[pure_alpha_col] = gross_exposure * result[beta_neutral_col] / realized_gross_by_row

    diag = neutralization_report.diagnostics[0]
    max_abs_net_exposure = _max_abs_group_sum(result, pure_alpha_col, date_column)
    max_abs_projected_exposure = _max_abs_projected_exposure(
        result, pure_alpha_col, exposures, date_column
    )
    max_gross_exposure_error = _max_abs_gross_exposure_error(
        result, pure_alpha_col, date_column, gross_exposure
    )

    report = PureAlphaReport(
        signal_column=signal_column,
        mapping_method=mapping.method_name,
        exposure_columns=diag.exposure_columns,
        gross_exposure_target=gross_exposure,
        n_input_rows=diag.n_input_rows,
        n_valid_rows=diag.n_valid_rows,
        n_degenerate_dates=diag.n_degenerate_dates,
        max_abs_net_exposure=max_abs_net_exposure,
        max_abs_projected_exposure=max_abs_projected_exposure,
        max_gross_exposure_error=max_gross_exposure_error,
    )
    return result, report


def _demean(weights: pd.Series, dates: pd.Series) -> pd.Series:
    return weights - weights.groupby(dates).transform("mean")


def _normalize_long_short_legs(
    weights: pd.Series, dates: pd.Series, *, gross_long: float, gross_short: float
) -> pd.Series:
    """Symmetric long/short leg normalization (guide's "Long/Short Exposure
    Normalization"): the long leg sums to ``gross_long``, the short leg's
    absolute value sums to ``gross_short``. NaN inputs stay NaN; an exact
    zero weight maps to zero (belongs to neither leg).
    """
    is_long = weights > 0
    is_short = weights < 0
    is_zero = weights == 0

    long_sum = weights.where(is_long).groupby(dates).transform("sum")
    short_sum_abs = weights.where(is_short).abs().groupby(dates).transform("sum")

    result = pd.Series(np.nan, index=weights.index, dtype=float)
    result[is_long] = gross_long * weights[is_long] / long_sum[is_long]
    result[is_short] = gross_short * weights[is_short] / short_sum_abs[is_short]
    result[is_zero] = 0.0
    return result


def _has_any_valid_row_by_date(data: pd.DataFrame, column: str, date_column: str) -> pd.Series:
    return data.groupby(date_column)[column].apply(lambda s: s.notna().any())


def _max_abs_group_sum(data: pd.DataFrame, column: str, date_column: str) -> float | None:
    # pandas' sum() over an all-NaN group silently returns 0.0, not NaN -- a
    # degenerate date (no valid weights at all) must not be reported as "net
    # exposure achieved 0.0", so it's excluded via the same has-any-valid-row
    # filter every other invariant here uses, rather than trusted at face value.
    has_valid = _has_any_valid_row_by_date(data, column, date_column)
    by_date = data.groupby(date_column)[column].sum()[has_valid]
    return float(by_date.abs().max()) if not by_date.empty else None


def _max_abs_gross_exposure_error(
    data: pd.DataFrame, column: str, date_column: str, gross_exposure: float
) -> float | None:
    has_valid = _has_any_valid_row_by_date(data, column, date_column)
    realized_by_date = data.groupby(date_column)[column].apply(lambda s: s.abs().sum())[has_valid]
    if realized_by_date.empty:
        return None
    return float((realized_by_date - gross_exposure).abs().max())


def _max_abs_projected_exposure(
    data: pd.DataFrame, weight_column: str, exposures: Sequence[Exposure], date_column: str
) -> float | None:
    if not exposures:
        return None

    max_abs = 0.0
    any_valid = False
    for _, date_index in data.groupby(date_column).groups.items():
        block = data.loc[date_index]
        weights = block[weight_column]
        valid = weights.notna()
        if not valid.any():
            continue

        exposure_matrix = build_exposure_matrix(block.loc[valid], exposures)
        exposure_cols = [c for c in exposure_matrix.columns if c != INTERCEPT_COLUMN]
        if not exposure_cols:
            continue

        contributions = exposure_matrix[exposure_cols].to_numpy(dtype=float).T @ weights[
            valid
        ].to_numpy(dtype=float)
        any_valid = True
        max_abs = max(max_abs, float(np.abs(contributions).max()))

    return max_abs if any_valid else None