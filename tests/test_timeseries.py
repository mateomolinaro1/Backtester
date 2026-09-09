import numpy as np
import pandas as pd
import pytest

from backtester.timeseries import rolling_beta


def _dates(n: int, start: str = "2020-01-01") -> pd.DatetimeIndex:
    return pd.bdate_range(start, periods=n)


def _market_frame(security_id: int, dates: pd.DatetimeIndex, returns: list[float]) -> pd.DataFrame:
    return pd.DataFrame(
        {"security_id": security_id, "date": dates, "return": returns}
    )


def test_beta_matches_analytic_covariance_over_variance() -> None:
    # Deterministic security_excess = 2 * market_excess exactly -> beta must be
    # exactly 2.0 once enough observations have accumulated, regardless of
    # window/min_periods internals.
    n = 30
    dates = _dates(n)
    rng = np.random.default_rng(0)
    market_excess = rng.normal(0.0, 0.01, size=n)
    security_returns = 2.0 * market_excess  # rf = 0 here, so excess == raw return

    market = _market_frame(1, dates, list(security_returns))
    benchmark_returns = pd.Series(market_excess, index=dates)
    risk_free_returns = pd.Series(0.0, index=dates)

    beta, report = rolling_beta(
        market, benchmark_returns, risk_free_returns, window=n, min_periods=10
    )

    assert beta.iloc[-1] == pytest.approx(2.0)
    assert report.n_beta_computed == n - 10 + 1  # first (min_periods - 1) rows are null
    assert report.n_degenerate_zero_variance == 0
    assert report.n_rows_missing_benchmark_or_rf == 0


def test_beta_null_before_min_periods_observations() -> None:
    n = 15
    dates = _dates(n)
    market = _market_frame(1, dates, [0.01] * n)
    benchmark_returns = pd.Series(0.01, index=dates)
    risk_free_returns = pd.Series(0.0, index=dates)

    beta, report = rolling_beta(
        market, benchmark_returns, risk_free_returns, window=n, min_periods=10
    )

    assert beta.iloc[:9].isna().all()
    assert report.n_null_insufficient_history == 9


def test_beta_null_when_market_excess_variance_is_zero() -> None:
    # Benchmark return constant every day -> rolling variance of market excess
    # return is exactly 0 once the window fills -- must not divide by zero.
    n = 15
    dates = _dates(n)
    market = _market_frame(1, dates, list(np.linspace(-0.02, 0.02, n)))
    benchmark_returns = pd.Series(0.005, index=dates)  # constant
    risk_free_returns = pd.Series(0.0, index=dates)

    beta, report = rolling_beta(
        market, benchmark_returns, risk_free_returns, window=n, min_periods=5
    )

    computed = beta.iloc[4:]
    assert computed.isna().all()
    assert report.n_degenerate_zero_variance == len(computed)


def test_beta_null_once_window_ages_past_available_benchmark_history() -> None:
    # Benchmark/rf only cover the first 6 dates; a window (4) shorter than the
    # remaining 10 dates means those covered dates eventually roll out of every
    # window entirely, so beta must go -- and stay -- null once that happens
    # (not silently freeze at the last value computed while coverage lasted).
    n = 16
    dates = _dates(n)
    rng = np.random.default_rng(4)
    security_returns = rng.normal(0.0, 0.01, size=n)
    benchmark_values = rng.normal(0.0, 0.01, size=6)

    market = _market_frame(1, dates, list(security_returns))
    benchmark_returns = pd.Series(benchmark_values, index=dates[:6])
    risk_free_returns = pd.Series(0.0, index=dates[:6])

    beta, report = rolling_beta(
        market, benchmark_returns, risk_free_returns, window=4, min_periods=3
    )

    assert beta.iloc[:2].isna().all()  # below min_periods
    assert beta.iloc[2:7].notna().all()  # window still overlaps covered dates
    assert beta.iloc[7:].isna().all()  # window has fully aged past covered dates
    assert report.n_rows_missing_benchmark_or_rf == n - 6
    assert report.n_beta_computed == 5


def test_beta_computed_independently_per_security() -> None:
    n = 20
    dates = _dates(n)
    rng = np.random.default_rng(1)
    market_excess = rng.normal(0.0, 0.01, size=n)
    risk_free_returns = pd.Series(0.0, index=dates)
    benchmark_returns = pd.Series(market_excess, index=dates)

    security_1 = _market_frame(1, dates, list(1.0 * market_excess))
    security_2 = _market_frame(2, dates, list(-0.5 * market_excess))
    market = pd.concat([security_1, security_2], ignore_index=True)

    beta, _ = rolling_beta(market, benchmark_returns, risk_free_returns, window=n, min_periods=10)
    result = market.assign(beta=beta)

    assert result.loc[result["security_id"] == 1, "beta"].iloc[-1] == pytest.approx(1.0)
    assert result.loc[result["security_id"] == 2, "beta"].iloc[-1] == pytest.approx(-0.5)


def test_excess_return_subtracts_risk_free_rate() -> None:
    # security return == benchmark return every day, but a nonzero, varying rf
    # must cancel out of both excess-return series identically -> beta == 1.
    n = 20
    dates = _dates(n)
    rng = np.random.default_rng(2)
    raw_returns = rng.normal(0.0, 0.01, size=n)
    rf = rng.normal(0.0002, 0.00005, size=n)

    market = _market_frame(1, dates, list(raw_returns))
    benchmark_returns = pd.Series(raw_returns, index=dates)
    risk_free_returns = pd.Series(rf, index=dates)

    beta, _ = rolling_beta(market, benchmark_returns, risk_free_returns, window=n, min_periods=10)

    assert beta.iloc[-1] == pytest.approx(1.0)


def test_raises_when_benchmark_returns_not_datetime_indexed() -> None:
    dates = _dates(5)
    market = _market_frame(1, dates, [0.01] * 5)
    benchmark_returns = pd.Series([0.01] * 5)  # RangeIndex, not DatetimeIndex
    risk_free_returns = pd.Series(0.0, index=dates)

    with pytest.raises(ValueError, match="benchmark_returns must be indexed by date"):
        rolling_beta(market, benchmark_returns, risk_free_returns)


def test_raises_when_risk_free_returns_has_duplicate_dates() -> None:
    # benchmark_returns - risk_free_returns aligns by date label, not position, so
    # a duplicate date doesn't silently mispair -- but it does leave a duplicate
    # label in the result, which the following .reindex(dates) can't handle
    # (pandas: "cannot reindex on an axis with duplicate labels"). Caught explicitly
    # here rather than surfacing that raw pandas error to the caller.
    dates = _dates(5)
    market = _market_frame(1, dates, [0.01] * 5)
    benchmark_returns = pd.Series(0.01, index=dates)
    risk_free_returns = pd.Series(
        0.0, index=dates.insert(0, dates[0])
    )  # dates[0] now appears twice

    with pytest.raises(ValueError, match="risk_free_returns has duplicate dates"):
        rolling_beta(market, benchmark_returns, risk_free_returns)


def test_raises_when_benchmark_returns_has_duplicate_dates() -> None:
    dates = _dates(5)
    market = _market_frame(1, dates, [0.01] * 5)
    benchmark_returns = pd.Series(0.01, index=dates.insert(0, dates[0]))
    risk_free_returns = pd.Series(0.0, index=dates)

    with pytest.raises(ValueError, match="benchmark_returns has duplicate dates"):
        rolling_beta(market, benchmark_returns, risk_free_returns)
