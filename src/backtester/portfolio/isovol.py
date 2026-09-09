"""Isovol volatility-targeting (generic scaling step; guide's
docs/backtesting/12.3_isovol.md / 12.3_historical_portfolio_volatility_xw.md
sec. 11; ADR-0015).

Deliberately decoupled from how the forecast volatility was estimated --
takes a precomputed per-date ``sigma_hat_p,t`` series as input, per the
guide's explicit "Generic Risk-Model Interface": "the portfolio volatility
estimator should consume a point-in-time covariance matrix [or scalar
volatility derived from one] without requiring knowledge of how that
covariance matrix was estimated." Today's only estimator is
``risk.historical_portfolio_volatility``, but this function doesn't import
or know about it -- a future single-factor or shrinkage estimator plugs in
without any change here.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class IsovolReport:
    target_volatility_annualized: float
    periods_per_year: float
    max_leverage: float | None
    n_dates: int
    #: Dates with a usable (non-null) forecast volatility, hence a scale factor.
    n_scaled: int
    n_missing_forecast_volatility: int
    n_capped_by_leverage: int
    mean_scale_factor: float | None
    min_scale_factor: float | None
    max_scale_factor: float | None


def infer_periods_per_year(dates: pd.Series) -> float:
    """Median number of distinct trading dates observed per calendar year in
    ``dates`` -- used to de-annualize a volatility target when the caller
    doesn't supply ``periods_per_year`` explicitly. Median (not mean/total)
    so that one or two partial calendar years (the panel's first/last) don't
    skew the estimate.
    """
    unique_dates = pd.Series(pd.to_datetime(dates).unique())
    counts_by_year = unique_dates.dt.year.value_counts()
    return float(counts_by_year.median())


def apply_isovol_scaling(
    data: pd.DataFrame,
    weight_column: str,
    forecast_volatility: pd.Series,
    *,
    target_volatility_annualized: float,
    periods_per_year: float | None = None,
    max_leverage: float | None = None,
    date_column: str = "date",
) -> tuple[pd.DataFrame, IsovolReport]:
    """``w^iso_t = lambda_t * w_t``, ``lambda_t = min(sigma*_daily / sigma_hat_p,t, max_leverage)``.

    ``forecast_volatility`` is a date-indexed ``pd.Series`` of ex-ante
    portfolio volatility (e.g. ``risk.historical_portfolio_volatility``'s
    output) -- a date missing from it, or null within it, leaves that date's
    ``{weight_column}_iso`` null rather than dividing by a fabricated value.
    ``periods_per_year=None`` auto-detects from ``data``'s own date column
    (:func:`infer_periods_per_year`).

    Returns a copy of ``data`` with one new column, ``{weight_column}_iso``.
    """
    if date_column not in data.columns:
        raise ValueError(
            f"date_column {date_column!r} not found in data; available columns: "
            f"{sorted(data.columns)}"
        )
    if weight_column not in data.columns:
        raise ValueError(
            f"weight_column {weight_column!r} not found in data; available columns: "
            f"{sorted(data.columns)}"
        )

    if periods_per_year is None:
        periods_per_year = infer_periods_per_year(data[date_column])
    target_volatility_daily = target_volatility_annualized / np.sqrt(periods_per_year)

    unique_dates = pd.Index(data[date_column].unique())
    sigma_by_date = forecast_volatility.reindex(unique_dates)

    lambda_vol_by_date = target_volatility_daily / sigma_by_date
    if max_leverage is not None:
        capped_mask = lambda_vol_by_date.notna() & (lambda_vol_by_date > max_leverage)
        lambda_by_date = lambda_vol_by_date.clip(upper=max_leverage)
    else:
        capped_mask = pd.Series(False, index=unique_dates)
        lambda_by_date = lambda_vol_by_date

    result = data.copy()
    lambda_on_rows = lambda_by_date.reindex(data[date_column]).to_numpy()
    result[f"{weight_column}_iso"] = result[weight_column].to_numpy() * lambda_on_rows

    valid_lambda = lambda_by_date.dropna()
    report = IsovolReport(
        target_volatility_annualized=target_volatility_annualized,
        periods_per_year=float(periods_per_year),
        max_leverage=max_leverage,
        n_dates=len(unique_dates),
        n_scaled=int(valid_lambda.shape[0]),
        n_missing_forecast_volatility=int(sigma_by_date.isna().sum()),
        n_capped_by_leverage=int(capped_mask.sum()),
        mean_scale_factor=float(valid_lambda.mean()) if not valid_lambda.empty else None,
        min_scale_factor=float(valid_lambda.min()) if not valid_lambda.empty else None,
        max_scale_factor=float(valid_lambda.max()) if not valid_lambda.empty else None,
    )
    return result, report