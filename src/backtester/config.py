"""JSON-driven configuration.

Today this only covers the ``data_sources`` section (where each data source's
file lives and how to map its columns to this backtester's canonical schema --
see data/schema.py). As more modules are built (universe, signal, portfolio,
...), each gets its own top-level section and its own loader here, following
the same pattern: parse JSON -> validate -> typed config object.

``data_sources`` supports two shapes:

- Separate files -- a ``"market"`` and a ``"fundamentals"`` entry, each with
  its own ``"path"``.
- One combined/stacked file -- a ``"combined"`` entry with a single
  ``"path"``, a ``"dataset_column"`` naming the discriminator column, and
  ``"market"``/``"fundamentals"`` sub-entries carrying each block's
  ``"dataset_value"`` (see data/combined.py for the splitting mechanism).

If both shapes are present, ``"combined"`` wins and a warning is raised
naming what got ignored (see ADR-0004).

A data source's column mapping is specified in the config either by naming
one of the built-in presets (``"preset": "wrds"``) or by supplying a full
custom mapping inline (``"columns": {...}``, every canonical field required
-- see ADR-0003 for why partial overrides aren't supported).

The optional ``universe`` section lists eligibility filters applied to the
cleaned market data (see universe/build.py and ADR-0005), e.g.::

    "universe": {
        "filters": [
            {"column": "exchcd", "operator": "in", "value": [1, 2, 3]},
            {"column": "price", "operator": ">=", "value": 5.0}
        ]
    }

Omitting ``universe`` entirely means no filters -- the caller's data source is
already the intended universe.

The optional ``outlier_treatment`` section lists cross-sectional treatments
(see outliers/treat.py and ADR-0006), applied by the pipeline to the joined
market+fundamentals frame (ADR-0011) -- one flat list, not grouped by source,
e.g.::

    "outlier_treatment": {
        "treatments": [
            {"column": "return", "method": "quantile",
             "lower_quantile": 0.01, "upper_quantile": 0.99, "action": "winsorize"},
            {"column": "bm", "method": "mad", "multiplier": 3.0, "action": "truncate"}
        ]
    }

There is no ``date_column`` option: the pipeline always groups by the
canonical market date column (``"date"``) once market and fundamentals are
joined (ADR-0011) -- grouping by fundamentals' own ``available_date`` on the
joined (daily) frame would silently pool a stale value once per day it stayed
matched, not once per security, corrupting the cross-sectional statistics.
Omitting the section means no treatments.

The optional ``signal_construction`` section lists raw-score transforms and an
optional equal-weighted combination (see signals/scoring.py,
signals/combine.py, and ADR-0007), applied the same way -- one flat list, no
``date_column``, same ADR-0011 rationale, e.g.::

    "signal_construction": {
        "scores": [
            {"column": "return_treated", "method": "zscore", "direction": 1},
            {"column": "bm_treated", "method": "robust_zscore", "direction": -1}
        ],
        "combine": {"columns": ["return_treated_raw_score", "bm_treated_raw_score"]}
    }

Because market and fundamentals scores now live in one list on one joined
frame, ``combine`` can mix a market-derived score with a fundamentals-derived
one (ADR-0011 removed the join-timing blocker ADR-0007 flagged).

The optional ``beta`` section configures rolling market-beta estimation (see
timeseries.py and ADR-0012), needed as an exposure for signal neutralization::

    "beta": {
        "benchmark_path": "data/russell_returns.parquet",
        "benchmark_level_column": "Russell 1000",
        "benchmark_max_ffill": 5,
        "benchmark_calendar_max_ffill": 5,
        "risk_free_path": "data/risk_free_returns.parquet",
        "risk_free_rate_column": "rf_returns",
        "risk_free_max_ffill": 5,
        "risk_free_calendar_max_ffill": 5,
        "window": 252,
        "min_periods": 126
    }

Only ``benchmark_path``/``risk_free_path`` are required; the rest default to
the values shown. ``*_max_ffill`` bounds how many consecutive missing rows
``read_benchmark_returns``/``read_risk_free_returns`` will forward-fill before
leaving a gap as NaN (see ADR-0012); set to ``null``/``0`` to disable filling
for that source. ``*_calendar_max_ffill`` is a second, independent fill stage
(see timeseries.py's ``rolling_beta`` and ADR-0015's addendum) against
*market's own date calendar* -- a date entirely absent as a row in the
benchmark/risk-free source (not merely null) survives ``*_max_ffill``
untouched, since that fill only ever sees rows the source actually has;
``*_calendar_max_ffill`` reindexes onto market's dates first, turning "row
doesn't exist" into "row exists and is null," which can then be filled.
Omitting the section entirely means beta is not computed -- the pipeline's
``beta`` column never appears, and any neutralization exposure
referencing it will fail with a clear "unknown column" error.

The optional ``neutralization`` section lists which already-scored signal
column(s) to neutralize against which exposures (see signals/neutralize.py
and ADR-0012), applied on the joined, treated, scored frame::

    "neutralization": {
        "signal_columns": ["composite_raw_score"],
        "exposures": [
            {"type": "continuous", "column": "beta"},
            {"type": "categorical", "column": "gsector"}
        ]
    }

Omitting the section means no neutralization -- signal columns pass through
unneutralized.

The optional ``final_signal`` section lists which column(s) to standardize
into the final investable signal (see signals/finalize.py and ADR-0013 --
"Final Signal Construction" ch. 11's standardization sub-section only;
combination/smoothing/turnover-awareness/confidence-weighting are deferred).
Same transform shape as ``signal_construction.scores`` (``zscore``/
``robust_zscore``, optional ``direction``, default 1 -- there's no economic
reason to re-flip a signal that's already oriented from raw-score
construction, but it stays technically overridable), applied on the
neutralized frame::

    "final_signal": {
        "standardizations": [
            {"column": "return_treated_raw_score_neutral", "method": "robust_zscore"}
        ]
    }

The column list is independent of ``neutralization.signal_columns`` -- a
signal that skipped neutralization can still be standardized directly.
Omitting the section means no post-neutralization standardization -- the
neutralized signal columns pass through as the final ones.

The optional ``pure_alpha`` section configures direct Pure Alpha long-short
portfolio construction (see portfolio/construct.py and ADR-0014 --
docs/backtesting/12.2_direct_pure_alpha_construction.md's "Recommended
Closed-Form Approach")::

    "pure_alpha": {
        "signal_column": "return_treated_raw_score_neutral_final",
        "mapping": {"method": "tanh", "kappa": 1.0},
        "exposures": [
            {"type": "continuous", "column": "beta"}
        ],
        "gross_exposure": 2.0
    }

``mapping.method`` is ``"linear"`` (identity) or ``"tanh"`` (``kappa``
defaults to 1.0, ignored for ``"linear"``). ``exposures`` uses the same
shape as ``neutralization.exposures``. Omitting the section entirely means
no Pure Alpha portfolio is constructed -- unlike ``neutralization``/
``final_signal``, there's no sensible "empty means no-op" default here since
``signal_column`` is always required once this stage runs at all.

The optional ``isovol`` section configures Pure Alpha volatility-targeting
(see risk/historical.py + portfolio/isovol.py and ADR-0015 --
docs/backtesting/12.3_historical_portfolio_volatility_xw.md's ``Xw`` ex-ante
volatility estimator, feeding docs/backtesting/12.3_isovol.md's generic
scaling step)::

    "isovol": {
        "target_volatility_annualized": 0.10,
        "periods_per_year": null,
        "max_leverage": 4.0,
        "window": 252,
        "min_periods": 126
    }

``periods_per_year: null`` (or omitted) auto-detects from the market panel's
own date frequency (median distinct trading dates per calendar year) rather
than assuming 252. ``max_leverage: null`` (or omitted) means uncapped.
``window``/``min_periods`` bound the historical lookback the ``Xw``
estimator uses -- independent of ``beta``'s own window (a deliberately
separate risk-estimation choice, not assumed to match). Omitting the section
entirely means no isovol scaling -- the Pure Alpha weights are the final
ones, requiring ``pure_alpha`` to be present too (isovol has nothing to
scale otherwise).
"""

from __future__ import annotations

import dataclasses
import json
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

import pandas as pd

from backtester.data.combined import read_combined_data
from backtester.data.io import read_fundamentals, read_market_data
from backtester.data.schema import (
    FUNDAMENTALS_COLUMN_PRESETS,
    MARKET_COLUMN_PRESETS,
    FundamentalsColumnMapping,
    MarketColumnMapping,
)
from backtester.exceptions import AmbiguousDataSourceConfigWarning
from backtester.outliers.types import (
    MadOutlierTreatment,
    OutlierTreatment,
    QuantileOutlierTreatment,
)
from backtester.portfolio.types import LinearWeightMapping, TanhWeightMapping, WeightMapping
from backtester.signals.types import (
    CategoricalExposure,
    ContinuousExposure,
    Exposure,
    RobustZScoreTransform,
    ScoreTransform,
    ZScoreTransform,
)
from backtester.universe.types import EligibilityFilter

if TYPE_CHECKING:
    from _typeshed import DataclassInstance

_T = TypeVar("_T", bound="DataclassInstance")

# JSON keys that don't match a canonical field name 1:1 because the field name had to
# avoid a Python reserved word (the "return" column -> dataclass field `return_`).
_JSON_FIELD_ALIASES: dict[str, str] = {"return": "return_"}

_DEFAULT_DATASET_COLUMN = "dataset"


@dataclasses.dataclass(frozen=True)
class SeparateDataSourcesConfig:
    market_path: Path
    market_columns: MarketColumnMapping
    fundamentals_path: Path
    fundamentals_columns: FundamentalsColumnMapping


@dataclasses.dataclass(frozen=True)
class CombinedDataSourcesConfig:
    path: Path
    dataset_column: str
    market_columns: MarketColumnMapping
    market_dataset_value: str
    fundamentals_columns: FundamentalsColumnMapping
    fundamentals_dataset_value: str


DataSourcesConfig = SeparateDataSourcesConfig | CombinedDataSourcesConfig


@dataclasses.dataclass(frozen=True)
class UniverseConfig:
    filters: tuple[EligibilityFilter, ...]


def load_universe_config(path: str | Path) -> UniverseConfig:
    """Load the optional ``universe`` section of a backtest JSON config file.

    Absent entirely, or present with an empty ``filters`` list, both mean "no
    filters" -- the caller's data source is already the intended universe.
    """
    raw = json.loads(Path(path).read_text())
    universe_section = raw.get("universe") or {}
    filters_json = universe_section.get("filters", [])

    filters = tuple(
        EligibilityFilter(
            column=_require(f, "column", context="universe filter"),
            operator=_require(f, "operator", context="universe filter"),
            value=f.get("value"),
        )
        for f in filters_json
    )
    return UniverseConfig(filters=filters)


@dataclasses.dataclass(frozen=True)
class OutlierTreatmentConfig:
    treatments: tuple[OutlierTreatment, ...]


def load_outlier_treatment_config(path: str | Path) -> OutlierTreatmentConfig:
    """Load the optional ``outlier_treatment`` section of a backtest JSON config file.

    One flat list applied to the joined market+fundamentals frame (ADR-0011) --
    the pipeline always groups by the canonical market date column, so there is no
    per-treatment ``date_column`` to configure. Omitting the section means "no
    treatments" -- data passes through untouched.
    """
    raw = json.loads(Path(path).read_text())
    section = raw.get("outlier_treatment") or {}
    treatments = tuple(_outlier_treatment_from_json(t) for t in section.get("treatments", []))
    return OutlierTreatmentConfig(treatments=treatments)


def _outlier_treatment_from_json(entry: dict[str, Any]) -> OutlierTreatment:
    column = _require(entry, "column", context="outlier treatment")
    method = _require(entry, "method", context="outlier treatment")
    action = entry.get("action", "winsorize")

    if method == "quantile":
        return QuantileOutlierTreatment(
            column=column,
            lower_quantile=_require(entry, "lower_quantile", context="quantile outlier treatment"),
            upper_quantile=_require(entry, "upper_quantile", context="quantile outlier treatment"),
            action=action,
        )
    if method == "mad":
        return MadOutlierTreatment(
            column=column,
            multiplier=_require(entry, "multiplier", context="mad outlier treatment"),
            action=action,
        )
    raise ValueError(
        f"unknown outlier treatment method {method!r} for column {column!r}; supported: "
        "['quantile', 'mad']"
    )


@dataclasses.dataclass(frozen=True)
class ScoreCombinationConfig:
    columns: tuple[str, ...]
    output_column: str = "composite_raw_score"


@dataclasses.dataclass(frozen=True)
class SignalConstructionConfig:
    scores: tuple[ScoreTransform, ...]
    combination: ScoreCombinationConfig | None = None


def load_signal_construction_config(path: str | Path) -> SignalConstructionConfig:
    """Load the optional ``signal_construction`` section of a backtest JSON config file.

    One flat list applied to the joined market+fundamentals frame (ADR-0011) -- same
    rationale as ``load_outlier_treatment_config``: no per-score ``date_column``, since
    the pipeline always groups by the canonical market date column. Omitting the
    section means "no scores."
    """
    raw = json.loads(Path(path).read_text())
    section = raw.get("signal_construction") or {}

    scores = tuple(_score_transform_from_json(s) for s in section.get("scores", []))

    combine_json = section.get("combine")
    combination = None
    if combine_json is not None:
        combination = ScoreCombinationConfig(
            columns=tuple(_require(combine_json, "columns", context="score combination")),
            output_column=combine_json.get("output_column", "composite_raw_score"),
        )

    return SignalConstructionConfig(scores=scores, combination=combination)


def _score_transform_from_json(entry: dict[str, Any]) -> ScoreTransform:
    column = _require(entry, "column", context="score transform")
    method = _require(entry, "method", context="score transform")
    direction = entry.get("direction", 1)

    if method == "zscore":
        return ZScoreTransform(column=column, direction=direction)
    if method == "robust_zscore":
        return RobustZScoreTransform(column=column, direction=direction)
    raise ValueError(
        f"unknown score transform method {method!r} for column {column!r}; supported: "
        "['zscore', 'robust_zscore']"
    )


@dataclasses.dataclass(frozen=True)
class BetaConfig:
    benchmark_path: Path
    benchmark_level_column: str
    benchmark_max_ffill: int | None
    #: Distinct from benchmark_max_ffill: fills gaps against MARKET's own date
    #: calendar (ADR-0015 addendum), not gaps within the benchmark source's
    #: own native index (which benchmark_max_ffill already handles).
    benchmark_calendar_max_ffill: int | None
    risk_free_path: Path
    risk_free_rate_column: str
    risk_free_max_ffill: int | None
    risk_free_calendar_max_ffill: int | None
    window: int
    min_periods: int


def load_beta_config(path: str | Path) -> BetaConfig | None:
    """Load the optional ``beta`` section of a backtest JSON config file.

    Absent entirely means beta is not computed at all -- returns ``None``,
    distinct from a present-but-empty section (which isn't a valid shape here,
    since ``benchmark_path``/``risk_free_path`` are always required once the
    section exists).
    """
    raw = json.loads(Path(path).read_text())
    section = raw.get("beta")
    if section is None:
        return None

    return BetaConfig(
        benchmark_path=Path(_require(section, "benchmark_path", context="beta")),
        benchmark_level_column=section.get("benchmark_level_column", "Russell 1000"),
        benchmark_max_ffill=section.get("benchmark_max_ffill", 5),
        benchmark_calendar_max_ffill=section.get("benchmark_calendar_max_ffill", 5),
        risk_free_path=Path(_require(section, "risk_free_path", context="beta")),
        risk_free_rate_column=section.get("risk_free_rate_column", "rf_returns"),
        risk_free_max_ffill=section.get("risk_free_max_ffill", 5),
        risk_free_calendar_max_ffill=section.get("risk_free_calendar_max_ffill", 5),
        window=section.get("window", 252),
        min_periods=section.get("min_periods", 126),
    )


@dataclasses.dataclass(frozen=True)
class NeutralizationConfig:
    signal_columns: tuple[str, ...]
    exposures: tuple[Exposure, ...]


def load_neutralization_config(path: str | Path) -> NeutralizationConfig:
    """Load the optional ``neutralization`` section of a backtest JSON config file.

    Omitting the section, or leaving ``signal_columns``/``exposures`` empty,
    means no neutralization -- signal columns pass through unmodified.
    """
    raw = json.loads(Path(path).read_text())
    section = raw.get("neutralization") or {}

    signal_columns = tuple(section.get("signal_columns", []))
    exposures = tuple(_exposure_from_json(e) for e in section.get("exposures", []))
    return NeutralizationConfig(signal_columns=signal_columns, exposures=exposures)


def _exposure_from_json(entry: dict[str, Any]) -> Exposure:
    column = _require(entry, "column", context="exposure")
    exposure_type = _require(entry, "type", context="exposure")

    if exposure_type == "continuous":
        return ContinuousExposure(column=column)
    if exposure_type == "categorical":
        return CategoricalExposure(column=column)
    raise ValueError(
        f"unknown exposure type {exposure_type!r} for column {column!r}; supported: "
        "['continuous', 'categorical']"
    )


@dataclasses.dataclass(frozen=True)
class FinalSignalConfig:
    standardizations: tuple[ScoreTransform, ...]


def load_final_signal_config(path: str | Path) -> FinalSignalConfig:
    """Load the optional ``final_signal`` section of a backtest JSON config file.

    Omitting the section, or leaving ``standardizations`` empty, means no
    post-neutralization standardization -- the neutralized signal columns
    pass through as the final ones. Reuses ``_score_transform_from_json``
    (same ``zscore``/``robust_zscore``/``direction`` shape as
    ``signal_construction.scores``) since the underlying math is identical --
    only the pipeline stage and output suffix differ (see ADR-0013).
    """
    raw = json.loads(Path(path).read_text())
    section = raw.get("final_signal") or {}

    standardizations = tuple(
        _score_transform_from_json(s) for s in section.get("standardizations", [])
    )
    return FinalSignalConfig(standardizations=standardizations)


@dataclasses.dataclass(frozen=True)
class PureAlphaConfig:
    signal_column: str
    mapping: WeightMapping
    exposures: tuple[Exposure, ...]
    gross_exposure: float


def load_pure_alpha_config(path: str | Path) -> PureAlphaConfig | None:
    """Load the optional ``pure_alpha`` section of a backtest JSON config file.

    Absent entirely means no Pure Alpha portfolio is constructed -- returns
    ``None``, same "None means the whole stage is skipped" convention as
    ``load_beta_config`` (not the "empty list means no-op" convention used by
    ``neutralization``/``final_signal``, since ``signal_column`` has no
    sensible default once this section exists at all).
    """
    raw = json.loads(Path(path).read_text())
    section = raw.get("pure_alpha")
    if section is None:
        return None

    return PureAlphaConfig(
        signal_column=_require(section, "signal_column", context="pure_alpha"),
        mapping=_weight_mapping_from_json(_require(section, "mapping", context="pure_alpha")),
        exposures=tuple(_exposure_from_json(e) for e in section.get("exposures", [])),
        gross_exposure=section.get("gross_exposure", 2.0),
    )


def _weight_mapping_from_json(entry: dict[str, Any]) -> WeightMapping:
    method = _require(entry, "method", context="weight mapping")

    if method == "linear":
        return LinearWeightMapping()
    if method == "tanh":
        return TanhWeightMapping(kappa=entry.get("kappa", 1.0))
    raise ValueError(
        f"unknown weight mapping method {method!r}; supported: ['linear', 'tanh']"
    )


@dataclasses.dataclass(frozen=True)
class IsovolConfig:
    target_volatility_annualized: float
    #: None means auto-detect from the market panel's own date frequency
    #: (see portfolio/isovol.py's infer_periods_per_year).
    periods_per_year: float | None
    #: None means uncapped.
    max_leverage: float | None
    window: int
    min_periods: int


def load_isovol_config(path: str | Path) -> IsovolConfig | None:
    """Load the optional ``isovol`` section of a backtest JSON config file.

    Absent entirely means no isovol scaling -- returns ``None``, same
    "None means the whole stage is skipped" convention as ``load_beta_config``/
    ``load_pure_alpha_config`` (``target_volatility_annualized`` has no
    sensible default once this section exists at all).
    """
    raw = json.loads(Path(path).read_text())
    section = raw.get("isovol")
    if section is None:
        return None

    return IsovolConfig(
        target_volatility_annualized=_require(
            section, "target_volatility_annualized", context="isovol"
        ),
        periods_per_year=section.get("periods_per_year"),
        max_leverage=section.get("max_leverage"),
        window=section.get("window", 252),
        min_periods=section.get("min_periods", 126),
    )


def load_data_sources_config(path: str | Path) -> DataSourcesConfig:
    """Load the ``data_sources`` section of a backtest JSON config file."""
    raw = json.loads(Path(path).read_text())
    try:
        data_sources = raw["data_sources"]
    except KeyError as exc:
        raise ValueError(f"{path} is missing required config key: {exc}") from exc

    combined_entry = data_sources.get("combined")
    market_entry = data_sources.get("market")
    fundamentals_entry = data_sources.get("fundamentals")

    if combined_entry is not None:
        ignored = [
            name
            for name, entry in (("market", market_entry), ("fundamentals", fundamentals_entry))
            if entry is not None
        ]
        if ignored:
            warnings.warn(
                f"{path}: data_sources specifies 'combined' as well as {ignored}; "
                f"'combined' takes precedence and {ignored} will be ignored. Remove the "
                "unused key(s) to silence this warning.",
                AmbiguousDataSourceConfigWarning,
                stacklevel=2,
            )
        return _load_combined(combined_entry)

    if market_entry is not None and fundamentals_entry is not None:
        return _load_separate(market_entry, fundamentals_entry)

    raise ValueError(
        f"{path}: data_sources must specify either 'combined', or both 'market' and "
        "'fundamentals'"
    )


def read_data_sources(config: DataSourcesConfig) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return ``(market, fundamentals)`` DataFrames for either config shape."""
    if isinstance(config, CombinedDataSourcesConfig):
        return read_combined_data(
            config.path,
            dataset_column=config.dataset_column,
            market_columns=config.market_columns,
            market_dataset_value=config.market_dataset_value,
            fundamentals_columns=config.fundamentals_columns,
            fundamentals_dataset_value=config.fundamentals_dataset_value,
        )
    return (
        read_market_data(config.market_path, columns=config.market_columns),
        read_fundamentals(config.fundamentals_path, columns=config.fundamentals_columns),
    )


def _load_separate(
    market_entry: dict[str, Any], fundamentals_entry: dict[str, Any]
) -> SeparateDataSourcesConfig:
    return SeparateDataSourcesConfig(
        market_path=Path(_require(market_entry, "path", context="market data source")),
        market_columns=_resolve_column_mapping(
            market_entry, MARKET_COLUMN_PRESETS, MarketColumnMapping, source_name="market"
        ),
        fundamentals_path=Path(
            _require(fundamentals_entry, "path", context="fundamentals data source")
        ),
        fundamentals_columns=_resolve_column_mapping(
            fundamentals_entry,
            FUNDAMENTALS_COLUMN_PRESETS,
            FundamentalsColumnMapping,
            source_name="fundamentals",
        ),
    )


def _load_combined(entry: dict[str, Any]) -> CombinedDataSourcesConfig:
    market_entry = _require(entry, "market", context="combined data source")
    fundamentals_entry = _require(entry, "fundamentals", context="combined data source")

    return CombinedDataSourcesConfig(
        path=Path(_require(entry, "path", context="combined data source")),
        dataset_column=entry.get("dataset_column", _DEFAULT_DATASET_COLUMN),
        market_columns=_resolve_column_mapping(
            market_entry, MARKET_COLUMN_PRESETS, MarketColumnMapping, source_name="combined market"
        ),
        market_dataset_value=market_entry.get("dataset_value", "market"),
        fundamentals_columns=_resolve_column_mapping(
            fundamentals_entry,
            FUNDAMENTALS_COLUMN_PRESETS,
            FundamentalsColumnMapping,
            source_name="combined fundamentals",
        ),
        fundamentals_dataset_value=fundamentals_entry.get("dataset_value", "fundamentals"),
    )


def _require(entry: dict[str, Any], key: str, *, context: str) -> Any:
    if key not in entry:
        raise ValueError(f"{context} config is missing required key: {key!r}")
    return entry[key]


def _resolve_column_mapping(  # noqa: UP047 -- bound TypeVar needs TYPE_CHECKING-only import
    entry: dict[str, Any],
    presets: dict[str, _T],
    mapping_cls: type[_T],
    *,
    source_name: str,
) -> _T:
    has_preset = "preset" in entry
    has_columns = "columns" in entry
    if has_preset == has_columns:
        raise ValueError(
            f"{source_name} data source config must specify exactly one of 'preset' or "
            "'columns'"
        )

    if has_preset:
        preset_name = entry["preset"]
        if preset_name not in presets:
            raise ValueError(
                f"unknown {source_name} preset {preset_name!r}; available presets: "
                f"{sorted(presets)}"
            )
        return presets[preset_name]

    return _column_mapping_from_json(entry["columns"], mapping_cls, source_name=source_name)


def _column_mapping_from_json(  # noqa: UP047 -- bound TypeVar needs TYPE_CHECKING-only import
    columns_json: dict[str, str], mapping_cls: type[_T], *, source_name: str
) -> _T:
    field_names = {f.name for f in dataclasses.fields(mapping_cls)}
    kwargs = {_JSON_FIELD_ALIASES.get(key, key): value for key, value in columns_json.items()}

    missing = field_names - kwargs.keys()
    unknown = kwargs.keys() - field_names
    if missing or unknown:
        raise ValueError(
            f"{source_name} custom column mapping is invalid "
            f"(missing fields: {sorted(missing)}, unknown fields: {sorted(unknown)})"
        )
    return mapping_cls(**kwargs)
