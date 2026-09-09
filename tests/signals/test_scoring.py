import pandas as pd
import pytest

from backtester.signals.scoring import compute_raw_scores
from backtester.signals.types import RobustZScoreTransform, ZScoreTransform


def _frame(rows: list[dict[str, object]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def _row(security_id: int, date: str, value: float | None) -> dict[str, object]:
    return {"security_id": security_id, "date": date, "value": value}


def test_original_column_is_never_overwritten() -> None:
    data = _frame([_row(1, "2020-01-02", 1.0), _row(2, "2020-01-02", 2.0)])

    result, _ = compute_raw_scores(data, [ZScoreTransform(column="value")])

    assert result["value"].tolist() == [1.0, 2.0]
    assert "value_raw_score" in result.columns


def test_zscore_has_zero_mean_within_date() -> None:
    data = _frame([_row(i, "2020-01-02", float(i)) for i in range(1, 6)])

    result, report = compute_raw_scores(data, [ZScoreTransform(column="value")])

    assert result["value_raw_score"].mean() == pytest.approx(0.0, abs=1e-9)
    assert report.diagnostics[0].method == "zscore"
    assert report.diagnostics[0].n_degenerate_dates == 0


def test_direction_flips_sign() -> None:
    data = _frame([_row(i, "2020-01-02", float(i)) for i in range(1, 6)])

    positive, _ = compute_raw_scores(data, [ZScoreTransform(column="value", direction=1)])
    negative, _ = compute_raw_scores(data, [ZScoreTransform(column="value", direction=-1)])

    pd.testing.assert_series_equal(
        positive["value_raw_score"], -negative["value_raw_score"], check_names=False
    )


def test_bounds_computed_independently_per_date() -> None:
    data = _frame(
        [
            _row(1, "2020-01-02", 1.0),
            _row(2, "2020-01-02", 2.0),
            _row(3, "2020-01-02", 3.0),
            _row(4, "2020-01-03", 100.0),
            _row(5, "2020-01-03", 200.0),
            _row(6, "2020-01-03", 300.0),
        ]
    )

    result, _ = compute_raw_scores(data, [ZScoreTransform(column="value")])

    date1_scores = result[result["date"] == "2020-01-02"]["value_raw_score"]
    date2_scores = result[result["date"] == "2020-01-03"]["value_raw_score"]
    # each date's cross-section is standardized independently, so the shape of
    # scores should match even though the raw magnitudes differ hugely.
    pd.testing.assert_series_equal(date1_scores, date2_scores, check_names=False, check_index=False)


def test_zscore_skips_degenerate_dates_without_dividing_by_zero() -> None:
    data = _frame(
        [_row(1, "2020-01-02", 5.0), _row(2, "2020-01-02", 5.0), _row(3, "2020-01-02", 5.0)]
    )

    result, report = compute_raw_scores(data, [ZScoreTransform(column="value")])

    assert result["value_raw_score"].isna().all()
    assert report.diagnostics[0].n_degenerate_dates == 1


def test_robust_zscore_skips_degenerate_dates() -> None:
    data = _frame(
        [_row(1, "2020-01-02", 5.0), _row(2, "2020-01-02", 5.0), _row(3, "2020-01-02", 5.0)]
    )

    result, report = compute_raw_scores(data, [RobustZScoreTransform(column="value")])

    assert result["value_raw_score"].isna().all()
    assert report.diagnostics[0].method == "robust_zscore"
    assert report.diagnostics[0].n_degenerate_dates == 1


def test_robust_zscore_is_less_sensitive_to_a_single_extreme_value() -> None:
    rows = [_row(i, "2020-01-02", float(v)) for i, v in enumerate([1, 2, 3, 4, 1000], start=1)]
    data = _frame(rows)

    zscore_result, _ = compute_raw_scores(data, [ZScoreTransform(column="value")])
    robust_result, _ = compute_raw_scores(data, [RobustZScoreTransform(column="value")])

    # the extreme value should dominate the ordinary z-score's scale far more than
    # the robust (median/MAD) one.
    zscore_range = zscore_result["value_raw_score"].iloc[:4].abs().max()
    robust_range = robust_result["value_raw_score"].iloc[:4].abs().max()
    assert robust_range > zscore_range


def test_null_values_stay_null() -> None:
    data = _frame(
        [_row(1, "2020-01-02", 1.0), _row(2, "2020-01-02", None), _row(3, "2020-01-02", 3.0)]
    )

    result, _ = compute_raw_scores(data, [ZScoreTransform(column="value")])

    null_row = result[result["security_id"] == 2]
    assert pd.isna(null_row["value_raw_score"].item())


def test_raises_on_unknown_column() -> None:
    data = _frame([_row(1, "2020-01-02", 1.0)])

    with pytest.raises(ValueError, match="unknown column"):
        compute_raw_scores(data, [ZScoreTransform(column="not_a_column")])


def test_raises_on_missing_date_column() -> None:
    data = _frame([_row(1, "2020-01-02", 1.0)])

    with pytest.raises(ValueError, match="date_column"):
        compute_raw_scores(data, [ZScoreTransform(column="value")], date_column="not_a_date_column")


def test_raises_on_invalid_direction() -> None:
    with pytest.raises(ValueError, match="direction must be 1 or -1"):
        ZScoreTransform(column="value", direction=2)
