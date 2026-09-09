"""Historical ex-ante portfolio volatility via the Xw shortcut
(docs/backtesting/12.3_historical_portfolio_volatility_xw.md; ADR-0015).

For a given date's Pure Alpha weights, the historical sample-covariance
portfolio volatility ``sqrt(w'Sigma_t w)`` is algebraically identical to
``Std(X_t @ w)`` -- the sample standard deviation of the *hypothetical*
historical return series obtained by applying today's weights retroactively
to the trailing return panel. This avoids ever materializing the
N_t x N_t covariance matrix (irrelevant for isovol, which only needs the
scalar volatility) and sidesteps the missing-data-driven positive-semi-
definiteness problems a pairwise covariance matrix would raise.

Operates generically on whatever DataFrame it's handed -- same pattern as
every other module here.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class HistoricalVolatilityReport:
    window: int
    min_periods: int
    #: Distinct dates present in ``weights`` that this ran for.
    n_dates: int
    n_volatility_computed: int
    #: No security held a nonzero weight that date at all (e.g. a upstream
    #: warm-up period -- beta/pure_alpha need their own min_periods of
    #: history before any weight exists -- not a failure of this function).
    n_degenerate_no_holdings: int
    #: The date has held securities, but doesn't appear in market's own date
    #: index at all -- a structural weights/market mismatch, not expected in
    #: normal pipeline use (weights derives from market).
    n_degenerate_date_not_in_market: int
    #: Fewer than ``min_periods`` distinct trading dates exist yet anywhere
    #: in ``market`` before this date (e.g. too early in the panel).
    n_degenerate_insufficient_calendar_history: int
    #: Every currently-held security had at least one gap somewhere in the
    #: window, so none qualified for inclusion in the estimate.
    n_degenerate_no_eligible_securities: int
    #: The resulting hypothetical-return series had (numerically) zero
    #: variance -- volatility left null rather than a downstream silent
    #: division by zero in isovol's sigma*/sigma_hat.
    n_degenerate_zero_variance: int
    #: Dates where at least one held security was excluded from the estimate
    #: because its own window history had a gap -- the estimate reflects a
    #: subset of the book on these dates, not every currently-held name.
    n_dates_with_excluded_securities: int
    #: Mean fraction of held securities (by count, not weight) actually used
    #: in the estimate, across computed dates.
    mean_security_coverage: float | None


def historical_portfolio_volatility(
    market: pd.DataFrame,
    weights: pd.DataFrame,
    weight_column: str,
    *,
    window: int = 252,
    min_periods: int = 126,
    security_id_column: str = "security_id",
    date_column: str = "date",
    return_column: str = "return",
) -> tuple[pd.Series, HistoricalVolatilityReport]:
    """``sigma_hat_PA,t = Std(X_t @ w_t^PA, ddof=1)`` for every date in ``weights``.

    ``X_t`` is built from ``market``'s full return history: the ``window``
    most recent distinct trading dates strictly before ``t`` (row-count
    based, matching every other rolling-window convention in this codebase),
    restricted to the securities holding a nonzero weight at ``t``.

    A held security is included in the estimate only if it has a valid
    return on *every* one of those trading dates -- never a fabricated 0%
    return for a gap (per the guide's explicit warning). With books holding
    hundreds of names, requiring the *entire* held set to be gap-free would
    make almost every date degenerate (one name's data issue kills the whole
    estimate), so the exclusion is per-security, not per-date: a held
    security with a gap anywhere in the window is dropped from this
    estimate specifically (it still holds its normal portfolio weight
    elsewhere), while every other held security -- and every one of the
    ``window`` trading dates -- is retained. ``n_dates_with_excluded_securities``/
    ``mean_security_coverage`` in the report make this visible rather than
    silent.

    Returns a ``pd.Series`` of volatility values indexed by date (one row per
    distinct date in ``weights`` -- a portfolio-level quantity, not a
    security-level one, unlike most of this codebase's per-row transforms).
    """
    if date_column not in market.columns:
        raise ValueError(
            f"date_column {date_column!r} not found in market; available columns: "
            f"{sorted(market.columns)}"
        )
    if date_column not in weights.columns or weight_column not in weights.columns:
        raise ValueError(
            f"weights must have columns {date_column!r} and {weight_column!r}; available: "
            f"{sorted(weights.columns)}"
        )

    wide_returns = market.pivot_table(
        index=date_column, columns=security_id_column, values=return_column
    ).sort_index()
    all_dates = wide_returns.index

    results: dict[pd.Timestamp, float] = {}
    n_degenerate_no_holdings = 0
    n_degenerate_date_not_in_market = 0
    n_degenerate_insufficient_calendar_history = 0
    n_degenerate_no_eligible_securities = 0
    n_degenerate_zero_variance = 0
    n_dates_with_excluded_securities = 0
    coverage_fractions: list[float] = []

    for date, group in weights.groupby(date_column):
        held = group.set_index(security_id_column)[weight_column].dropna()
        held = held[held != 0]

        if held.empty:
            n_degenerate_no_holdings += 1
            results[date] = float("nan")
            continue
        if date not in all_dates:
            n_degenerate_date_not_in_market += 1
            results[date] = float("nan")
            continue

        unknown_held = [sid for sid in held.index if sid not in wide_returns.columns]
        if unknown_held:
            raise ValueError(
                f"weights reference security_id(s) {sorted(unknown_held)} at date {date} "
                "with no return history anywhere in market; market and weights must derive "
                "from the same panel"
            )

        pos = all_dates.get_loc(date)
        # ddof=1 sample std is undefined below 2 observations -- enforced
        # regardless of a smaller configured min_periods, rather than letting
        # np.std silently emit a 0/0 RuntimeWarning and a NaN nothing accounts for.
        if pos < max(min_periods, 2):
            n_degenerate_insufficient_calendar_history += 1
            results[date] = float("nan")
            continue

        start = max(pos - window, 0)
        window_dates = all_dates[start:pos]

        held_returns = wide_returns.loc[window_dates, held.index]
        has_full_coverage = held_returns.notna().all(axis=0)
        eligible = held.index[has_full_coverage]

        if len(eligible) == 0:
            n_degenerate_no_eligible_securities += 1
            results[date] = float("nan")
            continue
        if len(eligible) < len(held):
            n_dates_with_excluded_securities += 1
        coverage_fractions.append(len(eligible) / len(held))

        x = held_returns[eligible].to_numpy(dtype=float)
        w_vec = held.loc[eligible].to_numpy(dtype=float)
        hypothetical_returns = x @ w_vec
        sigma = float(np.std(hypothetical_returns, ddof=1))

        # sigma is computed via a matrix-vector product, not a direct column variance,
        # so genuinely-constant hypothetical returns land near but not exactly at 0.0
        # (floating-point rounding through the multiply-and-sum) -- an exact `== 0.0`
        # check (as rolling_beta uses on a direct .var()) would miss this. 1e-12 is
        # ~1e10 below any real daily-return volatility, so it only catches degeneracy.
        if sigma < 1e-12:
            n_degenerate_zero_variance += 1
            results[date] = float("nan")
            continue

        results[date] = sigma

    volatility = pd.Series(results, name="historical_volatility").sort_index()
    volatility.index.name = date_column

    report = HistoricalVolatilityReport(
        window=window,
        min_periods=min_periods,
        n_dates=len(results),
        n_volatility_computed=int(volatility.notna().sum()),
        n_degenerate_no_holdings=n_degenerate_no_holdings,
        n_degenerate_date_not_in_market=n_degenerate_date_not_in_market,
        n_degenerate_insufficient_calendar_history=n_degenerate_insufficient_calendar_history,
        n_degenerate_no_eligible_securities=n_degenerate_no_eligible_securities,
        n_degenerate_zero_variance=n_degenerate_zero_variance,
        n_dates_with_excluded_securities=n_dates_with_excluded_securities,
        mean_security_coverage=(
            float(np.mean(coverage_fractions)) if coverage_fractions else None
        ),
    )
    return volatility, report