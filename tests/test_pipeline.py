import json
from pathlib import Path

import pandas as pd
import pytest

from backtester.pipeline import BacktestPipeline, PipelineStateError

# security_id 3 is ineligible (exchcd == 2); 1 and 2 are eligible (exchcd == 1). Two
# eligible securities per date keeps cross-sectional z-scores/quantiles non-degenerate.
_MARKET_ROWS = [
    {"permno": 1, "date": "2020-01-02", "prc": 10.0, "vol": 100, "ret": 0.01, "exchcd": 1},
    {"permno": 2, "date": "2020-01-02", "prc": 20.0, "vol": 200, "ret": 0.02, "exchcd": 1},
    {"permno": 3, "date": "2020-01-02", "prc": 30.0, "vol": 300, "ret": 0.03, "exchcd": 2},
    {"permno": 1, "date": "2020-01-03", "prc": 10.1, "vol": 110, "ret": -0.01, "exchcd": 1},
    {"permno": 2, "date": "2020-01-03", "prc": 20.4, "vol": 210, "ret": 0.02, "exchcd": 1},
    {"permno": 3, "date": "2020-01-03", "prc": 30.9, "vol": 310, "ret": 0.03, "exchcd": 2},
]

# All three securities have fundamentals -- security 3's is expected to never reach the
# joined frame (ADR-0011): the as-of join is driven from market_universe, which already
# excludes it, so its bm=2.5 never contaminates the other two's cross-sectional bm stats.
_FUNDA_ROWS = [
    {
        "permno": 1,
        "gvkey": "001",
        "adate": "2019-12-31",
        "qdate": "2019-12-31",
        "public_date": "2019-12-31",
        "ticker": "AAA",
        "cusip": "111111111",
        "bm": 0.5,
    },
    {
        "permno": 2,
        "gvkey": "002",
        "adate": "2019-12-31",
        "qdate": "2019-12-31",
        "public_date": "2019-12-31",
        "ticker": "BBB",
        "cusip": "222222222",
        "bm": 1.5,
    },
    {
        "permno": 3,
        "gvkey": "003",
        "adate": "2019-12-31",
        "qdate": "2019-12-31",
        "public_date": "2019-12-31",
        "ticker": "CCC",
        "cusip": "333333333",
        "bm": 2.5,
    },
]


def _write_parquet(rows: list[dict[str, object]], date_cols: list[str], path: Path) -> None:
    df = pd.DataFrame(rows)
    for col in date_cols:
        df[col] = pd.to_datetime(df[col])
    df.to_parquet(path)


def _write_pipeline_config(tmp_path: Path, market_path: Path, funda_path: Path) -> Path:
    config = {
        "data_sources": {
            "market": {"path": str(market_path), "preset": "wrds"},
            "fundamentals": {"path": str(funda_path), "preset": "wrds"},
        },
        "universe": {"filters": [{"column": "exchcd", "operator": "==", "value": 1}]},
        "outlier_treatment": {
            "treatments": [
                {
                    "column": "return",
                    "method": "quantile",
                    "lower_quantile": 0.0,
                    "upper_quantile": 1.0,
                    "action": "winsorize",
                },
                {
                    "column": "bm",
                    "method": "quantile",
                    "lower_quantile": 0.0,
                    "upper_quantile": 1.0,
                    "action": "winsorize",
                },
            ]
        },
        "signal_construction": {
            "scores": [
                {"column": "return_treated", "method": "zscore", "direction": 1},
                {"column": "bm_treated", "method": "zscore", "direction": 1},
            ]
        },
    }
    config_path = tmp_path / "backtest.json"
    config_path.write_text(json.dumps(config))
    return config_path


@pytest.fixture
def pipeline(tmp_path: Path) -> BacktestPipeline:
    market_path = tmp_path / "market.parquet"
    funda_path = tmp_path / "funda.parquet"
    _write_parquet(_MARKET_ROWS, ["date"], market_path)
    _write_parquet(_FUNDA_ROWS, ["adate", "qdate", "public_date"], funda_path)
    config_path = _write_pipeline_config(tmp_path, market_path, funda_path)
    return BacktestPipeline.from_config(config_path)


def test_stages_raise_if_prerequisite_not_run(pipeline: BacktestPipeline) -> None:
    with pytest.raises(PipelineStateError):
        pipeline.clean()
    with pytest.raises(PipelineStateError):
        pipeline.align_benchmark_and_risk_free()
    with pytest.raises(PipelineStateError):
        pipeline.compute_beta()
    with pytest.raises(PipelineStateError):
        pipeline.build_universe()
    with pytest.raises(PipelineStateError):
        pipeline.join_market_fundamentals()
    with pytest.raises(PipelineStateError):
        pipeline.treat_outliers()
    with pytest.raises(PipelineStateError):
        pipeline.construct_signals()
    with pytest.raises(PipelineStateError):
        pipeline.neutralize()
    with pytest.raises(PipelineStateError):
        pipeline.finalize()
    with pytest.raises(PipelineStateError):
        pipeline.construct_pure_alpha()
    with pytest.raises(PipelineStateError):
        pipeline.estimate_portfolio_volatility()
    with pytest.raises(PipelineStateError):
        pipeline.apply_isovol()


def test_run_populates_every_stage(pipeline: BacktestPipeline) -> None:
    result = pipeline.run()

    assert result is pipeline
    assert pipeline.market_raw is not None and len(pipeline.market_raw) == 6
    assert pipeline.fundamentals_raw is not None and len(pipeline.fundamentals_raw) == 3
    assert pipeline.market_clean is not None
    assert pipeline.market_clean_report is not None
    assert pipeline.fundamentals_clean is not None
    assert pipeline.fundamentals_clean_report is not None
    assert pipeline.universe is not None
    assert pipeline.universe_report is not None
    assert pipeline.market_universe is not None
    assert pipeline.market_fundamentals_joined is not None
    assert pipeline.as_of_join_report is not None
    assert pipeline.treated is not None
    assert pipeline.outlier_report is not None
    assert pipeline.scored is not None
    assert pipeline.score_report is not None
    assert pipeline.neutralized is not None
    assert pipeline.neutralization_report is not None
    assert pipeline.final is not None
    assert pipeline.final_signal_report is not None


def test_join_restricts_fundamentals_to_eligible_securities(pipeline: BacktestPipeline) -> None:
    pipeline.run()

    assert pipeline.market_universe is not None
    assert sorted(pipeline.market_universe["security_id"].unique()) == [1, 2]

    # ADR-0011: the as-of join is driven from market_universe, so fundamentals for the
    # ineligible security (3, exchcd == 2) never reach the joined frame at all -- not
    # just excluded from the final output, but absent from every downstream stage's
    # cross-sectional statistics too.
    assert pipeline.market_fundamentals_joined is not None
    joined_ids = sorted(pipeline.market_fundamentals_joined["security_id"].unique())
    assert joined_ids == [1, 2]
    assert len(pipeline.market_fundamentals_joined) == 4  # 2 eligible securities x 2 dates
    assert set(pipeline.market_fundamentals_joined["bm"].unique()) == {0.5, 1.5}


def test_funda_cross_sectional_stats_restricted_to_eligible_universe(
    pipeline: BacktestPipeline,
) -> None:
    """The bug ADR-0011 fixes: bm's z-score must be computed only over the eligible
    universe (permnos 1, 2; bm = 0.5, 1.5), never over ineligible permno 3's bm = 2.5.
    """
    pipeline.run()

    assert pipeline.scored is not None
    assert sorted(pipeline.scored["security_id"].unique()) == [1, 2]

    row = pipeline.scored[
        (pipeline.scored["security_id"] == 1) & (pipeline.scored["date"] == pd.Timestamp("2020-01-02"))
    ]
    assert len(row) == 1
    # mean([0.5, 1.5]) = 1.0, std([0.5, 1.5], ddof=1) = 0.70710678...
    # z = (0.5 - 1.0) / 0.70710678... = -0.70710678...
    # (if permno 3's bm = 2.5 had leaked in, this would instead be exactly -1.0)
    assert row["bm_treated_raw_score"].iloc[0] == pytest.approx(-0.7071067811865476)


def test_scored_has_raw_score_columns_for_both_sources(pipeline: BacktestPipeline) -> None:
    pipeline.run()

    assert pipeline.scored is not None
    assert "return_treated_raw_score" in pipeline.scored.columns
    assert "bm_treated_raw_score" in pipeline.scored.columns


def test_beta_not_computed_and_neutralization_is_noop_without_config(
    pipeline: BacktestPipeline,
) -> None:
    # The fixture's config has no "beta"/"neutralization"/"final_signal"/
    # "pure_alpha"/"isovol" sections -- all seven stages must still run cleanly
    # (ADR-0012/ADR-0013/ADR-0014/ADR-0015/ADR-0016: optional, not required)
    # and produce no observable effect.
    pipeline.run()

    assert pipeline.benchmark_alignment_report is None
    assert pipeline.benchmark_aligned is None
    assert pipeline.risk_free_alignment_report is None
    assert pipeline.risk_free_aligned is None
    assert pipeline.beta_report is None
    assert pipeline.market_clean is not None and "beta" not in pipeline.market_clean.columns
    assert pipeline.neutralization_report is not None
    assert pipeline.neutralization_report.diagnostics == ()
    assert pipeline.neutralized is not None
    assert not any(c.endswith("_neutral") for c in pipeline.neutralized.columns)
    assert pipeline.final_signal_report is not None
    assert pipeline.final_signal_report.diagnostics == ()
    assert pipeline.final is not None
    assert not any(c.endswith("_final") for c in pipeline.final.columns)
    assert pipeline.pure_alpha_report is None
    assert pipeline.pure_alpha is None
    assert pipeline.portfolio_volatility_report is None
    assert pipeline.portfolio_volatility is None
    assert pipeline.isovol_report is None
    assert pipeline.isovol is None


# --- beta + neutralization ----------------------------------------------------------

_MARKET_ROWS_MULTI_DATE = [
    # 3 eligible securities (1, 2, 4; exchcd == 1) per date -- needed so the
    # per-date neutralization regression (intercept + beta = 2 parameters) has
    # more than 2 valid rows and isn't degenerate. Security 3 (exchcd == 2)
    # stays ineligible, as in the other fixture.
    {"permno": 1, "date": "2020-01-02", "prc": 10.0, "vol": 100, "ret": 0.010, "exchcd": 1},
    {"permno": 2, "date": "2020-01-02", "prc": 20.0, "vol": 200, "ret": 0.020, "exchcd": 1},
    {"permno": 3, "date": "2020-01-02", "prc": 30.0, "vol": 300, "ret": 0.030, "exchcd": 2},
    {"permno": 4, "date": "2020-01-02", "prc": 40.0, "vol": 400, "ret": 0.005, "exchcd": 1},
    {"permno": 1, "date": "2020-01-03", "prc": 10.1, "vol": 110, "ret": -0.010, "exchcd": 1},
    {"permno": 2, "date": "2020-01-03", "prc": 20.4, "vol": 210, "ret": 0.020, "exchcd": 1},
    {"permno": 3, "date": "2020-01-03", "prc": 30.9, "vol": 310, "ret": 0.030, "exchcd": 2},
    {"permno": 4, "date": "2020-01-03", "prc": 40.4, "vol": 410, "ret": 0.010, "exchcd": 1},
    {"permno": 1, "date": "2020-01-06", "prc": 10.2, "vol": 120, "ret": 0.015, "exchcd": 1},
    {"permno": 2, "date": "2020-01-06", "prc": 20.8, "vol": 220, "ret": 0.025, "exchcd": 1},
    {"permno": 3, "date": "2020-01-06", "prc": 31.9, "vol": 320, "ret": 0.035, "exchcd": 2},
    {"permno": 4, "date": "2020-01-06", "prc": 40.8, "vol": 420, "ret": 0.008, "exchcd": 1},
]

_BENCHMARK_LEVELS = [
    {"date": "2019-12-31", "level": 100.00},
    {"date": "2020-01-02", "level": 101.00},
    {"date": "2020-01-03", "level": 102.00},
    {"date": "2020-01-06", "level": 103.02},
]

_RISK_FREE_RETURNS = [
    {"date": "2020-01-02", "rf": 0.0},
    {"date": "2020-01-03", "rf": 0.0},
    {"date": "2020-01-06", "rf": 0.0},
]


def _write_beta_input_parquet(
    rows: list[dict[str, object]], value_column: str, path: Path
) -> None:
    df = pd.DataFrame(rows).set_index("date")
    df.index = pd.to_datetime(df.index)
    df.to_parquet(path)
    assert value_column in df.columns


def _write_beta_neutralization_config(
    tmp_path: Path,
    market_path: Path,
    funda_path: Path,
    benchmark_path: Path,
    risk_free_path: Path,
) -> Path:
    config = {
        "data_sources": {
            "market": {"path": str(market_path), "preset": "wrds"},
            "fundamentals": {"path": str(funda_path), "preset": "wrds"},
        },
        "universe": {"filters": [{"column": "exchcd", "operator": "==", "value": 1}]},
        "outlier_treatment": {
            "treatments": [
                {
                    "column": "return",
                    "method": "quantile",
                    "lower_quantile": 0.0,
                    "upper_quantile": 1.0,
                    "action": "winsorize",
                }
            ]
        },
        "signal_construction": {
            "scores": [{"column": "return_treated", "method": "zscore", "direction": 1}]
        },
        "beta": {
            "benchmark_path": str(benchmark_path),
            "benchmark_level_column": "level",
            "risk_free_path": str(risk_free_path),
            "risk_free_rate_column": "rf",
            "window": 2,
            "min_periods": 1,
        },
        "neutralization": {
            "signal_columns": ["return_treated_raw_score"],
            "exposures": [{"type": "continuous", "column": "beta"}],
        },
        "final_signal": {
            "standardizations": [
                {"column": "return_treated_raw_score_neutral", "method": "zscore"}
            ]
        },
        "pure_alpha": {
            "signal_column": "return_treated_raw_score_neutral_final",
            "mapping": {"method": "tanh", "kappa": 1.0},
            "exposures": [{"type": "continuous", "column": "beta"}],
            "gross_exposure": 2.0,
        },
        "isovol": {
            "target_volatility_annualized": 0.16,
            "periods_per_year": 252,
            "max_leverage": 10.0,
            "window": 2,
            "min_periods": 1,
        },
    }
    config_path = tmp_path / "backtest_beta.json"
    config_path.write_text(json.dumps(config))
    return config_path


@pytest.fixture
def pipeline_with_beta(tmp_path: Path) -> BacktestPipeline:
    market_path = tmp_path / "market_multi.parquet"
    funda_path = tmp_path / "funda_multi.parquet"
    benchmark_path = tmp_path / "benchmark.parquet"
    risk_free_path = tmp_path / "risk_free.parquet"

    _write_parquet(_MARKET_ROWS_MULTI_DATE, ["date"], market_path)
    _write_parquet(_FUNDA_ROWS, ["adate", "qdate", "public_date"], funda_path)
    _write_beta_input_parquet(_BENCHMARK_LEVELS, "level", benchmark_path)
    _write_beta_input_parquet(_RISK_FREE_RETURNS, "rf", risk_free_path)

    config_path = _write_beta_neutralization_config(
        tmp_path, market_path, funda_path, benchmark_path, risk_free_path
    )
    return BacktestPipeline.from_config(config_path)


def test_align_benchmark_and_risk_free_produces_market_calendar_aligned_series(
    pipeline_with_beta: BacktestPipeline,
) -> None:
    pipeline_with_beta.run()

    assert pipeline_with_beta.market_clean is not None
    market_dates = sorted(pipeline_with_beta.market_clean["date"].unique())

    assert pipeline_with_beta.benchmark_aligned is not None
    assert pipeline_with_beta.risk_free_aligned is not None
    assert list(pipeline_with_beta.benchmark_aligned.index) == market_dates
    assert list(pipeline_with_beta.risk_free_aligned.index) == market_dates

    assert pipeline_with_beta.benchmark_alignment_report is not None
    assert pipeline_with_beta.risk_free_alignment_report is not None
    assert pipeline_with_beta.benchmark_alignment_report.n_calendar_dates == len(market_dates)

    # compute_beta consumes these directly -- beta must actually get computed
    # from them, not fail silently.
    assert pipeline_with_beta.beta_report is not None
    assert pipeline_with_beta.beta_report.n_beta_computed > 0


def test_beta_column_flows_through_to_scored_frame(pipeline_with_beta: BacktestPipeline) -> None:
    pipeline_with_beta.run()

    assert pipeline_with_beta.beta_report is not None
    assert pipeline_with_beta.beta_report.n_beta_computed > 0
    assert pipeline_with_beta.market_clean is not None
    assert "beta" in pipeline_with_beta.market_clean.columns

    assert pipeline_with_beta.scored is not None
    assert "beta" in pipeline_with_beta.scored.columns
    # only eligible securities (1, 2, 4) reach the joined/scored frame.
    assert sorted(pipeline_with_beta.scored["security_id"].unique()) == [1, 2, 4]


def test_neutralization_consumes_beta_as_an_exposure(pipeline_with_beta: BacktestPipeline) -> None:
    pipeline_with_beta.run()

    assert pipeline_with_beta.neutralized is not None
    assert "return_treated_raw_score_neutral" in pipeline_with_beta.neutralized.columns
    assert pipeline_with_beta.neutralization_report is not None
    diag = pipeline_with_beta.neutralization_report.diagnostics[0]
    assert diag.column == "return_treated_raw_score"
    assert "beta" in diag.exposure_columns
    assert diag.n_valid_rows > 0


def test_finalize_standardizes_neutralized_signal(pipeline_with_beta: BacktestPipeline) -> None:
    pipeline_with_beta.run()

    assert pipeline_with_beta.final is not None
    assert "return_treated_raw_score_neutral_final" in pipeline_with_beta.final.columns
    assert pipeline_with_beta.final_signal_report is not None
    diag = pipeline_with_beta.final_signal_report.diagnostics[0]
    assert diag.column == "return_treated_raw_score_neutral"
    assert diag.method == "zscore"
    assert diag.n_input_rows == len(pipeline_with_beta.neutralized)


def test_construct_pure_alpha_produces_dollar_and_beta_neutral_portfolio(
    pipeline_with_beta: BacktestPipeline,
) -> None:
    pipeline_with_beta.run()

    assert pipeline_with_beta.pure_alpha is not None
    col = "return_treated_raw_score_neutral_final_pure_alpha"
    assert col in pipeline_with_beta.pure_alpha.columns
    assert pipeline_with_beta.pure_alpha_report is not None
    report = pipeline_with_beta.pure_alpha_report
    assert report.signal_column == "return_treated_raw_score_neutral_final"
    assert report.mapping_method == "tanh"
    assert report.gross_exposure_target == 2.0

    for _, group in pipeline_with_beta.pure_alpha.groupby("date"):
        weights = group[col]
        if weights.notna().any():
            assert weights.sum() == pytest.approx(0.0, abs=1e-9)
            assert weights.abs().sum() == pytest.approx(2.0, abs=1e-9)


def test_isovol_scales_pure_alpha_weights(pipeline_with_beta: BacktestPipeline) -> None:
    pipeline_with_beta.run()

    assert pipeline_with_beta.portfolio_volatility is not None
    assert pipeline_with_beta.portfolio_volatility_report is not None
    vol_report = pipeline_with_beta.portfolio_volatility_report
    assert vol_report.window == 2
    assert vol_report.min_periods == 1
    # window=2 needs >=2 distinct prior trading dates -- only the fixture's
    # last date (2020-01-06) has that; the first two are degenerate/empty.
    assert vol_report.n_volatility_computed == 1

    assert pipeline_with_beta.isovol is not None
    iso_col = "return_treated_raw_score_neutral_final_pure_alpha_iso"
    assert iso_col in pipeline_with_beta.isovol.columns
    assert pipeline_with_beta.isovol_report is not None
    iso_report = pipeline_with_beta.isovol_report
    assert iso_report.target_volatility_annualized == 0.16
    assert iso_report.n_scaled == 1

    pure_alpha_col = "return_treated_raw_score_neutral_final_pure_alpha"
    last_date = pd.Timestamp("2020-01-06")
    scaled = pipeline_with_beta.isovol[pipeline_with_beta.isovol["date"] == last_date]
    # isovol is a single scalar per date -- the ratio between iso and pre-iso
    # weights must be identical across every security that date.
    ratios = (scaled[iso_col] / scaled[pure_alpha_col]).dropna()
    assert ratios.nunique() == 1

    earlier_dates = pipeline_with_beta.isovol[pipeline_with_beta.isovol["date"] != last_date]
    assert earlier_dates[iso_col].isna().all()


def test_neutralization_raises_clear_error_when_beta_exposure_configured_without_beta_section(
    tmp_path: Path,
) -> None:
    market_path = tmp_path / "market.parquet"
    funda_path = tmp_path / "funda.parquet"
    _write_parquet(_MARKET_ROWS, ["date"], market_path)
    _write_parquet(_FUNDA_ROWS, ["adate", "qdate", "public_date"], funda_path)

    config = {
        "data_sources": {
            "market": {"path": str(market_path), "preset": "wrds"},
            "fundamentals": {"path": str(funda_path), "preset": "wrds"},
        },
        "universe": {"filters": [{"column": "exchcd", "operator": "==", "value": 1}]},
        "signal_construction": {
            "scores": [{"column": "return_treated", "method": "zscore", "direction": 1}]
        },
        "outlier_treatment": {
            "treatments": [
                {
                    "column": "return",
                    "method": "quantile",
                    "lower_quantile": 0.0,
                    "upper_quantile": 1.0,
                    "action": "winsorize",
                }
            ]
        },
        "neutralization": {
            "signal_columns": ["return_treated_raw_score"],
            "exposures": [{"type": "continuous", "column": "beta"}],
        },
    }
    config_path = tmp_path / "backtest_missing_beta.json"
    config_path.write_text(json.dumps(config))

    pipeline = BacktestPipeline.from_config(config_path)

    with pytest.raises(ValueError, match="unknown exposure column"):
        pipeline.run()


# --- real-data end-to-end ----------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[1]
_EXAMPLE_CONFIG = _REPO_ROOT / "config" / "backtest.example.json"
_MARKET_DATA_FILE = _REPO_ROOT / "data" / "wrds_gross_query.parquet"


@pytest.mark.skipif(
    not _MARKET_DATA_FILE.exists(), reason="requires local WRDS data in data/ (not in git)"
)
def test_example_config_beta_and_neutralization_run_end_to_end_on_real_data() -> None:
    # Paths in the example config are relative to the repo root, matching how the
    # test suite itself is invoked (uv run pytest from the repo root).
    pipeline = BacktestPipeline.from_config(_EXAMPLE_CONFIG)
    pipeline.run()

    assert pipeline.beta_report is not None
    assert pipeline.beta_report.n_beta_computed > 0
    assert pipeline.market_clean is not None
    assert "beta" in pipeline.market_clean.columns

    assert pipeline.scored is not None
    assert "beta" in pipeline.scored.columns

    assert pipeline.neutralized is not None
    assert "return_treated_raw_score_neutral" in pipeline.neutralized.columns
    assert pipeline.neutralization_report is not None
    diag = pipeline.neutralization_report.diagnostics[0]
    # beta and gsector (GICS sector dummies) are both configured exposures now --
    # a row needs complete-case beta *and* gsector to get a neutral score, so
    # n_valid_rows is bounded by (not equal to) beta's own coverage.
    assert "gsector_15" in diag.exposure_columns
    assert 0 < diag.n_valid_rows <= pipeline.beta_report.n_beta_computed

    assert pipeline.final is not None
    assert "return_treated_raw_score_neutral_final" in pipeline.final.columns
    assert pipeline.final_signal_report is not None
    final_diag = pipeline.final_signal_report.diagnostics[0]
    assert final_diag.column == "return_treated_raw_score_neutral"
    assert final_diag.method == "robust_zscore"

    assert pipeline.pure_alpha is not None
    pure_alpha_col = "return_treated_raw_score_neutral_final_pure_alpha"
    assert pure_alpha_col in pipeline.pure_alpha.columns
    assert pipeline.pure_alpha_report is not None
    pa_report = pipeline.pure_alpha_report
    assert pa_report.mapping_method == "tanh"
    assert pa_report.gross_exposure_target == 2.0
    assert pa_report.n_valid_rows > 0
    # exact by construction (closed-form joint projection + scalar gross
    # renormalization), verified against the full real WRDS panel.
    assert pa_report.max_abs_net_exposure == pytest.approx(0.0, abs=1e-6)
    assert pa_report.max_abs_projected_exposure == pytest.approx(0.0, abs=1e-6)
    assert pa_report.max_gross_exposure_error == pytest.approx(0.0, abs=1e-6)

    assert pipeline.portfolio_volatility_report is not None
    vol_report = pipeline.portfolio_volatility_report
    assert vol_report.n_volatility_computed > 0
    # a book of hundreds of held names essentially always has at least one
    # with a gap somewhere in a 252-day window -- confirms the per-security
    # (not per-date) exclusion policy is actually engaging on real data.
    assert vol_report.n_dates_with_excluded_securities > 0
    assert vol_report.mean_security_coverage is not None
    assert 0.0 < vol_report.mean_security_coverage <= 1.0

    assert pipeline.isovol is not None
    iso_col = f"{pure_alpha_col}_iso"
    assert iso_col in pipeline.isovol.columns
    assert pipeline.isovol_report is not None
    iso_report = pipeline.isovol_report
    assert iso_report.n_scaled == vol_report.n_volatility_computed
    assert iso_report.mean_scale_factor is not None and iso_report.mean_scale_factor > 0