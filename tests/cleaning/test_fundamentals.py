import pandas as pd
import pytest

from backtester.cleaning.fundamentals import clean_fundamentals

_DATES = {
    "annual_report_date": "2020-01-31",
    "quarterly_report_date": "2020-01-31",
    "available_date": "2020-03-31",
}


def _row(
    security_id: int, company_id: str, ticker: str | None, cusip: str, roa: float, **dates: str
) -> dict[str, object]:
    return {
        "security_id": security_id,
        "company_id": company_id,
        "ticker": ticker,
        "cusip": cusip,
        "roa": roa,
        **{**_DATES, **dates},
    }


def _funda_frame(rows: list[dict[str, object]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    for col in ("annual_report_date", "quarterly_report_date", "available_date"):
        df[col] = pd.to_datetime(df[col])
    return df


def test_clean_passthrough_when_valid() -> None:
    raw = _funda_frame(
        [
            _row(1, "000001", "AAA", "00000001", 0.10),
            _row(2, "000002", "BBB", "00000002", 0.20),
        ]
    )

    cleaned, report = clean_fundamentals(raw)

    pd.testing.assert_frame_equal(cleaned, raw)
    assert report.n_input_rows == 2
    assert report.n_output_rows == 2
    assert report.dropped_reasons == {
        "duplicate_ticker_only_resolved": 0,
        "duplicate_dual_company_quarantined_rows": 0,
    }
    assert report.quarantined_keys == ()


def test_raises_on_missing_required_column() -> None:
    raw = _funda_frame([_row(1, "000001", "AAA", "00000001", 0.10)]).drop(columns=["company_id"])

    with pytest.raises(ValueError, match="missing required columns"):
        clean_fundamentals(raw)


def test_resolves_identifier_only_duplicate_keeping_non_null_ticker() -> None:
    raw = _funda_frame(
        [
            _row(1, "000001", "AAA", "00000001", 0.10),
            _row(1, "000001", None, "00000001", 0.10),
        ]
    )

    cleaned, report = clean_fundamentals(raw)

    assert len(cleaned) == 1
    assert cleaned["ticker"].iloc[0] == "AAA"
    assert report.n_input_rows == 2
    assert report.n_output_rows == 1
    assert report.dropped_reasons["duplicate_ticker_only_resolved"] == 1
    assert report.dropped_reasons["duplicate_dual_company_quarantined_rows"] == 0
    assert report.quarantined_keys == ()


def test_quarantines_dual_company_conflict() -> None:
    raw = _funda_frame(
        [
            _row(1, "000001", "AAA", "00000001", 0.10),
            _row(1, "000099", "AAA", "00000001", 0.55),
            _row(2, "000002", "BBB", "00000002", 0.20),
        ]
    )

    cleaned, report = clean_fundamentals(raw)

    assert cleaned["security_id"].tolist() == [2]
    assert report.n_input_rows == 3
    assert report.n_output_rows == 1
    assert report.dropped_reasons["duplicate_ticker_only_resolved"] == 0
    assert report.dropped_reasons["duplicate_dual_company_quarantined_rows"] == 2
    assert report.quarantined_keys == ((1, pd.Timestamp(_DATES["available_date"])),)


def test_raises_on_duplicate_group_larger_than_two() -> None:
    raw = _funda_frame(
        [
            _row(1, "000001", "AAA", "00000001", 0.10),
            _row(1, "000002", "AAA", "00000001", 0.55),
            _row(1, "000003", "AAA", "00000001", 0.77),
        ]
    )

    with pytest.raises(ValueError, match="unrecognized duplicate group of size 3"):
        clean_fundamentals(raw)


def test_raises_on_unrecognized_diff_pattern() -> None:
    # Same company_id (so it's not the known dual-company-conflict shape) but a
    # substantive column differs -- no resolution rule covers this.
    raw = _funda_frame(
        [
            _row(1, "000001", "AAA", "00000001", 0.10),
            _row(1, "000001", "AAA", "00000001", 0.55),
        ]
    )

    with pytest.raises(ValueError, match="unrecognized duplicate pattern"):
        clean_fundamentals(raw)


def test_raises_when_quarterly_report_date_after_available_date() -> None:
    raw = _funda_frame(
        [_row(1, "000001", "AAA", "00000001", 0.10, quarterly_report_date="2020-06-30")]
    )

    with pytest.raises(ValueError, match="annual_report_date <= available_date"):
        clean_fundamentals(raw)


def test_raises_when_annual_report_date_after_available_date() -> None:
    raw = _funda_frame(
        [_row(1, "000001", "AAA", "00000001", 0.10, annual_report_date="2020-06-30")]
    )

    with pytest.raises(ValueError, match="annual_report_date <= available_date"):
        clean_fundamentals(raw)


def test_allows_annual_report_date_after_quarterly_report_date() -> None:
    # annual_report_date and quarterly_report_date are independent report vintages;
    # annual_report_date is not required to precede quarterly_report_date, only to
    # precede available_date. This mirrors a real pattern found in the WRDS extract.
    raw = _funda_frame(
        [
            _row(
                1,
                "000001",
                "AAA",
                "00000001",
                0.10,
                annual_report_date="2020-01-31",
                quarterly_report_date="2019-10-31",
            )
        ]
    )

    cleaned, report = clean_fundamentals(raw)

    assert len(cleaned) == 1
    assert report.n_output_rows == 1
