import pandas as pd
import pytest

from backtester.universe.build import build_universe
from backtester.universe.types import EligibilityFilter


def _market_frame(rows: list[dict[str, object]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def test_no_filters_means_entire_input_is_the_universe() -> None:
    market = _market_frame(
        [
            {"security_id": 1, "date": "2020-01-02", "price": 10.0, "exchcd": 1},
            {"security_id": 2, "date": "2020-01-02", "price": 0.50, "exchcd": 4},
        ]
    )

    universe, report = build_universe(market, filters=[])

    assert len(universe) == 2
    assert list(universe.columns) == ["security_id", "date"]
    assert report.n_input_rows == 2
    assert report.n_eligible_rows == 2
    assert report.filter_diagnostics == ()


def test_single_filter_narrows_universe() -> None:
    market = _market_frame(
        [
            {"security_id": 1, "date": "2020-01-02", "price": 10.0},
            {"security_id": 2, "date": "2020-01-02", "price": 0.50},
        ]
    )

    universe, report = build_universe(
        market, filters=[EligibilityFilter(column="price", operator=">=", value=5.0)]
    )

    assert universe["security_id"].tolist() == [1]
    assert report.n_eligible_rows == 1
    assert len(report.filter_diagnostics) == 1
    diag = report.filter_diagnostics[0]
    assert diag.n_rows_before == 2
    assert diag.n_rows_dropped == 1
    assert diag.n_rows_after == 1


def test_filters_apply_sequentially_as_a_funnel() -> None:
    market = _market_frame(
        [
            {"security_id": 1, "date": "2020-01-02", "price": 10.0, "exchcd": 1},
            {"security_id": 2, "date": "2020-01-02", "price": 0.50, "exchcd": 1},
            {"security_id": 3, "date": "2020-01-02", "price": 10.0, "exchcd": 4},
        ]
    )

    universe, report = build_universe(
        market,
        filters=[
            EligibilityFilter(column="exchcd", operator="in", value=[1, 2, 3]),
            EligibilityFilter(column="price", operator=">=", value=5.0),
        ],
    )

    assert universe["security_id"].tolist() == [1]
    exch_diag, price_diag = report.filter_diagnostics
    assert exch_diag.n_rows_before == 3
    assert exch_diag.n_rows_after == 2
    assert price_diag.n_rows_before == 2
    assert price_diag.n_rows_after == 1


def test_is_null_and_is_not_null_operators() -> None:
    market = _market_frame(
        [
            {"security_id": 1, "date": "2020-01-02", "sector": "Tech"},
            {"security_id": 2, "date": "2020-01-02", "sector": None},
        ]
    )

    universe, _ = build_universe(
        market, filters=[EligibilityFilter(column="sector", operator="is_not_null")]
    )
    assert universe["security_id"].tolist() == [1]

    universe, _ = build_universe(
        market, filters=[EligibilityFilter(column="sector", operator="is_null")]
    )
    assert universe["security_id"].tolist() == [2]


def test_raises_on_unknown_column() -> None:
    market = _market_frame([{"security_id": 1, "date": "2020-01-02", "price": 10.0}])

    with pytest.raises(ValueError, match="unknown column"):
        build_universe(
            market, filters=[EligibilityFilter(column="market_cap", operator=">=", value=1.0)]
        )


def test_raises_on_unknown_operator() -> None:
    with pytest.raises(ValueError, match="unknown eligibility filter operator"):
        EligibilityFilter(column="price", operator="~=", value=5.0)


def test_raises_when_non_nullary_operator_missing_value() -> None:
    with pytest.raises(ValueError, match="requires a 'value'"):
        EligibilityFilter(column="price", operator=">=")
