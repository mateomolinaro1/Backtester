import numpy as np
import pandas as pd
import pytest

from backtester.portfolio.construct import construct_pure_alpha_portfolio
from backtester.portfolio.types import LinearWeightMapping, TanhWeightMapping
from backtester.signals.types import ContinuousExposure


def _frame(rows: list[dict[str, object]]) -> pd.DataFrame:
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def _rows(n: int, date: str, rng: np.random.Generator) -> list[dict[str, object]]:
    signal = rng.normal(0.0, 1.0, n)
    beta = rng.normal(1.0, 0.3, n)
    return [
        {"security_id": i, "date": date, "signal": float(s), "beta": float(b)}
        for i, (s, b) in enumerate(zip(signal, beta), start=1)
    ]


def test_original_column_is_never_overwritten() -> None:
    data = _frame(_rows(8, "2020-01-02", np.random.default_rng(0)))

    result, _ = construct_pure_alpha_portfolio(
        data,
        "signal",
        TanhWeightMapping(kappa=1.0),
        [ContinuousExposure(column="beta")],
        gross_exposure=2.0,
    )

    assert result["signal"].tolist() == data["signal"].tolist()


def test_produces_all_five_checkpoint_columns() -> None:
    data = _frame(_rows(8, "2020-01-02", np.random.default_rng(0)))

    result, _ = construct_pure_alpha_portfolio(
        data,
        "signal",
        TanhWeightMapping(kappa=1.0),
        [ContinuousExposure(column="beta")],
        gross_exposure=2.0,
    )

    assert "signal_raw_mapped" in result.columns
    assert "signal_dollar_neutral" in result.columns
    assert "signal_exposure_normalized" in result.columns
    assert "signal_raw_mapped_neutral" in result.columns
    assert "signal_pure_alpha" in result.columns


def test_pure_alpha_weights_are_exactly_dollar_and_beta_neutral_with_target_gross() -> None:
    data = _frame(_rows(20, "2020-01-02", np.random.default_rng(1)))

    result, report = construct_pure_alpha_portfolio(
        data,
        "signal",
        TanhWeightMapping(kappa=1.5),
        [ContinuousExposure(column="beta")],
        gross_exposure=2.0,
    )

    weights = result["signal_pure_alpha"]
    assert weights.sum() == pytest.approx(0.0, abs=1e-9)
    assert (weights * result["beta"]).sum() == pytest.approx(0.0, abs=1e-9)
    assert weights.abs().sum() == pytest.approx(2.0, abs=1e-9)

    assert report.max_abs_net_exposure == pytest.approx(0.0, abs=1e-9)
    assert report.max_abs_projected_exposure == pytest.approx(0.0, abs=1e-9)
    assert report.max_gross_exposure_error == pytest.approx(0.0, abs=1e-9)


def test_pure_alpha_weights_neutral_with_no_exposures_configured() -> None:
    # Only the intercept is in A_t -- dollar-neutral only, no beta constraint.
    data = _frame(_rows(10, "2020-01-02", np.random.default_rng(2)))

    result, report = construct_pure_alpha_portfolio(
        data, "signal", LinearWeightMapping(), [], gross_exposure=2.0
    )

    weights = result["signal_pure_alpha"]
    assert weights.sum() == pytest.approx(0.0, abs=1e-9)
    assert weights.abs().sum() == pytest.approx(2.0, abs=1e-9)
    assert report.max_abs_projected_exposure is None
    assert report.exposure_columns == ("intercept",)


def test_dollar_neutral_checkpoint_is_simple_demeaning() -> None:
    data = _frame(_rows(8, "2020-01-02", np.random.default_rng(3)))

    result, _ = construct_pure_alpha_portfolio(
        data,
        "signal",
        LinearWeightMapping(),
        [ContinuousExposure(column="beta")],
        gross_exposure=2.0,
    )

    raw = result["signal_raw_mapped"]
    dn = result["signal_dollar_neutral"]
    assert dn.sum() == pytest.approx(0.0, abs=1e-9)
    pd.testing.assert_series_equal(dn, raw - raw.mean(), check_names=False)


def test_exposure_normalized_checkpoint_hits_symmetric_leg_targets() -> None:
    data = _frame(_rows(10, "2020-01-02", np.random.default_rng(4)))

    result, _ = construct_pure_alpha_portfolio(
        data,
        "signal",
        LinearWeightMapping(),
        [ContinuousExposure(column="beta")],
        gross_exposure=2.0,
    )

    en = result["signal_exposure_normalized"]
    long_leg = en[en > 0].sum()
    short_leg = en[en < 0].abs().sum()
    assert long_leg == pytest.approx(1.0, abs=1e-9)
    assert short_leg == pytest.approx(1.0, abs=1e-9)


def test_diagnostic_checkpoints_do_not_feed_the_authoritative_construction() -> None:
    # dollar_neutral/exposure_normalized are computed in parallel from raw_mapped,
    # not chained into beta_neutral -- confirm beta_neutral is NOT simply a beta
    # projection of exposure_normalized (it should instead exactly equal the
    # direct projection of raw_mapped).
    data = _frame(_rows(10, "2020-01-02", np.random.default_rng(5)))

    result, _ = construct_pure_alpha_portfolio(
        data,
        "signal",
        LinearWeightMapping(),
        [ContinuousExposure(column="beta")],
        gross_exposure=2.0,
    )

    raw = result["signal_raw_mapped"].to_numpy()
    beta = result["beta"].to_numpy()
    intercept = np.ones_like(beta)
    a_matrix = np.column_stack([intercept, beta])
    gamma, *_ = np.linalg.lstsq(a_matrix, raw, rcond=None)
    expected_bn = raw - a_matrix @ gamma

    np.testing.assert_allclose(result["signal_raw_mapped_neutral"].to_numpy(), expected_bn, atol=1e-9)


def test_security_with_missing_beta_is_excluded_from_pure_alpha() -> None:
    rows = _rows(10, "2020-01-02", np.random.default_rng(6))
    rows[0]["beta"] = None
    data = _frame(rows)

    result, report = construct_pure_alpha_portfolio(
        data,
        "signal",
        LinearWeightMapping(),
        [ContinuousExposure(column="beta")],
        gross_exposure=2.0,
    )

    excluded = result[result["security_id"] == 1]
    assert pd.isna(excluded["signal_raw_mapped_neutral"].item())
    assert pd.isna(excluded["signal_pure_alpha"].item())
    assert report.n_valid_rows == 9


def test_degenerate_date_with_too_few_securities_yields_null_pure_alpha() -> None:
    # 1 continuous exposure + intercept = 2 params; need > 2 valid rows.
    data = _frame(
        [
            {"security_id": 1, "date": "2020-01-02", "signal": 1.0, "beta": 0.5},
            {"security_id": 2, "date": "2020-01-02", "signal": 2.0, "beta": 1.5},
        ]
    )

    result, report = construct_pure_alpha_portfolio(
        data,
        "signal",
        LinearWeightMapping(),
        [ContinuousExposure(column="beta")],
        gross_exposure=2.0,
    )

    assert result["signal_pure_alpha"].isna().all()
    assert report.n_degenerate_dates == 1
    assert report.n_valid_rows == 0
    assert report.max_abs_net_exposure is None
    assert report.max_gross_exposure_error is None


def test_tanh_mapping_bounds_raw_mapped_weights() -> None:
    data = _frame(
        [
            {"security_id": 1, "date": "2020-01-02", "signal": 2.0, "beta": 1.0},
            {"security_id": 2, "date": "2020-01-02", "signal": -2.0, "beta": 1.0},
            {"security_id": 3, "date": "2020-01-02", "signal": 0.0, "beta": 1.0},
        ]
    )

    result, _ = construct_pure_alpha_portfolio(
        data, "signal", TanhWeightMapping(kappa=1.0), [], gross_exposure=2.0
    )

    assert result["signal_raw_mapped"].abs().max() < 1.0
    assert result["signal_raw_mapped"].tolist() == pytest.approx(
        [np.tanh(2.0), np.tanh(-2.0), 0.0]
    )


def test_raises_on_unknown_signal_column() -> None:
    data = _frame(_rows(5, "2020-01-02", np.random.default_rng(7)))

    with pytest.raises(ValueError, match="unknown signal column"):
        construct_pure_alpha_portfolio(
            data, "not_a_column", LinearWeightMapping(), [], gross_exposure=2.0
        )


def test_raises_on_missing_date_column() -> None:
    data = _frame(_rows(5, "2020-01-02", np.random.default_rng(8)))

    with pytest.raises(ValueError, match="date_column"):
        construct_pure_alpha_portfolio(
            data,
            "signal",
            LinearWeightMapping(),
            [],
            gross_exposure=2.0,
            date_column="not_a_date_column",
        )


def test_multiple_dates_are_independent() -> None:
    rng = np.random.default_rng(9)
    data = pd.concat(
        [_frame(_rows(10, "2020-01-02", rng)), _frame(_rows(10, "2020-01-03", rng))],
        ignore_index=True,
    )

    result, report = construct_pure_alpha_portfolio(
        data,
        "signal",
        TanhWeightMapping(kappa=1.0),
        [ContinuousExposure(column="beta")],
        gross_exposure=2.0,
    )

    for date, group in result.groupby("date"):
        weights = group["signal_pure_alpha"]
        assert weights.sum() == pytest.approx(0.0, abs=1e-9)
        assert weights.abs().sum() == pytest.approx(2.0, abs=1e-9)
    assert report.n_degenerate_dates == 0