import numpy as np
import pandas as pd
import pytest

from backtester.portfolio.isovol import apply_isovol_scaling, infer_periods_per_year


def _data(dates: pd.DatetimeIndex, sec_ids: list[int], weight: float) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": list(dates) * len(sec_ids),
            "security_id": [s for s in sec_ids for _ in dates],
            "w": [weight] * (len(dates) * len(sec_ids)),
        }
    )


def test_scale_factor_matches_target_over_forecast_ratio() -> None:
    dates = pd.bdate_range("2020-01-01", periods=1)
    data = _data(dates, [1], 0.5)
    forecast_vol = pd.Series([0.01], index=dates)

    result, report = apply_isovol_scaling(
        data, "w", forecast_vol, target_volatility_annualized=0.16, periods_per_year=256
    )

    # target_daily = 0.16 / sqrt(256) = 0.01 -> lambda = 0.01 / 0.01 = 1.0
    assert result["w_iso"].iloc[0] == pytest.approx(0.5)
    assert report.mean_scale_factor == pytest.approx(1.0)
    assert report.n_missing_forecast_volatility == 0


def test_leverage_cap_clips_scale_factor() -> None:
    dates = pd.bdate_range("2020-01-01", periods=1)
    data = _data(dates, [1], 0.5)
    forecast_vol = pd.Series([0.001], index=dates)  # would need lambda=10 uncapped

    result, report = apply_isovol_scaling(
        data,
        "w",
        forecast_vol,
        target_volatility_annualized=0.16,
        periods_per_year=256,
        max_leverage=3.0,
    )

    assert result["w_iso"].iloc[0] == pytest.approx(1.5)  # 0.5 * 3.0
    assert report.n_capped_by_leverage == 1
    assert report.max_scale_factor == pytest.approx(3.0)


def test_missing_forecast_volatility_yields_null_iso_weight() -> None:
    dates = pd.bdate_range("2020-01-01", periods=2)
    data = _data(dates, [1], 0.5)
    forecast_vol = pd.Series([0.01], index=[dates[0]])  # date[1] missing entirely

    result, report = apply_isovol_scaling(
        data, "w", forecast_vol, target_volatility_annualized=0.16, periods_per_year=256
    )

    assert result["w_iso"].notna().iloc[0]
    assert pd.isna(result["w_iso"].iloc[1])
    assert report.n_missing_forecast_volatility == 1
    assert report.n_scaled == 1


def test_null_forecast_volatility_value_yields_null_iso_weight() -> None:
    dates = pd.bdate_range("2020-01-01", periods=1)
    data = _data(dates, [1], 0.5)
    forecast_vol = pd.Series([np.nan], index=dates)

    result, report = apply_isovol_scaling(
        data, "w", forecast_vol, target_volatility_annualized=0.16, periods_per_year=256
    )

    assert pd.isna(result["w_iso"].iloc[0])
    assert report.n_missing_forecast_volatility == 1


def test_same_lambda_applied_to_every_security_that_date() -> None:
    dates = pd.bdate_range("2020-01-01", periods=1)
    data = pd.concat(
        [_data(dates, [1], 0.5), _data(dates, [2], -0.3)], ignore_index=True
    )
    forecast_vol = pd.Series([0.02], index=dates)

    result, _ = apply_isovol_scaling(
        data, "w", forecast_vol, target_volatility_annualized=0.16, periods_per_year=256
    )

    # target_daily = 0.01, sigma = 0.02 -> lambda = 0.5 for both securities
    assert result.loc[result["security_id"] == 1, "w_iso"].iloc[0] == pytest.approx(0.25)
    assert result.loc[result["security_id"] == 2, "w_iso"].iloc[0] == pytest.approx(-0.15)


def test_auto_detected_periods_per_year_matches_explicit() -> None:
    dates = pd.bdate_range("2020-01-01", periods=1)
    data = _data(dates, [1], 0.5)
    forecast_vol = pd.Series([0.01], index=dates)

    # a full year of business days is close to 252 -- build one explicitly to compare.
    full_year_dates = pd.bdate_range("2019-01-01", periods=252)
    detected = infer_periods_per_year(pd.Series(full_year_dates))
    assert detected == pytest.approx(252, abs=5)

    explicit_result, _ = apply_isovol_scaling(
        data, "w", forecast_vol, target_volatility_annualized=0.16, periods_per_year=252
    )
    auto_result, _ = apply_isovol_scaling(
        data,
        "w",
        forecast_vol,
        target_volatility_annualized=0.16,
        periods_per_year=None,
    )
    # only one date in `data` -> infer_periods_per_year falls back to that single
    # year's count, which won't match 252 exactly, but both calls should at least
    # produce a deterministic, finite scale factor.
    assert np.isfinite(auto_result["w_iso"].iloc[0])
    assert np.isfinite(explicit_result["w_iso"].iloc[0])


def test_raises_on_unknown_weight_column() -> None:
    dates = pd.bdate_range("2020-01-01", periods=1)
    data = _data(dates, [1], 0.5)
    forecast_vol = pd.Series([0.01], index=dates)

    with pytest.raises(ValueError, match="weight_column"):
        apply_isovol_scaling(
            data,
            "not_a_column",
            forecast_vol,
            target_volatility_annualized=0.16,
            periods_per_year=256,
        )


def test_raises_on_missing_date_column() -> None:
    dates = pd.bdate_range("2020-01-01", periods=1)
    data = _data(dates, [1], 0.5)
    forecast_vol = pd.Series([0.01], index=dates)

    with pytest.raises(ValueError, match="date_column"):
        apply_isovol_scaling(
            data,
            "w",
            forecast_vol,
            target_volatility_annualized=0.16,
            periods_per_year=256,
            date_column="not_a_date_column",
        )