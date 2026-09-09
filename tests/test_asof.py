import pandas as pd
import pytest

from backtester.asof import as_of_join


def _market(rows: list[dict[str, object]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def _funda(rows: list[dict[str, object]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["available_date"] = pd.to_datetime(df["available_date"])
    return df


def test_attaches_most_recent_funda_row_as_of_market_date() -> None:
    market = _market([{"security_id": 1, "date": "2020-06-15", "price": 10.0}])
    funda = _funda(
        [
            {"security_id": 1, "available_date": "2020-04-30", "bm": 1.0, "ticker": "AAA"},
            {"security_id": 1, "available_date": "2020-05-31", "bm": 2.0, "ticker": "AAA"},
        ]
    )

    result, report = as_of_join(market, funda)

    assert result["bm"].iloc[0] == 2.0
    assert result["available_date"].iloc[0] == pd.Timestamp("2020-05-31")
    assert report.n_matched_rows == 1
    assert report.n_unmatched_rows == 0


def test_never_uses_a_future_funda_row() -> None:
    market = _market([{"security_id": 1, "date": "2020-05-01", "price": 10.0}])
    funda = _funda(
        [
            {"security_id": 1, "available_date": "2020-04-30", "bm": 1.0, "ticker": "AAA"},
            {"security_id": 1, "available_date": "2020-06-30", "bm": 999.0, "ticker": "AAA"},
        ]
    )

    result, _ = as_of_join(market, funda)

    assert result["bm"].iloc[0] == 1.0


def test_market_row_before_any_funda_data_gets_null() -> None:
    market = _market([{"security_id": 1, "date": "2020-01-01", "price": 10.0}])
    funda = _funda([{"security_id": 1, "available_date": "2020-04-30", "bm": 1.0, "ticker": "AAA"}])

    result, report = as_of_join(market, funda)

    assert pd.isna(result["bm"].iloc[0])
    assert report.n_unmatched_rows == 1


def test_join_is_grouped_by_security_no_cross_contamination() -> None:
    market = _market(
        [
            {"security_id": 1, "date": "2020-06-01", "price": 10.0},
            {"security_id": 2, "date": "2020-06-01", "price": 20.0},
        ]
    )
    funda = _funda(
        [
            {"security_id": 1, "available_date": "2020-05-01", "bm": 1.0, "ticker": "AAA"},
            {"security_id": 2, "available_date": "2020-05-01", "bm": 2.0, "ticker": "BBB"},
        ]
    )

    result, _ = as_of_join(market, funda)

    sec1 = result[result["security_id"] == 1]
    sec2 = result[result["security_id"] == 2]
    assert sec1["bm"].iloc[0] == 1.0
    assert sec2["bm"].iloc[0] == 2.0


def test_max_staleness_nulls_out_stale_matches() -> None:
    market = _market([{"security_id": 1, "date": "2021-01-01", "price": 10.0}])
    funda = _funda([{"security_id": 1, "available_date": "2020-01-01", "bm": 1.0, "ticker": "AAA"}])

    result, report = as_of_join(market, funda, max_staleness=pd.Timedelta(days=93))

    assert pd.isna(result["bm"].iloc[0])
    assert report.n_unmatched_rows == 1


def test_no_max_staleness_carries_forward_indefinitely() -> None:
    market = _market([{"security_id": 1, "date": "2021-01-01", "price": 10.0}])
    funda = _funda([{"security_id": 1, "available_date": "2020-01-01", "bm": 1.0, "ticker": "AAA"}])

    result, report = as_of_join(market, funda, max_staleness=None)

    assert result["bm"].iloc[0] == 1.0
    assert report.n_matched_rows == 1


def test_funda_data_age_days_computed_correctly() -> None:
    market = _market([{"security_id": 1, "date": "2020-05-10", "price": 10.0}])
    funda = _funda([{"security_id": 1, "available_date": "2020-05-01", "bm": 1.0, "ticker": "AAA"}])

    result, _ = as_of_join(market, funda)

    assert result["funda_data_age_days"].iloc[0] == 9


def test_colliding_columns_are_suffixed() -> None:
    market = _market([{"security_id": 1, "date": "2020-05-10", "price": 10.0, "ticker": "MKT"}])
    funda = _funda([{"security_id": 1, "available_date": "2020-05-01", "bm": 1.0, "ticker": "FND"}])

    result, _ = as_of_join(market, funda)

    assert result["ticker"].iloc[0] == "MKT"
    assert result["ticker_funda"].iloc[0] == "FND"


def test_raises_on_missing_date_column() -> None:
    market = _market([{"security_id": 1, "date": "2020-05-10", "price": 10.0}])
    funda = _funda([{"security_id": 1, "available_date": "2020-05-01", "bm": 1.0}])

    with pytest.raises(ValueError, match="missing date column"):
        as_of_join(market, funda, market_date_column="not_a_column")


def test_raises_on_missing_security_id_column() -> None:
    market = pd.DataFrame({"date": pd.to_datetime(["2020-05-10"]), "price": [10.0]})
    funda = _funda([{"security_id": 1, "available_date": "2020-05-01", "bm": 1.0}])

    with pytest.raises(ValueError, match="missing 'security_id'"):
        as_of_join(market, funda)
