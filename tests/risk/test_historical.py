import numpy as np
import pandas as pd
import pytest

from backtester.risk.historical import historical_portfolio_volatility


def _market(sec_ids: list[int], dates: pd.DatetimeIndex, rng: np.random.Generator) -> pd.DataFrame:
    rows = [
        {"security_id": s, "date": d, "return": float(r)}
        for d in dates
        for s, r in zip(sec_ids, rng.normal(0.0, 0.01, len(sec_ids)))
    ]
    return pd.DataFrame(rows)


def _weights(sec_ids: list[int], date: pd.Timestamp, values: list[float]) -> pd.DataFrame:
    return pd.DataFrame({"security_id": sec_ids, "date": [date] * len(sec_ids), "w": values})


def test_matches_manual_xw_computation() -> None:
    rng = np.random.default_rng(0)
    dates = pd.bdate_range("2020-01-01", periods=300)
    sec_ids = [1, 2, 3, 4]
    market = _market(sec_ids, dates, rng)
    weights = _weights(sec_ids, dates[-1], [0.5, -0.5, 0.3, -0.3])

    vol, report = historical_portfolio_volatility(market, weights, "w", window=252, min_periods=126)

    wide = market.pivot_table(index="date", columns="security_id", values="return").sort_index()
    pos = wide.index.get_loc(dates[-1])
    x = wide.iloc[pos - 252 : pos][sec_ids].to_numpy()
    expected = (x @ np.array([0.5, -0.5, 0.3, -0.3])).std(ddof=1)

    assert vol.loc[dates[-1]] == pytest.approx(expected)
    assert report.n_volatility_computed == 1
    assert report.n_degenerate_insufficient_calendar_history == 0
    assert report.n_degenerate_zero_variance == 0


def test_zero_weight_security_excluded_from_missing_data_requirement() -> None:
    # security 3 has a large gap but holds zero weight -- must not affect the result at all.
    rng = np.random.default_rng(1)
    dates = pd.bdate_range("2020-01-01", periods=300)
    market = _market([1, 2], dates, rng)
    gappy = _market([3], dates[:100], rng)  # security 3 only trades for the first 100 days
    market = pd.concat([market, gappy], ignore_index=True)

    weights_with_zero = _weights([1, 2, 3], dates[-1], [0.5, -0.5, 0.0])
    weights_without = _weights([1, 2], dates[-1], [0.5, -0.5])

    vol_with, _ = historical_portfolio_volatility(market, weights_with_zero, "w", window=252, min_periods=126)
    vol_without, _ = historical_portfolio_volatility(market, weights_without, "w", window=252, min_periods=126)

    assert vol_with.loc[dates[-1]] == pytest.approx(vol_without.loc[dates[-1]])


def test_gap_in_held_security_excludes_only_that_security() -> None:
    # security 2 has a gap somewhere in the window -- must be dropped from the
    # estimate entirely (not the whole date), while security 1 (gap-free) and
    # every one of the window's trading dates are retained in full.
    rng = np.random.default_rng(2)
    dates = pd.bdate_range("2020-01-01", periods=300)
    rows = []
    for i, d in enumerate(dates):
        for s in (1, 2):
            if s == 2 and 200 <= i < 205:
                continue
            rows.append({"security_id": s, "date": d, "return": float(rng.normal(0.0, 0.01))})
    market = pd.DataFrame(rows)
    weights = _weights([1, 2], dates[-1], [0.6, -0.6])

    vol, report = historical_portfolio_volatility(market, weights, "w", window=252, min_periods=126)

    assert vol.notna().loc[dates[-1]]
    assert report.n_degenerate_insufficient_calendar_history == 0
    assert report.n_dates_with_excluded_securities == 1
    assert report.mean_security_coverage == pytest.approx(0.5)  # 1 of 2 held securities used

    wide = market.pivot_table(index="date", columns="security_id", values="return").sort_index()
    pos = wide.index.get_loc(dates[-1])
    window = wide.iloc[pos - 252 : pos]
    assert len(window) == 252  # no dates dropped, unlike a row-drop policy
    expected = (window[[1]].to_numpy() @ np.array([0.6])).std(ddof=1)
    assert vol.loc[dates[-1]] == pytest.approx(expected)


def test_insufficient_history_yields_null() -> None:
    rng = np.random.default_rng(3)
    dates = pd.bdate_range("2020-01-01", periods=200)
    market = _market([1, 2], dates, rng)
    weights = _weights([1, 2], dates[100], [0.5, -0.5])  # only 100 prior dates < min_periods=126

    vol, report = historical_portfolio_volatility(market, weights, "w", window=252, min_periods=126)

    assert pd.isna(vol.loc[dates[100]])
    assert report.n_degenerate_insufficient_calendar_history == 1
    assert report.n_volatility_computed == 0


def test_all_held_securities_gappy_yields_null() -> None:
    rng = np.random.default_rng(8)
    dates = pd.bdate_range("2020-01-01", periods=300)
    rows = []
    for i, d in enumerate(dates):
        # security 3 anchors every date in the pivot index (unheld -- 0 weight
        # below) so securities 1/2's shared gap shows up as NaN cells, not as
        # the calendar dates vanishing from the index entirely.
        rows.append({"security_id": 3, "date": d, "return": float(rng.normal(0.0, 0.01))})
        for s in (1, 2):
            if 200 <= i < 205:  # both held securities have a gap on the same days
                continue
            rows.append({"security_id": s, "date": d, "return": float(rng.normal(0.0, 0.01))})
    market = pd.DataFrame(rows)
    weights = pd.concat(
        [_weights([1, 2], dates[-1], [0.5, -0.5]), _weights([3], dates[-1], [0.0])],
        ignore_index=True,
    )

    vol, report = historical_portfolio_volatility(market, weights, "w", window=252, min_periods=126)

    assert pd.isna(vol.loc[dates[-1]])
    assert report.n_degenerate_no_eligible_securities == 1


def test_zero_variance_yields_null_not_division_by_zero() -> None:
    dates = pd.bdate_range("2020-01-01", periods=300)
    # constant returns -> zero variance
    market = pd.DataFrame(
        [{"security_id": 1, "date": d, "return": 0.001} for d in dates]
    )
    weights = _weights([1], dates[-1], [1.0])

    vol, report = historical_portfolio_volatility(market, weights, "w", window=252, min_periods=126)

    assert pd.isna(vol.loc[dates[-1]])
    assert report.n_degenerate_zero_variance == 1


def test_empty_weights_at_a_date_yields_null() -> None:
    rng = np.random.default_rng(4)
    dates = pd.bdate_range("2020-01-01", periods=300)
    market = _market([1, 2], dates, rng)
    weights = _weights([1, 2], dates[-1], [0.0, 0.0])

    vol, report = historical_portfolio_volatility(market, weights, "w", window=252, min_periods=126)

    assert pd.isna(vol.loc[dates[-1]])
    assert report.n_dates == 1
    assert report.n_volatility_computed == 0
    assert report.n_degenerate_no_holdings == 1


def test_raises_on_security_absent_from_market_entirely() -> None:
    rng = np.random.default_rng(5)
    dates = pd.bdate_range("2020-01-01", periods=300)
    market = _market([1, 2], dates, rng)
    weights = _weights([1, 999], dates[-1], [0.5, 0.5])

    with pytest.raises(ValueError, match="no return history anywhere in market"):
        historical_portfolio_volatility(market, weights, "w", window=252, min_periods=126)


def test_raises_on_missing_date_column() -> None:
    rng = np.random.default_rng(6)
    dates = pd.bdate_range("2020-01-01", periods=10)
    market = _market([1], dates, rng)
    weights = _weights([1], dates[-1], [1.0])

    with pytest.raises(ValueError, match="date_column"):
        historical_portfolio_volatility(market, weights, "w", date_column="not_a_column")


def test_multiple_dates_computed_independently() -> None:
    rng = np.random.default_rng(7)
    dates = pd.bdate_range("2020-01-01", periods=400)
    market = _market([1, 2], dates, rng)
    weights = pd.concat(
        [
            _weights([1, 2], dates[300], [0.5, -0.5]),
            _weights([1, 2], dates[350], [0.3, -0.3]),
        ],
        ignore_index=True,
    )

    vol, report = historical_portfolio_volatility(market, weights, "w", window=252, min_periods=126)

    assert report.n_dates == 2
    assert report.n_volatility_computed == 2
    assert vol.loc[dates[300]] != pytest.approx(vol.loc[dates[350]])