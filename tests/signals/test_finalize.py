import pandas as pd
import pytest

from backtester.signals.finalize import standardize_final_signal
from backtester.signals.types import RobustZScoreTransform, ZScoreTransform


def _frame(rows: list[dict[str, object]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def _row(security_id: int, date: str, value: float | None) -> dict[str, object]:
    return {"security_id": security_id, "date": date, "value": value}


def test_original_column_is_never_overwritten() -> None:
    data = _frame([_row(1, "2020-01-02", 1.0), _row(2, "2020-01-02", 2.0)])

    result, _ = standardize_final_signal(data, [ZScoreTransform(column="value")])

    assert result["value"].tolist() == [1.0, 2.0]
    assert "value_final" in result.columns
    # this is a distinct stage from raw-score construction -- no _raw_score column.
    assert "value_raw_score" not in result.columns


def test_zscore_has_zero_mean_within_date() -> None:
    data = _frame([_row(i, "2020-01-02", float(i)) for i in range(1, 6)])

    result, report = standardize_final_signal(data, [ZScoreTransform(column="value")])

    assert result["value_final"].mean() == pytest.approx(0.0, abs=1e-9)
    assert report.diagnostics[0].column == "value"
    assert report.diagnostics[0].method == "zscore"
    assert report.diagnostics[0].direction == 1
    assert report.diagnostics[0].n_degenerate_dates == 0


def test_typically_standardizes_a_neutralized_column() -> None:
    # the realistic V1 pipeline shape: standardize an already-neutralized
    # residual column, not a raw characteristic.
    data = _frame(
        [_row(i, "2020-01-02", float(i)) for i in range(1, 6)]
    ).rename(columns={"value": "return_treated_raw_score_neutral"})

    result, report = standardize_final_signal(
        data, [RobustZScoreTransform(column="return_treated_raw_score_neutral")]
    )

    assert "return_treated_raw_score_neutral_final" in result.columns
    assert report.diagnostics[0].method == "robust_zscore"


def test_skips_degenerate_dates_without_dividing_by_zero() -> None:
    data = _frame(
        [_row(1, "2020-01-02", 5.0), _row(2, "2020-01-02", 5.0), _row(3, "2020-01-02", 5.0)]
    )

    result, report = standardize_final_signal(data, [ZScoreTransform(column="value")])

    assert result["value_final"].isna().all()
    assert report.diagnostics[0].n_degenerate_dates == 1


def test_null_values_stay_null() -> None:
    data = _frame(
        [_row(1, "2020-01-02", 1.0), _row(2, "2020-01-02", None), _row(3, "2020-01-02", 3.0)]
    )

    result, _ = standardize_final_signal(data, [ZScoreTransform(column="value")])

    null_row = result[result["security_id"] == 2]
    assert pd.isna(null_row["value_final"].item())


def test_raises_on_unknown_column() -> None:
    data = _frame([_row(1, "2020-01-02", 1.0)])

    with pytest.raises(ValueError, match="unknown column"):
        standardize_final_signal(data, [ZScoreTransform(column="not_a_column")])


def test_raises_on_missing_date_column() -> None:
    data = _frame([_row(1, "2020-01-02", 1.0)])

    with pytest.raises(ValueError, match="date_column"):
        standardize_final_signal(
            data, [ZScoreTransform(column="value")], date_column="not_a_date_column"
        )


def test_empty_transforms_is_a_noop_copy() -> None:
    data = _frame([_row(1, "2020-01-02", 1.0)])

    result, report = standardize_final_signal(data, [])

    assert list(result.columns) == list(data.columns)
    assert report.diagnostics == ()