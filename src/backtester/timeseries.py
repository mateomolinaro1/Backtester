"""Rolling time-series statistics -- the time-series counterpart to
``stats.py``'s cross-sectional helpers.

Starts with rolling market beta (guide: "Beta Estimation", ch. 14), pulled
forward from the full Portfolio Risk Model chapter because Signal
Neutralization (ch. 10) needs beta as an input exposure now. Only what's
needed for that is built here -- no covariance matrix, no shrinkage, no
factor models. A future Portfolio Risk Model module should extend this file
(e.g. ``rolling_volatility``) rather than duplicate its rolling-window
mechanics.

Operates on whatever DataFrame/Series it's handed -- same generic philosophy
as every other module here. In particular this runs on the *full* cleaned
market panel, not the eligibility-restricted universe: a security's beta
should reflect its actual return history, and restricting to eligible dates
first would silently introduce gaps into the rolling window whenever the
security was temporarily ineligible, corrupting the covariance/variance
estimate. That's a pipeline-composition choice made by the caller, not
enforced here.

``rolling_beta`` expects ``benchmark_returns``/``risk_free_returns`` already
aligned to market's date calendar if that's wanted (``calendar.py``'s
``align_to_calendar``, ADR-0016) -- a pipeline-composition concern, not this
function's, per ADR-0009's "standalone function, composition is the caller's
job." A date missing from either series here is left null (via plain
``reindex``), not silently filled.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class RollingBetaReport:
    window: int
    min_periods: int
    n_input_rows: int
    #: Rows whose own date has no matching benchmark/risk-free return.
    n_rows_missing_benchmark_or_rf: int
    #: Rows whose rolling window had fewer than min_periods valid observations
    #: (new listing, or too many missing benchmark/rf days within the window).
    n_null_insufficient_history: int
    #: Rows whose rolling window had a (numerically) zero market-excess-return
    #: variance -- beta left null rather than a silent division by zero.
    n_degenerate_zero_variance: int
    n_beta_computed: int


def rolling_beta(
    market: pd.DataFrame,
    benchmark_returns: pd.Series,
    risk_free_returns: pd.Series,
    *,
    window: int = 252,
    min_periods: int = 126,
    security_id_column: str = "security_id",
    date_column: str = "date",
    return_column: str = "return",
) -> tuple[pd.Series, RollingBetaReport]:
    """Rolling single-factor market beta per security:

    ``beta_{i,t} = RollingCov(R_i^e, R_M^e)_t / RollingVar(R_M^e)_t``

    over the trailing ``window`` observations available for security ``i``
    (``min_periods`` required before a beta is produced at all -- fewer than
    that is treated as insufficient history, not a noisy estimate). Excess
    returns are security/benchmark return minus the risk-free return on the
    same date (guide's ``R^e = R - R_f``).

    ``benchmark_returns``/``risk_free_returns`` are reindexed onto ``market``'s
    dates as-is -- a date either has no match (left null) or it does; no
    forward-fill happens here (see module docstring: pre-align via
    ``calendar.align_to_calendar`` first if that's wanted).

    Returns a ``pd.Series`` of beta values aligned to ``market``'s index (not
    a new column in a copied frame, unlike most of this codebase's other
    transforms -- this function's output is a single derived series, not a
    treated version of an existing column; callers typically ``.assign()`` it
    onto their own frame).
    """
    for label, s in (
        ("benchmark_returns", benchmark_returns),
        ("risk_free_returns", risk_free_returns),
    ):
        if not isinstance(s.index, pd.DatetimeIndex):
            raise ValueError(f"{label} must be indexed by date (a DatetimeIndex)")
        if s.index.has_duplicates:
            raise ValueError(
                f"{label} has duplicate dates in its index; deduplicate before calling "
                "rolling_beta (e.g. read_risk_free_returns' keep-last tie-break, ADR-0012)"
            )

    n_input_rows = len(market)
    dates = market[date_column]
    rf_on_dates = risk_free_returns.reindex(dates).to_numpy()
    market_excess_on_dates = (benchmark_returns - risk_free_returns).reindex(dates).to_numpy()

    working = pd.DataFrame(
        {
            security_id_column: market[security_id_column].to_numpy(),
            date_column: dates.to_numpy(),
            "security_excess": market[return_column].to_numpy() - rf_on_dates,
            "market_excess": market_excess_on_dates,
        },
        index=market.index,
    )
    n_rows_missing_benchmark_or_rf = int(working["market_excess"].isna().sum())

    sorted_working = working.sort_values([security_id_column, date_column])

    def _rolling_cov_var(group: pd.DataFrame) -> pd.DataFrame:
        cov = group["security_excess"].rolling(window, min_periods=min_periods).cov(
            group["market_excess"]
        )
        var = group["market_excess"].rolling(window, min_periods=min_periods).var()
        return pd.DataFrame({"cov": cov, "var": var}, index=group.index)

    rolled = sorted_working.groupby(security_id_column, group_keys=False)[
        [security_id_column, "security_excess", "market_excess"]
    ].apply(_rolling_cov_var)
    rolled = rolled.reindex(working.index)

    degenerate = rolled["var"].notna() & (rolled["var"] == 0.0)
    beta = (rolled["cov"] / rolled["var"].where(~degenerate)).rename("beta")

    n_degenerate_zero_variance = int(degenerate.sum())
    n_insufficient_history = max(
        int(rolled["var"].isna().sum()) - n_rows_missing_benchmark_or_rf, 0
    )

    report = RollingBetaReport(
        window=window,
        min_periods=min_periods,
        n_input_rows=n_input_rows,
        n_rows_missing_benchmark_or_rf=n_rows_missing_benchmark_or_rf,
        n_null_insufficient_history=n_insufficient_history,
        n_degenerate_zero_variance=n_degenerate_zero_variance,
        n_beta_computed=int(beta.notna().sum()),
    )
    return beta, report