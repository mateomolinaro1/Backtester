from pathlib import Path

import pandas as pd
import pytest

from backtester.data.io import (
    read_benchmark_returns,
    read_fundamentals,
    read_market_data,
    read_risk_free_returns,
)
from backtester.data.schema import FundamentalsColumnMapping, MarketColumnMapping


def test_read_market_data_renames_wrds_columns_to_canonical(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "permno": [1],
            "date": pd.to_datetime(["2020-01-02"]),
            "ret": [0.01],
            "prc": [10.0],
            "vol": [1000.0],
        }
    )
    path = tmp_path / "market.parquet"
    df.to_parquet(path)

    result = read_market_data(path)

    assert list(result.columns) == ["security_id", "date", "return", "price", "volume"]
    assert result["security_id"].tolist() == [1]
    assert result["price"].tolist() == [10.0]


def test_read_market_data_passes_through_unmapped_columns_unchanged(tmp_path: Path) -> None:
    # shares_outstanding isn't part of the canonical market schema (not required by
    # cleaning), so a source column like shrout is neither required nor renamed --
    # it just passes through under its original name.
    df = pd.DataFrame(
        {
            "permno": [1],
            "date": pd.to_datetime(["2020-01-02"]),
            "ret": [0.01],
            "prc": [10.0],
            "vol": [1000.0],
            "shrout": [100.0],
        }
    )
    path = tmp_path / "market.parquet"
    df.to_parquet(path)

    result = read_market_data(path)

    assert "shrout" in result.columns
    assert result["shrout"].tolist() == [100.0]


def test_read_market_data_missing_column_raises(tmp_path: Path) -> None:
    df = pd.DataFrame({"permno": [1], "date": pd.to_datetime(["2020-01-02"])})
    path = tmp_path / "market.parquet"
    df.to_parquet(path)

    with pytest.raises(ValueError, match="missing expected source columns"):
        read_market_data(path)


def test_read_market_data_supports_a_different_source_schema(tmp_path: Path) -> None:
    # Simulates a non-WRDS vendor with entirely different column names -- proves
    # that a new source needs only a new mapping, no changes to the reader.
    df = pd.DataFrame(
        {
            "SecurityID": [42],
            "TradeDate": pd.to_datetime(["2021-05-01"]),
            "DailyReturn": [0.02],
            "ClosePrice": [55.0],
            "Volume": [500.0],
        }
    )
    path = tmp_path / "other_vendor.parquet"
    df.to_parquet(path)

    other_vendor_columns = MarketColumnMapping(
        security_id="SecurityID",
        date="TradeDate",
        return_="DailyReturn",
        price="ClosePrice",
        volume="Volume",
    )

    result = read_market_data(path, columns=other_vendor_columns)

    assert result["security_id"].tolist() == [42]
    assert result["price"].tolist() == [55.0]
    assert result["return"].tolist() == [0.02]


def test_read_fundamentals_renames_wrds_columns_to_canonical(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "permno": [1],
            "gvkey": ["000001"],
            "adate": pd.to_datetime(["2020-01-31"]),
            "qdate": pd.to_datetime(["2020-01-31"]),
            "public_date": pd.to_datetime(["2020-03-31"]),
            "ticker": ["AAA"],
            "cusip": ["00000001"],
        }
    )
    path = tmp_path / "funda.parquet"
    df.to_parquet(path)

    result = read_fundamentals(path)

    assert set(result.columns) == {
        "security_id",
        "company_id",
        "annual_report_date",
        "quarterly_report_date",
        "available_date",
        "ticker",
        "cusip",
    }


def test_read_fundamentals_missing_column_raises(tmp_path: Path) -> None:
    df = pd.DataFrame({"permno": [1], "gvkey": ["000001"]})
    path = tmp_path / "funda.parquet"
    df.to_parquet(path)

    with pytest.raises(ValueError, match="missing expected source columns"):
        read_fundamentals(path)


def test_read_fundamentals_supports_a_different_source_schema(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "id": [7],
            "company": ["C1"],
            "fy_end": pd.to_datetime(["2021-12-31"]),
            "fq_end": pd.to_datetime(["2021-12-31"]),
            "release_date": pd.to_datetime(["2022-03-01"]),
            "symbol": ["XYZ"],
            "cusip9": ["99999999"],
        }
    )
    path = tmp_path / "other_vendor_funda.parquet"
    df.to_parquet(path)

    other_vendor_columns = FundamentalsColumnMapping(
        security_id="id",
        company_id="company",
        annual_report_date="fy_end",
        quarterly_report_date="fq_end",
        available_date="release_date",
        ticker="symbol",
        cusip="cusip9",
    )

    result = read_fundamentals(path, columns=other_vendor_columns)

    assert result["security_id"].tolist() == [7]
    assert result["ticker"].tolist() == ["XYZ"]


def test_read_benchmark_returns_computes_pct_change_and_drops_first_nan(tmp_path: Path) -> None:
    levels = pd.DataFrame(
        {"Russell 1000": [100.0, 101.0, 99.99]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
    )
    path = tmp_path / "benchmark.parquet"
    levels.to_parquet(path)

    result = read_benchmark_returns(path)

    assert result.index.name == "date"
    assert result.tolist() == pytest.approx([0.01, -0.01])
    assert result.index.tolist() == list(pd.to_datetime(["2020-01-02", "2020-01-03"]))


def test_read_benchmark_returns_supports_a_different_level_column(tmp_path: Path) -> None:
    levels = pd.DataFrame(
        {"S&P 500": [200.0, 202.0]}, index=pd.to_datetime(["2020-01-01", "2020-01-02"])
    )
    path = tmp_path / "benchmark.parquet"
    levels.to_parquet(path)

    result = read_benchmark_returns(path, level_column="S&P 500")

    assert result.tolist() == pytest.approx([0.01])


def test_read_risk_free_returns_passes_through_rates_unchanged(tmp_path: Path) -> None:
    rf = pd.DataFrame(
        {"rf_returns": [0.0001, 0.00012]}, index=pd.to_datetime(["2020-01-01", "2020-01-02"])
    )
    path = tmp_path / "rf.parquet"
    rf.to_parquet(path)

    result = read_risk_free_returns(path)

    assert result.index.name == "date"
    assert result.tolist() == pytest.approx([0.0001, 0.00012])


def test_read_benchmark_returns_forward_fills_short_gap_in_level(tmp_path: Path) -> None:
    # A single missing print (NaN level) on an otherwise-traded day: the missing
    # day is filled flat (0% return) and the following day correctly spans the
    # full move from the last known level, rather than two NaN returns.
    levels = pd.DataFrame(
        {"Russell 1000": [100.0, float("nan"), 102.0]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
    )
    path = tmp_path / "benchmark_gap.parquet"
    levels.to_parquet(path)

    result = read_benchmark_returns(path)

    assert result.index.tolist() == list(pd.to_datetime(["2020-01-02", "2020-01-03"]))
    assert result.tolist() == pytest.approx([0.0, 0.02])


def test_read_benchmark_returns_leaves_gaps_longer_than_max_ffill_unfilled(
    tmp_path: Path,
) -> None:
    # Gap of 6 consecutive missing levels exceeds the default max_ffill=5, so it
    # stays NaN past the limit and those rows fall out via the trailing dropna().
    dates = pd.date_range("2020-01-01", periods=9, freq="D")
    values = [100.0] + [float("nan")] * 6 + [110.0, 111.0]
    levels = pd.DataFrame({"Russell 1000": values}, index=dates)
    path = tmp_path / "benchmark_long_gap.parquet"
    levels.to_parquet(path)

    result = read_benchmark_returns(path)

    # Filled through the first 5 consecutive NaNs (limit=5) -> 5 flat (0%)
    # return days; the 6th NaN (index 6) is left unfilled, so both its own
    # pct_change and the following day's (index 6 -> 7) drop out; the last
    # day's return (7 -> 8, both real prints) survives untouched.
    assert result.index.tolist() == list(dates[1:6]) + [dates[8]]
    assert result.tolist() == pytest.approx([0.0, 0.0, 0.0, 0.0, 0.0, 111.0 / 110.0 - 1])


def test_read_benchmark_returns_max_ffill_none_disables_filling(tmp_path: Path) -> None:
    levels = pd.DataFrame(
        {"Russell 1000": [100.0, float("nan"), 102.0]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
    )
    path = tmp_path / "benchmark_gap_nofill.parquet"
    levels.to_parquet(path)

    result = read_benchmark_returns(path, max_ffill=None)

    # Both the gap day and the day after it drop out (unfilled NaN level
    # poisons both pct_change() terms), same as before max_ffill existed.
    assert result.empty


def test_read_risk_free_returns_forward_fills_short_gap(tmp_path: Path) -> None:
    rf = pd.DataFrame(
        {"rf_returns": [0.0001, float("nan"), 0.00015]},
        index=pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-03"]),
    )
    path = tmp_path / "rf_gap.parquet"
    rf.to_parquet(path)

    result = read_risk_free_returns(path)

    assert result.tolist() == pytest.approx([0.0001, 0.0001, 0.00015])


def test_read_risk_free_returns_leaves_gaps_longer_than_max_ffill_unfilled(
    tmp_path: Path,
) -> None:
    dates = pd.date_range("2020-01-01", periods=8, freq="D")
    values = [0.0001] + [float("nan")] * 6 + [0.0002]
    rf = pd.DataFrame({"rf_returns": values}, index=dates)
    path = tmp_path / "rf_long_gap.parquet"
    rf.to_parquet(path)

    result = read_risk_free_returns(path)

    assert result.iloc[:6].tolist() == pytest.approx([0.0001] * 6)
    assert pd.isna(result.iloc[6])
    assert result.iloc[7] == pytest.approx(0.0002)


def test_read_risk_free_returns_keeps_last_value_on_duplicate_dates(tmp_path: Path) -> None:
    # The real WRDS risk-free extract has duplicate dates with conflicting rates
    # (a known upstream data-quality issue) -- ADR-0012 documents "keep last" as
    # the deliberate tie-break, rather than raising on the downstream reindex.
    rf = pd.DataFrame(
        {"rf_returns": [0.0001, 0.00099, 0.0002]},
        index=pd.to_datetime(["2020-01-01", "2020-01-01", "2020-01-02"]),
    )
    path = tmp_path / "rf_dup.parquet"
    rf.to_parquet(path)

    result = read_risk_free_returns(path)

    assert len(result) == 2
    assert result.loc[pd.Timestamp("2020-01-01")] == pytest.approx(0.00099)
    assert result.loc[pd.Timestamp("2020-01-02")] == pytest.approx(0.0002)
