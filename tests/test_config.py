import json
from pathlib import Path

import pandas as pd
import pytest

from backtester.config import (
    CombinedDataSourcesConfig,
    SeparateDataSourcesConfig,
    load_beta_config,
    load_data_sources_config,
    load_final_signal_config,
    load_isovol_config,
    load_neutralization_config,
    load_outlier_treatment_config,
    load_pure_alpha_config,
    load_signal_construction_config,
    load_universe_config,
    read_data_sources,
)
from backtester.data.schema import (
    WRDS_FUNDAMENTALS_COLUMNS,
    WRDS_MARKET_COLUMNS,
    MarketColumnMapping,
)
from backtester.exceptions import AmbiguousDataSourceConfigWarning
from backtester.outliers.types import MadOutlierTreatment, QuantileOutlierTreatment
from backtester.portfolio.types import LinearWeightMapping, TanhWeightMapping
from backtester.signals.types import (
    CategoricalExposure,
    ContinuousExposure,
    RobustZScoreTransform,
    ZScoreTransform,
)
from backtester.universe.types import EligibilityFilter


def _write_config(tmp_path: Path, config: dict[str, object]) -> Path:
    path = tmp_path / "backtest.json"
    path.write_text(json.dumps(config))
    return path


def _separate_config(
    market_entry: dict[str, object], fundamentals_entry: dict[str, object] | None = None
) -> dict[str, object]:
    return {
        "data_sources": {
            "market": market_entry,
            "fundamentals": fundamentals_entry or {"path": "funda.parquet", "preset": "wrds"},
        }
    }


def test_loads_preset_mapping(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path, _separate_config({"path": "market.parquet", "preset": "wrds"})
    )

    config = load_data_sources_config(config_path)

    assert isinstance(config, SeparateDataSourcesConfig)
    assert config.market_path == Path("market.parquet")
    assert config.market_columns == WRDS_MARKET_COLUMNS
    assert config.fundamentals_columns == WRDS_FUNDAMENTALS_COLUMNS


def test_loads_custom_column_mapping(tmp_path: Path) -> None:
    custom_columns = {
        "security_id": "SecurityID",
        "date": "TradeDate",
        "price": "ClosePrice",
        "volume": "Volume",
        "return": "DailyReturn",
    }
    config_path = _write_config(
        tmp_path, _separate_config({"path": "other.parquet", "columns": custom_columns})
    )

    config = load_data_sources_config(config_path)

    assert isinstance(config, SeparateDataSourcesConfig)
    assert config.market_columns == MarketColumnMapping(
        security_id="SecurityID",
        date="TradeDate",
        price="ClosePrice",
        volume="Volume",
        return_="DailyReturn",
    )


def test_raises_when_neither_preset_nor_columns_given(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, _separate_config({"path": "market.parquet"}))

    with pytest.raises(ValueError, match="exactly one of 'preset' or 'columns'"):
        load_data_sources_config(config_path)


def test_raises_when_both_preset_and_columns_given(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _separate_config({"path": "market.parquet", "preset": "wrds", "columns": {}}),
    )

    with pytest.raises(ValueError, match="exactly one of 'preset' or 'columns'"):
        load_data_sources_config(config_path)


def test_raises_on_unknown_preset(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path, _separate_config({"path": "market.parquet", "preset": "bloomberg"})
    )

    with pytest.raises(ValueError, match="unknown market preset 'bloomberg'"):
        load_data_sources_config(config_path)


def test_raises_on_custom_mapping_missing_fields(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _separate_config({"path": "market.parquet", "columns": {"security_id": "SecurityID"}}),
    )

    with pytest.raises(ValueError, match="missing fields"):
        load_data_sources_config(config_path)


def test_raises_on_custom_mapping_unknown_fields(tmp_path: Path) -> None:
    custom_columns = {
        "security_id": "SecurityID",
        "date": "TradeDate",
        "price": "ClosePrice",
        "volume": "Volume",
        "return": "DailyReturn",
        "not_a_real_field": "Whatever",
    }
    config_path = _write_config(
        tmp_path, _separate_config({"path": "market.parquet", "columns": custom_columns})
    )

    with pytest.raises(ValueError, match="unknown fields"):
        load_data_sources_config(config_path)


def test_raises_on_missing_data_sources_key(tmp_path: Path) -> None:
    config_path = tmp_path / "backtest.json"
    config_path.write_text(json.dumps({}))

    with pytest.raises(ValueError, match="missing required config key"):
        load_data_sources_config(config_path)


def test_raises_when_only_market_given(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path, {"data_sources": {"market": {"path": "market.parquet", "preset": "wrds"}}}
    )

    with pytest.raises(ValueError, match="must specify either 'combined'"):
        load_data_sources_config(config_path)


# --- combined-source config ------------------------------------------------------


def _combined_config(entry: dict[str, object]) -> dict[str, object]:
    return {"data_sources": {"combined": entry}}


def test_loads_combined_config_with_defaults(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _combined_config(
            {
                "path": "combined.parquet",
                "market": {"preset": "wrds"},
                "fundamentals": {"preset": "wrds"},
            }
        ),
    )

    config = load_data_sources_config(config_path)

    assert isinstance(config, CombinedDataSourcesConfig)
    assert config.path == Path("combined.parquet")
    assert config.dataset_column == "dataset"
    assert config.market_dataset_value == "market"
    assert config.fundamentals_dataset_value == "fundamentals"
    assert config.market_columns == WRDS_MARKET_COLUMNS
    assert config.fundamentals_columns == WRDS_FUNDAMENTALS_COLUMNS


def test_loads_combined_config_with_custom_dataset_column_and_values(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        _combined_config(
            {
                "path": "combined.parquet",
                "dataset_column": "source_type",
                "market": {"dataset_value": "mkt", "preset": "wrds"},
                "fundamentals": {"dataset_value": "fnd", "preset": "wrds"},
            }
        ),
    )

    config = load_data_sources_config(config_path)

    assert isinstance(config, CombinedDataSourcesConfig)
    assert config.dataset_column == "source_type"
    assert config.market_dataset_value == "mkt"
    assert config.fundamentals_dataset_value == "fnd"


def test_combined_null_is_treated_as_absent(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "data_sources": {
                "combined": None,
                "market": {"path": "market.parquet", "preset": "wrds"},
                "fundamentals": {"path": "funda.parquet", "preset": "wrds"},
            }
        },
    )

    config = load_data_sources_config(config_path)

    assert isinstance(config, SeparateDataSourcesConfig)


def test_combined_takes_precedence_and_warns_when_all_present(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "data_sources": {
                "combined": {
                    "path": "combined.parquet",
                    "market": {"preset": "wrds"},
                    "fundamentals": {"preset": "wrds"},
                },
                "market": {"path": "market.parquet", "preset": "wrds"},
                "fundamentals": {"path": "funda.parquet", "preset": "wrds"},
            }
        },
    )

    with pytest.warns(AmbiguousDataSourceConfigWarning, match="'combined' takes precedence"):
        config = load_data_sources_config(config_path)

    assert isinstance(config, CombinedDataSourcesConfig)


def test_raises_when_neither_combined_nor_separate_given(tmp_path: Path) -> None:
    config_path = tmp_path / "backtest.json"
    config_path.write_text(json.dumps({"data_sources": {}}))

    with pytest.raises(ValueError, match="must specify either 'combined'"):
        load_data_sources_config(config_path)


# --- universe config ---------------------------------------------------------------


def test_universe_config_absent_means_no_filters(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, {"data_sources": {}})

    config = load_universe_config(config_path)

    assert config.filters == ()


def test_universe_config_empty_filters_list_means_no_filters(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, {"universe": {"filters": []}})

    config = load_universe_config(config_path)

    assert config.filters == ()


def test_universe_config_loads_filters(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "universe": {
                "filters": [
                    {"column": "exchcd", "operator": "in", "value": [1, 2, 3]},
                    {"column": "price", "operator": ">=", "value": 5.0},
                ]
            }
        },
    )

    config = load_universe_config(config_path)

    assert config.filters == (
        EligibilityFilter(column="exchcd", operator="in", value=[1, 2, 3]),
        EligibilityFilter(column="price", operator=">=", value=5.0),
    )


def test_universe_config_raises_on_filter_missing_column(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path, {"universe": {"filters": [{"operator": ">=", "value": 5.0}]}}
    )

    with pytest.raises(ValueError, match="missing required key: 'column'"):
        load_universe_config(config_path)


# --- outlier treatment config -------------------------------------------------------


def test_outlier_treatment_config_absent_means_no_treatments(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, {"data_sources": {}})

    config = load_outlier_treatment_config(config_path)

    assert config.treatments == ()


def test_outlier_treatment_config_loads_flat_treatments_list(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "outlier_treatment": {
                "treatments": [
                    {
                        "column": "return",
                        "method": "quantile",
                        "lower_quantile": 0.01,
                        "upper_quantile": 0.99,
                        "action": "winsorize",
                    },
                    {"column": "bm", "method": "mad", "multiplier": 3.0, "action": "truncate"},
                ]
            }
        },
    )

    config = load_outlier_treatment_config(config_path)

    assert config.treatments == (
        QuantileOutlierTreatment(
            column="return", lower_quantile=0.01, upper_quantile=0.99, action="winsorize"
        ),
        MadOutlierTreatment(column="bm", multiplier=3.0, action="truncate"),
    )


def test_outlier_treatment_config_defaults_action_to_winsorize(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "outlier_treatment": {
                "treatments": [
                    {
                        "column": "return",
                        "method": "quantile",
                        "lower_quantile": 0.01,
                        "upper_quantile": 0.99,
                    }
                ]
            }
        },
    )

    config = load_outlier_treatment_config(config_path)

    assert config.treatments[0].action == "winsorize"


def test_outlier_treatment_config_raises_on_unknown_method(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {"outlier_treatment": {"treatments": [{"column": "return", "method": "zscore"}]}},
    )

    with pytest.raises(ValueError, match="unknown outlier treatment method"):
        load_outlier_treatment_config(config_path)


def test_outlier_treatment_config_raises_on_missing_method(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path, {"outlier_treatment": {"treatments": [{"column": "return"}]}}
    )

    with pytest.raises(ValueError, match="missing required key: 'method'"):
        load_outlier_treatment_config(config_path)


# --- signal construction config -----------------------------------------------------


def test_signal_construction_config_absent_means_no_scores(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, {"data_sources": {}})

    config = load_signal_construction_config(config_path)

    assert config.scores == ()
    assert config.combination is None


def test_signal_construction_config_loads_flat_scores_list_with_cross_source_combine(
    tmp_path: Path,
) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "signal_construction": {
                "scores": [
                    {"column": "return_treated", "method": "zscore", "direction": 1},
                    {"column": "bm_treated", "method": "robust_zscore", "direction": -1},
                    {"column": "roa_treated", "method": "zscore"},
                ],
                "combine": {
                    "columns": [
                        "return_treated_raw_score",
                        "bm_treated_raw_score",
                        "roa_treated_raw_score",
                    ]
                },
            }
        },
    )

    config = load_signal_construction_config(config_path)

    assert config.scores == (
        ZScoreTransform(column="return_treated", direction=1),
        RobustZScoreTransform(column="bm_treated", direction=-1),
        ZScoreTransform(column="roa_treated", direction=1),
    )
    assert config.combination is not None
    assert config.combination.columns == (
        "return_treated_raw_score",
        "bm_treated_raw_score",
        "roa_treated_raw_score",
    )
    assert config.combination.output_column == "composite_raw_score"


def test_signal_construction_config_custom_combination_output_column(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "signal_construction": {
                "scores": [{"column": "a", "method": "zscore"}],
                "combine": {"columns": ["a_raw_score"], "output_column": "my_signal"},
            }
        },
    )

    config = load_signal_construction_config(config_path)

    assert config.combination.output_column == "my_signal"


def test_signal_construction_config_raises_on_unknown_method(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {"signal_construction": {"scores": [{"column": "a", "method": "median"}]}},
    )

    with pytest.raises(ValueError, match="unknown score transform method"):
        load_signal_construction_config(config_path)


def test_signal_construction_config_raises_on_missing_method(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path, {"signal_construction": {"scores": [{"column": "a"}]}}
    )

    with pytest.raises(ValueError, match="missing required key: 'method'"):
        load_signal_construction_config(config_path)


# --- beta config ---------------------------------------------------------------------


def test_beta_config_absent_means_none(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, {"data_sources": {}})

    config = load_beta_config(config_path)

    assert config is None


def test_beta_config_loads_required_and_defaulted_fields(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "beta": {
                "benchmark_path": "data/russell_returns.parquet",
                "risk_free_path": "data/risk_free_returns.parquet",
            }
        },
    )

    config = load_beta_config(config_path)

    assert config is not None
    assert config.benchmark_path == Path("data/russell_returns.parquet")
    assert config.benchmark_level_column == "Russell 1000"
    assert config.benchmark_max_ffill == 5
    assert config.benchmark_calendar_max_ffill == 5
    assert config.risk_free_path == Path("data/risk_free_returns.parquet")
    assert config.risk_free_rate_column == "rf_returns"
    assert config.risk_free_max_ffill == 5
    assert config.risk_free_calendar_max_ffill == 5
    assert config.window == 252
    assert config.min_periods == 126


def test_beta_config_overrides_defaults(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "beta": {
                "benchmark_path": "b.parquet",
                "benchmark_level_column": "S&P 500",
                "benchmark_max_ffill": 3,
                "benchmark_calendar_max_ffill": 2,
                "risk_free_path": "rf.parquet",
                "risk_free_rate_column": "custom_rf",
                "risk_free_max_ffill": None,
                "risk_free_calendar_max_ffill": None,
                "window": 60,
                "min_periods": 20,
            }
        },
    )

    config = load_beta_config(config_path)

    assert config is not None
    assert config.benchmark_level_column == "S&P 500"
    assert config.benchmark_max_ffill == 3
    assert config.benchmark_calendar_max_ffill == 2
    assert config.risk_free_rate_column == "custom_rf"
    assert config.risk_free_max_ffill is None
    assert config.risk_free_calendar_max_ffill is None
    assert config.window == 60
    assert config.min_periods == 20


def test_beta_config_raises_on_missing_required_path(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, {"beta": {"benchmark_path": "b.parquet"}})

    with pytest.raises(ValueError, match="missing required key: 'risk_free_path'"):
        load_beta_config(config_path)


# --- neutralization config ------------------------------------------------------------


def test_neutralization_config_absent_means_no_neutralization(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, {"data_sources": {}})

    config = load_neutralization_config(config_path)

    assert config.signal_columns == ()
    assert config.exposures == ()


def test_neutralization_config_loads_signal_columns_and_exposures(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "neutralization": {
                "signal_columns": ["composite_raw_score"],
                "exposures": [
                    {"type": "continuous", "column": "beta"},
                    {"type": "categorical", "column": "gsector"},
                ],
            }
        },
    )

    config = load_neutralization_config(config_path)

    assert config.signal_columns == ("composite_raw_score",)
    assert config.exposures == (
        ContinuousExposure(column="beta"),
        CategoricalExposure(column="gsector"),
    )


def test_neutralization_config_raises_on_unknown_exposure_type(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "neutralization": {
                "signal_columns": ["composite_raw_score"],
                "exposures": [{"type": "industry_dummy", "column": "gsector"}],
            }
        },
    )

    with pytest.raises(ValueError, match="unknown exposure type"):
        load_neutralization_config(config_path)


# --- final signal config ---------------------------------------------------------------


def test_final_signal_config_absent_means_no_standardization(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, {"data_sources": {}})

    config = load_final_signal_config(config_path)

    assert config.standardizations == ()


def test_final_signal_config_loads_standardizations(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "final_signal": {
                "standardizations": [
                    {"column": "composite_raw_score_neutral", "method": "robust_zscore"},
                ]
            }
        },
    )

    config = load_final_signal_config(config_path)

    assert config.standardizations == (
        RobustZScoreTransform(column="composite_raw_score_neutral"),
    )


def test_final_signal_config_raises_on_unknown_method(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "final_signal": {
                "standardizations": [{"column": "composite_raw_score_neutral", "method": "rank"}]
            }
        },
    )

    with pytest.raises(ValueError, match="unknown score transform method"):
        load_final_signal_config(config_path)


# --- pure alpha config -------------------------------------------------------------


def test_pure_alpha_config_absent_means_none(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, {"data_sources": {}})

    config = load_pure_alpha_config(config_path)

    assert config is None


def test_pure_alpha_config_loads_linear_mapping_and_defaults(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "pure_alpha": {
                "signal_column": "composite_final",
                "mapping": {"method": "linear"},
            }
        },
    )

    config = load_pure_alpha_config(config_path)

    assert config is not None
    assert config.signal_column == "composite_final"
    assert config.mapping == LinearWeightMapping()
    assert config.exposures == ()
    assert config.gross_exposure == 2.0


def test_pure_alpha_config_loads_tanh_mapping_and_exposures(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "pure_alpha": {
                "signal_column": "composite_final",
                "mapping": {"method": "tanh", "kappa": 2.5},
                "exposures": [
                    {"type": "continuous", "column": "beta"},
                    {"type": "categorical", "column": "gsector"},
                ],
                "gross_exposure": 1.5,
            }
        },
    )

    config = load_pure_alpha_config(config_path)

    assert config is not None
    assert config.mapping == TanhWeightMapping(kappa=2.5)
    assert config.exposures == (
        ContinuousExposure(column="beta"),
        CategoricalExposure(column="gsector"),
    )
    assert config.gross_exposure == 1.5


def test_pure_alpha_config_raises_on_unknown_mapping_method(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "pure_alpha": {
                "signal_column": "composite_final",
                "mapping": {"method": "softmax"},
            }
        },
    )

    with pytest.raises(ValueError, match="unknown weight mapping method"):
        load_pure_alpha_config(config_path)


def test_pure_alpha_config_raises_on_missing_signal_column(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path, {"pure_alpha": {"mapping": {"method": "linear"}}}
    )

    with pytest.raises(ValueError, match="missing required key: 'signal_column'"):
        load_pure_alpha_config(config_path)


# --- isovol config -----------------------------------------------------------------


def test_isovol_config_absent_means_none(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, {"data_sources": {}})

    config = load_isovol_config(config_path)

    assert config is None


def test_isovol_config_loads_required_and_defaulted_fields(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path, {"isovol": {"target_volatility_annualized": 0.12}}
    )

    config = load_isovol_config(config_path)

    assert config is not None
    assert config.target_volatility_annualized == 0.12
    assert config.periods_per_year is None
    assert config.max_leverage is None
    assert config.window == 252
    assert config.min_periods == 126


def test_isovol_config_overrides_defaults(tmp_path: Path) -> None:
    config_path = _write_config(
        tmp_path,
        {
            "isovol": {
                "target_volatility_annualized": 0.08,
                "periods_per_year": 260,
                "max_leverage": 3.0,
                "window": 120,
                "min_periods": 60,
            }
        },
    )

    config = load_isovol_config(config_path)

    assert config is not None
    assert config.periods_per_year == 260
    assert config.max_leverage == 3.0
    assert config.window == 120
    assert config.min_periods == 60


def test_isovol_config_raises_on_missing_target_volatility(tmp_path: Path) -> None:
    config_path = _write_config(tmp_path, {"isovol": {"window": 100}})

    with pytest.raises(
        ValueError, match="missing required key: 'target_volatility_annualized'"
    ):
        load_isovol_config(config_path)


# --- real-data end-to-end ----------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[1]
_EXAMPLE_CONFIG = _REPO_ROOT / "config" / "backtest.example.json"
_MARKET_DATA_FILE = _REPO_ROOT / "data" / "wrds_gross_query.parquet"


@pytest.mark.skipif(
    not _EXAMPLE_CONFIG.exists(), reason="repo checkout missing config/backtest.example.json"
)
def test_example_config_uses_the_wrds_preset() -> None:
    config = load_data_sources_config(_EXAMPLE_CONFIG)

    assert isinstance(config, SeparateDataSourcesConfig)
    assert config.market_columns == WRDS_MARKET_COLUMNS
    assert config.fundamentals_columns == WRDS_FUNDAMENTALS_COLUMNS


@pytest.mark.skipif(
    not _MARKET_DATA_FILE.exists(), reason="requires local WRDS data in data/ (not in git)"
)
def test_example_config_reads_real_data_end_to_end() -> None:
    # Paths in the example config are relative to the repo root, matching how the
    # test suite itself is invoked (uv run pytest from the repo root).
    config = load_data_sources_config(_EXAMPLE_CONFIG)

    market, fundamentals = read_data_sources(config)

    assert isinstance(market, pd.DataFrame)
    assert isinstance(fundamentals, pd.DataFrame)
    assert "security_id" in market.columns
    assert "available_date" in fundamentals.columns
