import numpy as np
import pandas as pd
import pytest

from backtester.signals.neutralize import neutralize_signals
from backtester.signals.types import CategoricalExposure, ContinuousExposure


def _frame(rows: list[dict[str, object]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def test_original_column_is_never_overwritten() -> None:
    data = _frame(
        [
            {"security_id": 1, "date": "2020-01-02", "signal": 1.0, "beta": 0.5},
            {"security_id": 2, "date": "2020-01-02", "signal": 2.0, "beta": 1.5},
            {"security_id": 3, "date": "2020-01-02", "signal": 3.0, "beta": 2.5},
        ]
    )

    result, _ = neutralize_signals(data, ["signal"], [ContinuousExposure(column="beta")])

    assert result["signal"].tolist() == [1.0, 2.0, 3.0]
    assert "signal_neutral" in result.columns


def test_residual_is_orthogonal_to_a_single_continuous_exposure() -> None:
    # signal is an exact linear function of beta plus noise -> the neutralized
    # residual must have (numerically) zero correlation with beta, and the
    # regression should explain nearly all of the cross-sectional variance.
    beta = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    noise = np.array([0.1, -0.2, 0.05, -0.05, 0.2, -0.1])
    signal = 3.0 * beta + 1.0 + noise

    data = _frame(
        [
            {"security_id": i, "date": "2020-01-02", "signal": float(s), "beta": float(b)}
            for i, (s, b) in enumerate(zip(signal, beta), start=1)
        ]
    )

    result, report = neutralize_signals(data, ["signal"], [ContinuousExposure(column="beta")])

    residual = result["signal_neutral"].to_numpy()
    correlation = np.corrcoef(residual, beta)[0, 1]
    assert correlation == pytest.approx(0.0, abs=1e-9)
    assert report.diagnostics[0].mean_r_squared == pytest.approx(1.0, abs=1e-2)
    assert report.diagnostics[0].exposure_columns == ("beta", "intercept")


def test_residual_matches_closed_form_ols_for_a_known_case() -> None:
    # Single continuous exposure, no intercept-collinearity concerns: verify the
    # residual against a hand-computed OLS fit (intercept + beta) via numpy.
    beta = np.array([1.0, 2.0, 3.0, 4.0])
    signal = np.array([2.0, 3.0, 7.0, 6.0])
    data = _frame(
        [
            {"security_id": i, "date": "2020-01-02", "signal": float(s), "beta": float(b)}
            for i, (s, b) in enumerate(zip(signal, beta), start=1)
        ]
    )

    result, _ = neutralize_signals(data, ["signal"], [ContinuousExposure(column="beta")])

    design = np.column_stack([np.ones_like(beta), beta])
    gamma, *_ = np.linalg.lstsq(design, signal, rcond=None)
    expected_residual = signal - design @ gamma

    np.testing.assert_allclose(result["signal_neutral"].to_numpy(), expected_residual)


def test_categorical_exposure_residual_equals_within_group_demeaning() -> None:
    # With only an intercept + one categorical exposure, OLS residual == each
    # row's value minus its own category's cross-sectional mean.
    data = _frame(
        [
            {"security_id": 1, "date": "2020-01-02", "signal": 1.0, "sector": "tech"},
            {"security_id": 2, "date": "2020-01-02", "signal": 3.0, "sector": "tech"},
            {"security_id": 3, "date": "2020-01-02", "signal": 10.0, "sector": "energy"},
            {"security_id": 4, "date": "2020-01-02", "signal": 20.0, "sector": "energy"},
        ]
    )

    result, _ = neutralize_signals(data, ["signal"], [CategoricalExposure(column="sector")])

    expected = data["signal"] - data.groupby("sector")["signal"].transform("mean")
    pd.testing.assert_series_equal(
        result["signal_neutral"], expected.rename("signal_neutral"), check_index=False
    )


def test_bounds_computed_independently_per_date() -> None:
    data = _frame(
        [
            {"security_id": 1, "date": "2020-01-02", "signal": 1.0, "beta": 1.0},
            {"security_id": 2, "date": "2020-01-02", "signal": 2.0, "beta": 2.0},
            {"security_id": 3, "date": "2020-01-02", "signal": 3.0, "beta": 3.0},
            {"security_id": 4, "date": "2020-01-03", "signal": 100.0, "beta": 1.0},
            {"security_id": 5, "date": "2020-01-03", "signal": 300.0, "beta": 2.0},
            {"security_id": 6, "date": "2020-01-03", "signal": 200.0, "beta": 3.0},
        ]
    )

    result, _ = neutralize_signals(data, ["signal"], [ContinuousExposure(column="beta")])

    # each date's regression is independent -- date 2's wildly different scale
    # must not leak into date 1's residuals.
    date1 = result[result["date"] == "2020-01-02"]["signal_neutral"]
    assert date1.abs().max() < 1.0  # signal is an exact linear function of beta on date 1


def test_row_with_missing_exposure_excluded_and_left_null() -> None:
    data = _frame(
        [
            {"security_id": 1, "date": "2020-01-02", "signal": 1.0, "beta": 0.5},
            {"security_id": 2, "date": "2020-01-02", "signal": 2.0, "beta": None},
            {"security_id": 3, "date": "2020-01-02", "signal": 3.0, "beta": 2.5},
            {"security_id": 4, "date": "2020-01-02", "signal": 4.0, "beta": 3.5},
        ]
    )

    result, report = neutralize_signals(data, ["signal"], [ContinuousExposure(column="beta")])

    null_row = result[result["security_id"] == 2]
    assert pd.isna(null_row["signal_neutral"].item())
    assert report.diagnostics[0].n_valid_rows == 3


def test_row_with_missing_signal_excluded_and_left_null() -> None:
    data = _frame(
        [
            {"security_id": 1, "date": "2020-01-02", "signal": 1.0, "beta": 0.5},
            {"security_id": 2, "date": "2020-01-02", "signal": None, "beta": 1.5},
            {"security_id": 3, "date": "2020-01-02", "signal": 3.0, "beta": 2.5},
            {"security_id": 4, "date": "2020-01-02", "signal": 4.0, "beta": 3.5},
        ]
    )

    result, report = neutralize_signals(data, ["signal"], [ContinuousExposure(column="beta")])

    null_row = result[result["security_id"] == 2]
    assert pd.isna(null_row["signal_neutral"].item())
    assert report.diagnostics[0].n_valid_rows == 3


def test_degenerate_date_skipped_when_too_few_rows_for_exposure_rank() -> None:
    # 2 valid rows but 3 regressors (intercept + 2 exposures) -> rank-deficient,
    # must be skipped rather than producing a spurious perfect fit.
    data = _frame(
        [
            {
                "security_id": 1,
                "date": "2020-01-02",
                "signal": 1.0,
                "beta": 0.5,
                "size": 10.0,
            },
            {
                "security_id": 2,
                "date": "2020-01-02",
                "signal": 2.0,
                "beta": 1.5,
                "size": 20.0,
            },
        ]
    )

    result, report = neutralize_signals(
        data,
        ["signal"],
        [ContinuousExposure(column="beta"), ContinuousExposure(column="size")],
    )

    assert result["signal_neutral"].isna().all()
    assert report.diagnostics[0].n_degenerate_dates == 1
    assert report.diagnostics[0].n_valid_rows == 0


def test_multiple_signal_columns_get_independent_neutral_columns() -> None:
    data = _frame(
        [
            {"security_id": 1, "date": "2020-01-02", "a": 1.0, "b": 10.0, "beta": 0.5},
            {"security_id": 2, "date": "2020-01-02", "a": 2.0, "b": 30.0, "beta": 1.5},
            {"security_id": 3, "date": "2020-01-02", "a": 3.0, "b": 20.0, "beta": 2.5},
        ]
    )

    result, report = neutralize_signals(
        data, ["a", "b"], [ContinuousExposure(column="beta")]
    )

    assert "a_neutral" in result.columns
    assert "b_neutral" in result.columns
    assert len(report.diagnostics) == 2
    assert {d.column for d in report.diagnostics} == {"a", "b"}


def test_raises_on_unknown_signal_column() -> None:
    data = _frame([{"security_id": 1, "date": "2020-01-02", "signal": 1.0, "beta": 0.5}])

    with pytest.raises(ValueError, match="unknown signal column"):
        neutralize_signals(data, ["not_a_column"], [ContinuousExposure(column="beta")])


def test_raises_on_unknown_exposure_column() -> None:
    data = _frame([{"security_id": 1, "date": "2020-01-02", "signal": 1.0, "beta": 0.5}])

    with pytest.raises(ValueError, match="unknown exposure column"):
        neutralize_signals(data, ["signal"], [ContinuousExposure(column="not_a_column")])


def test_raises_on_missing_date_column() -> None:
    data = _frame([{"security_id": 1, "date": "2020-01-02", "signal": 1.0, "beta": 0.5}])

    with pytest.raises(ValueError, match="date_column"):
        neutralize_signals(
            data,
            ["signal"],
            [ContinuousExposure(column="beta")],
            date_column="not_a_date_column",
        )
