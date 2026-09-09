import pandas as pd
import pytest

from backtester.cleaning.market import clean_market_data


def _row(
    security_id: int,
    date: str,
    price: float,
    volume: float,
    return_: float | None,
) -> dict[str, object]:
    return {
        "security_id": security_id,
        "date": date,
        "price": price,
        "volume": volume,
        "return": return_,
    }


def _market_frame(rows: list[dict[str, object]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def test_clean_passthrough_when_valid() -> None:
    raw = _market_frame(
        [
            _row(1, "2020-01-02", 10.0, 100.0, 0.01),
            _row(1, "2020-01-03", 10.1, 110.0, 0.01),
        ]
    )

    cleaned, report = clean_market_data(raw)

    pd.testing.assert_frame_equal(cleaned, raw)
    assert report.n_input_rows == 2
    assert report.n_output_rows == 2
    assert report.dropped_reasons == {
        "non_positive_price": 0,
        "negative_volume": 0,
    }
    assert report.quarantined_keys == ()
    assert report.notes == ()


def test_raises_on_missing_required_column() -> None:
    raw = _market_frame([_row(1, "2020-01-02", 10.0, 100.0, 0.01)]).drop(columns=["price"])

    with pytest.raises(ValueError, match="missing required columns"):
        clean_market_data(raw)


def test_raises_on_duplicate_security_id_date_key() -> None:
    raw = _market_frame(
        [
            _row(1, "2020-01-02", 10.0, 100.0, 0.01),
            _row(1, "2020-01-02", 10.5, 100.0, 0.05),
        ]
    )

    with pytest.raises(ValueError, match="duplicate \\(security_id, date\\) keys"):
        clean_market_data(raw)


def test_drops_structurally_invalid_rows() -> None:
    raw = _market_frame(
        [
            _row(1, "2020-01-02", 10.0, 100.0, 0.01),
            _row(2, "2020-01-02", 0.0, 100.0, 0.01),  # non-positive price
            _row(3, "2020-01-02", 10.0, -5.0, 0.01),  # negative volume
        ]
    )

    cleaned, report = clean_market_data(raw)

    assert cleaned["security_id"].tolist() == [1]
    assert report.n_input_rows == 3
    assert report.n_output_rows == 1
    assert report.dropped_reasons == {
        "non_positive_price": 1,
        "negative_volume": 1,
    }
    assert set(report.quarantined_keys) == {
        (2, pd.Timestamp("2020-01-02")),
        (3, pd.Timestamp("2020-01-02")),
    }


def test_null_return_notes_distinguish_first_observation_from_unexplained() -> None:
    raw = _market_frame(
        [
            # security_id 1: null return on its first observation -> expected.
            _row(1, "2020-01-02", 10.0, 100.0, None),
            _row(1, "2020-01-03", 10.1, 100.0, 0.01),
            # security_id 2: null return NOT on its first observation -> unexplained.
            _row(2, "2020-01-02", 5.0, 100.0, 0.0),
            _row(2, "2020-01-03", 5.1, 100.0, None),
        ]
    )

    _, report = clean_market_data(raw)

    assert len(report.notes) == 1
    assert "2 null return values" in report.notes[0]
    assert "1 align with a security's first observation" in report.notes[0]
    assert "1 do not and should be investigated" in report.notes[0]
