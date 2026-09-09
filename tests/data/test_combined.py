from pathlib import Path

import pandas as pd
import pytest

from backtester.data.combined import read_combined_data
from backtester.data.schema import WRDS_FUNDAMENTALS_COLUMNS, WRDS_MARKET_COLUMNS


def _write_combined(tmp_path: Path, rows: list[dict[str, object]]) -> Path:
    df = pd.DataFrame(rows)
    for col in ("date", "adate", "qdate", "public_date"):
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
    path = tmp_path / "combined.parquet"
    df.to_parquet(path)
    return path


def test_splits_stacked_file_into_market_and_fundamentals(tmp_path: Path) -> None:
    path = _write_combined(
        tmp_path,
        [
            {
                "dataset": "market",
                "permno": 1,
                "date": "2020-01-02",
                "prc": 10.0,
                "vol": 100.0,
                "ret": 0.01,
            },
            {
                "dataset": "fundamentals",
                "permno": 1,
                "gvkey": "000001",
                "adate": "2020-01-31",
                "qdate": "2020-01-31",
                "public_date": "2020-03-31",
                "ticker": "AAA",
                "cusip": "00000001",
            },
        ],
    )

    market, fundamentals = read_combined_data(
        path,
        dataset_column="dataset",
        market_columns=WRDS_MARKET_COLUMNS,
        market_dataset_value="market",
        fundamentals_columns=WRDS_FUNDAMENTALS_COLUMNS,
        fundamentals_dataset_value="fundamentals",
    )

    assert len(market) == 1
    assert len(fundamentals) == 1
    assert market["security_id"].tolist() == [1]
    assert fundamentals["company_id"].tolist() == ["000001"]


def test_handles_legitimately_nullable_fields_without_misclassifying_rows(
    tmp_path: Path,
) -> None:
    # Regression test: a null-pattern heuristic (classify by "are all this block's
    # fields non-null") would wrongly drop these rows, since `ret` is legitimately
    # null on a security's first observation and `ticker` is legitimately null in
    # the funda dual-company case. The explicit dataset column must not care.
    path = _write_combined(
        tmp_path,
        [
            {
                "dataset": "market",
                "permno": 1,
                "date": "2020-01-02",
                "prc": 10.0,
                "vol": 100.0,
                "ret": None,
            },
            {
                "dataset": "fundamentals",
                "permno": 1,
                "gvkey": "000001",
                "adate": "2020-01-31",
                "qdate": "2020-01-31",
                "public_date": "2020-03-31",
                "ticker": None,
                "cusip": "00000001",
            },
        ],
    )

    market, fundamentals = read_combined_data(
        path,
        dataset_column="dataset",
        market_columns=WRDS_MARKET_COLUMNS,
        market_dataset_value="market",
        fundamentals_columns=WRDS_FUNDAMENTALS_COLUMNS,
        fundamentals_dataset_value="fundamentals",
    )

    assert len(market) == 1
    assert len(fundamentals) == 1
    assert market["return"].isna().all()
    assert fundamentals["ticker"].isna().all()


def test_raises_on_missing_dataset_column(tmp_path: Path) -> None:
    path = _write_combined(
        tmp_path,
        [
            {
                "permno": 1,
                "date": "2020-01-02",
                "prc": 10.0,
                "vol": 100.0,
                "ret": 0.01,
                "gvkey": "000001",
                "adate": "2020-01-31",
                "qdate": "2020-01-31",
                "public_date": "2020-03-31",
                "ticker": "AAA",
                "cusip": "00000001",
            }
        ],
    )

    with pytest.raises(ValueError, match="missing its dataset discriminator column"):
        read_combined_data(
            path,
            dataset_column="dataset",
            market_columns=WRDS_MARKET_COLUMNS,
            market_dataset_value="market",
            fundamentals_columns=WRDS_FUNDAMENTALS_COLUMNS,
            fundamentals_dataset_value="fundamentals",
        )


def test_raises_on_unrecognized_dataset_value(tmp_path: Path) -> None:
    path = _write_combined(
        tmp_path,
        [
            {
                "dataset": "estimates",
                "permno": 1,
                "date": "2020-01-02",
                "prc": 10.0,
                "vol": 100.0,
                "ret": 0.01,
                "gvkey": "000001",
                "adate": "2020-01-31",
                "qdate": "2020-01-31",
                "public_date": "2020-03-31",
                "ticker": "AAA",
                "cusip": "00000001",
            }
        ],
    )

    with pytest.raises(ValueError, match="unrecognized value"):
        read_combined_data(
            path,
            dataset_column="dataset",
            market_columns=WRDS_MARKET_COLUMNS,
            market_dataset_value="market",
            fundamentals_columns=WRDS_FUNDAMENTALS_COLUMNS,
            fundamentals_dataset_value="fundamentals",
        )


def test_raises_on_null_dataset_value(tmp_path: Path) -> None:
    path = _write_combined(
        tmp_path,
        [
            {
                "dataset": None,
                "permno": 1,
                "date": "2020-01-02",
                "prc": 10.0,
                "vol": 100.0,
                "ret": 0.01,
                "gvkey": "000001",
                "adate": "2020-01-31",
                "qdate": "2020-01-31",
                "public_date": "2020-03-31",
                "ticker": "AAA",
                "cusip": "00000001",
            }
        ],
    )

    with pytest.raises(ValueError, match="null value"):
        read_combined_data(
            path,
            dataset_column="dataset",
            market_columns=WRDS_MARKET_COLUMNS,
            market_dataset_value="market",
            fundamentals_columns=WRDS_FUNDAMENTALS_COLUMNS,
            fundamentals_dataset_value="fundamentals",
        )
