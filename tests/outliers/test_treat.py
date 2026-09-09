import pandas as pd
import pytest

from backtester.outliers.treat import treat_outliers
from backtester.outliers.types import MadOutlierTreatment, QuantileOutlierTreatment


def _frame(rows: list[dict[str, object]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def _row(security_id: int, date: str, value: float | None) -> dict[str, object]:
    return {"security_id": security_id, "date": date, "value": value}


def test_original_column_is_never_overwritten() -> None:
    data = _frame([_row(1, "2020-01-02", 100.0), _row(2, "2020-01-02", 1.0)])

    result, _ = treat_outliers(
        data, [QuantileOutlierTreatment(column="value", lower_quantile=0.1, upper_quantile=0.9)]
    )

    assert result["value"].tolist() == [100.0, 1.0]
    assert "value_treated" in result.columns
    assert "value_is_outlier" in result.columns


def test_quantile_winsorize_caps_extremes_per_date() -> None:
    # date 1: values 1..10, winsorize [10%, 90%] should cap the extremes.
    date1_rows = [_row(i, "2020-01-02", float(i)) for i in range(1, 11)]
    data = _frame(date1_rows)

    result, report = treat_outliers(
        data, [QuantileOutlierTreatment(column="value", lower_quantile=0.1, upper_quantile=0.9)]
    )

    lower_bound = result["value_treated"].min()
    upper_bound = result["value_treated"].max()
    assert lower_bound > 1.0
    assert upper_bound < 10.0
    assert result["value_is_outlier"].sum() == 2  # the min and the max
    diag = report.diagnostics[0]
    assert diag.method == "quantile"
    assert diag.n_treated_lower == 1
    assert diag.n_treated_upper == 1


def test_quantile_truncate_nulls_extremes() -> None:
    date1_rows = [_row(i, "2020-01-02", float(i)) for i in range(1, 11)]
    data = _frame(date1_rows)

    result, _ = treat_outliers(
        data,
        [
            QuantileOutlierTreatment(
                column="value", lower_quantile=0.1, upper_quantile=0.9, action="truncate"
            )
        ],
    )

    n_null = result["value_treated"].isna().sum()
    assert n_null == 2
    # non-outlier values are untouched (not nulled, not clipped)
    middle = result.loc[~result["value_is_outlier"], "value_treated"]
    assert middle.notna().all()


def test_bounds_computed_independently_per_date() -> None:
    # date 1 has small values, date 2 has large values -- a value that would be
    # an outlier pooled across dates must not be flagged if it's typical for its
    # own date's cross-section.
    data = _frame(
        [
            _row(1, "2020-01-02", 1.0),
            _row(2, "2020-01-02", 2.0),
            _row(3, "2020-01-02", 3.0),
            _row(4, "2020-01-03", 100.0),
            _row(5, "2020-01-03", 101.0),
            _row(6, "2020-01-03", 102.0),
        ]
    )

    result, _ = treat_outliers(
        data, [QuantileOutlierTreatment(column="value", lower_quantile=0.1, upper_quantile=0.9)]
    )

    # date 2's values are nowhere near date 1's, but should still just be treated
    # as *their own* cross-section's middle/extremes, not flagged as global outliers.
    date2 = result[result["date"] == "2020-01-03"]
    assert date2["value_is_outlier"].sum() == 2  # min and max of ITS OWN date


def test_mad_winsorize_caps_extremes() -> None:
    # median 5, MAD = median(|x-5|) = 2 for [1,3,5,7,9]; bounds = 5 +/- multiplier*1.4826*2
    rows = [_row(i, "2020-01-02", float(v)) for i, v in enumerate([1, 3, 5, 7, 9, 1000], start=1)]
    data = _frame(rows)

    result, report = treat_outliers(
        data, [MadOutlierTreatment(column="value", multiplier=1.0)]
    )

    assert result.loc[result["security_id"] == 6, "value_is_outlier"].item()
    assert result.loc[result["security_id"] == 6, "value_treated"].item() < 1000.0
    diag = report.diagnostics[0]
    assert diag.method == "mad"
    assert diag.n_degenerate_dates == 0


def test_mad_skips_degenerate_dates_without_dividing_by_zero() -> None:
    # All values identical on this date -> MAD == 0. Must not silently clip
    # everything to the median; must leave the date untreated instead.
    data = _frame(
        [_row(1, "2020-01-02", 5.0), _row(2, "2020-01-02", 5.0), _row(3, "2020-01-02", 5.0)]
    )

    result, report = treat_outliers(
        data, [MadOutlierTreatment(column="value", multiplier=1.0)]
    )

    assert result["value_treated"].tolist() == [5.0, 5.0, 5.0]
    assert not result["value_is_outlier"].any()
    assert report.diagnostics[0].n_degenerate_dates == 1


def test_null_values_are_not_flagged_as_outliers() -> None:
    data = _frame(
        [_row(1, "2020-01-02", 1.0), _row(2, "2020-01-02", None), _row(3, "2020-01-02", 3.0)]
    )

    result, _ = treat_outliers(
        data, [QuantileOutlierTreatment(column="value", lower_quantile=0.01, upper_quantile=0.99)]
    )

    null_row = result[result["security_id"] == 2]
    assert not null_row["value_is_outlier"].item()
    assert pd.isna(null_row["value_treated"].item())


def test_raises_on_unknown_column() -> None:
    data = _frame([_row(1, "2020-01-02", 1.0)])

    with pytest.raises(ValueError, match="unknown column"):
        treat_outliers(
            data,
            [
                QuantileOutlierTreatment(
                    column="not_a_column", lower_quantile=0.01, upper_quantile=0.99
                )
            ],
        )


def test_raises_on_missing_date_column() -> None:
    data = _frame([_row(1, "2020-01-02", 1.0)])

    with pytest.raises(ValueError, match="date_column"):
        treat_outliers(
            data,
            [QuantileOutlierTreatment(column="value", lower_quantile=0.01, upper_quantile=0.99)],
            date_column="not_a_date_column",
        )


def test_quantile_treatment_validates_bounds() -> None:
    with pytest.raises(ValueError, match="lower_quantile"):
        QuantileOutlierTreatment(column="value", lower_quantile=0.9, upper_quantile=0.1)


def test_mad_treatment_validates_multiplier() -> None:
    with pytest.raises(ValueError, match="multiplier must be positive"):
        MadOutlierTreatment(column="value", multiplier=-1.0)


def test_treatment_validates_action() -> None:
    with pytest.raises(ValueError, match="unknown outlier treatment action"):
        QuantileOutlierTreatment(
            column="value", lower_quantile=0.01, upper_quantile=0.99, action="delete"
        )
