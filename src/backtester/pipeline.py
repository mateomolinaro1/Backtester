"""End-to-end backtest pipeline orchestration.

Every module up to this point (cleaning, universe construction, the as-of join,
outlier treatment, signal construction) is a standalone function operating on
whatever DataFrame it's handed -- deliberately, so each has no knowledge of the
others (see ADR-0005/0006/0007/0008). Composing them into the actual
chronological chain the guide describes was explicitly left as "a
pipeline-composition decision" (ADR-0006) for whoever calls them. This module
is that caller.

Stage order (ADR-0011, superseding ADR-0009's order; beta/neutralization added
per ADR-0012; final-signal standardization added per ADR-0013; Pure Alpha
construction and isovol added per ADR-0014/ADR-0015; benchmark/risk-free
calendar alignment split out as its own stage per ADR-0016)::

    read data sources
        -> clean (market, fundamentals independently)
        -> align_benchmark_and_risk_free (benchmark/risk-free reindexed onto
                                           market's own date calendar with a
                                           bounded forward-fill -- ADR-0016,
                                           calendar.py's align_to_calendar)
        -> compute_beta (rolling market beta on the FULL cleaned market panel,
                          before any eligibility restriction -- see below)
        -> build_universe (market only, v1 -- see below)
        -> as_of_join (market_universe + fundamentals_clean -> one daily,
                        eligibility-restricted PIT frame)
        -> treat_outliers (market + fundamentals columns together, one call,
                            on the joined frame)
        -> compute_raw_scores + combine_scores (same, on the same frame)
        -> neutralize (cross-sectional OLS neutralization of already-scored
                        signal columns against configured exposures)
        -> finalize (post-neutralization cross-sectional standardization,
                      producing the final investable signal columns)
        -> construct_pure_alpha (direct, closed-form, dollar- and exposure-
                                  neutral long-short portfolio construction
                                  from a final signal column; no numerical
                                  optimizer -- see ADR-0014)
        -> estimate_portfolio_volatility (historical Xw ex-ante volatility
                                           estimate -- ADR-0015)
        -> apply_isovol (generic sigma*/sigma_hat scaling step, decoupled
                          from how volatility was estimated -- ADR-0015)

Each stage is a method that stores its result(s) as attributes named after
the stage (``market_clean``, ``market_universe``, ``market_fundamentals_joined``,
``treated``, ``scored``, ...), left ``None`` until that stage has run. Stages can
be called one at a time to inspect intermediate state -- per CLAUDE.md, no
two conceptually distinct stages are collapsed into one attribute, even
where V1 makes their values numerically similar. ``run()`` executes the
full chain.

Scope decisions (agreed with the user before implementing):

- **Universe eligibility restricts market only, not fundamentals -- directly.**
  Market rows are inner-joined against the universe membership table before the
  as-of join. Fundamentals rows are cleaned but not independently filtered by
  eligibility; instead, the as-of join is driven from ``market_universe``, so
  only fundamentals data for already-eligible (security_id, date) rows ever
  reaches the joined frame in the first place. This is what fixes ADR-0011's
  bug: unlike ADR-0009's ordering, ``treat_outliers``/``compute_raw_scores`` now
  run *after* this restriction, so fundamentals' own cross-sectional statistics
  (outlier bounds, z-score mean/std) are computed only over U_t, matching the
  guide's theta_t = g({X_j,t : j in U_t}) exactly, for every column regardless
  of source.
- **One outlier-treatment/scoring pass, not two.** ``treat_outliers`` and
  ``compute_raw_scores`` are still fully generic (ADR-0006/0007) -- only the
  call sites changed, from one call per source to one call covering both
  sources' columns on the joined frame, always grouped by the canonical market
  ``date`` column (never configurable to ``available_date`` on this frame --
  see ADR-0011 for why that would silently corrupt the statistics).
- **Cross-source score combination is now possible, not just cross-source data
  presence.** ``market_fundamentals_joined`` existing before scoring means
  ``combine_scores`` can mix a market-derived raw score with a
  fundamentals-derived one in the same ``combine`` config entry -- the
  blocker ADR-0007 flagged is resolved by ADR-0011's reorder.
- **Beta is computed on ``market_clean``, before ``build_universe`` restricts
  to eligible rows** (ADR-0012), then carried forward as an ordinary
  passthrough column through every later stage (inner-joined by
  ``build_universe``, preserved 1:1 by ``as_of_join``). This matches
  ``timeseries.py``'s rationale: a security's rolling beta should reflect its
  actual return history, not develop artificial gaps on dates it happened to
  be temporarily ineligible. Both ``compute_beta`` and ``neutralize`` are
  optional stages -- an absent ``beta``/``neutralization`` config section
  means the respective column/transform never appears, not an error.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pandas as pd

from backtester.asof import DEFAULT_MAX_STALENESS, AsOfJoinReport, as_of_join
from backtester.calendar import CalendarAlignmentReport, align_to_calendar
from backtester.cleaning import CleaningReport, clean_fundamentals, clean_market_data
from backtester.config import (
    BetaConfig,
    DataSourcesConfig,
    FinalSignalConfig,
    IsovolConfig,
    NeutralizationConfig,
    OutlierTreatmentConfig,
    PureAlphaConfig,
    SignalConstructionConfig,
    UniverseConfig,
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
from backtester.data.io import read_benchmark_returns, read_risk_free_returns
from backtester.outliers import OutlierTreatmentReport, treat_outliers
from backtester.portfolio import (
    IsovolReport,
    PureAlphaReport,
    apply_isovol_scaling,
    construct_pure_alpha_portfolio,
)
from backtester.risk import HistoricalVolatilityReport, historical_portfolio_volatility
from backtester.signals import (
    FinalSignalReport,
    NeutralizationReport,
    RawScoreReport,
    combine_scores,
    compute_raw_scores,
    neutralize_signals,
    standardize_final_signal,
)
from backtester.timeseries import RollingBetaReport, rolling_beta
from backtester.universe import UniverseReport, build_universe

#: Canonical market date column (data/schema.py guarantees this name after
#: column mapping). Hardcoded, not configurable, for the joined-frame stages --
#: see ADR-0011.
_DATE_COLUMN = "date"


@dataclasses.dataclass(frozen=True)
class PipelineConfig:
    """Every section of a backtest JSON config file, parsed once."""

    data_sources: DataSourcesConfig
    universe: UniverseConfig
    outlier_treatment: OutlierTreatmentConfig
    signal_construction: SignalConstructionConfig
    beta: BetaConfig | None
    neutralization: NeutralizationConfig
    final_signal: FinalSignalConfig
    pure_alpha: PureAlphaConfig | None
    isovol: IsovolConfig | None


def load_pipeline_config(path: str | Path) -> PipelineConfig:
    """Load every recognized section of a backtest JSON config file.

    Delegates to each section's existing ``load_*_config`` loader rather than
    re-implementing parsing here -- each of those already handles its
    section being absent (empty config = no filters/treatments/scores for
    that stage), so composing them costs a few extra cheap file reads and no
    duplicated logic.
    """
    return PipelineConfig(
        data_sources=load_data_sources_config(path),
        universe=load_universe_config(path),
        outlier_treatment=load_outlier_treatment_config(path),
        signal_construction=load_signal_construction_config(path),
        beta=load_beta_config(path),
        neutralization=load_neutralization_config(path),
        final_signal=load_final_signal_config(path),
        pure_alpha=load_pure_alpha_config(path),
        isovol=load_isovol_config(path),
    )


class PipelineStateError(RuntimeError):
    """Raised when a pipeline stage is run before its prerequisite stage."""


class BacktestPipeline:
    """Stepwise orchestrator chaining the backtester's modules in order.

    Construct via :meth:`from_config`, then either ``run()`` the whole chain
    or call stages individually::

        pipeline = BacktestPipeline.from_config("config/backtest.example.json")
        pipeline.run()
        pipeline.scored          # DataFrame
        pipeline.outlier_report  # OutlierTreatmentReport

        # or step by step, e.g. to inspect state mid-chain:
        pipeline.load_data()
        pipeline.clean()
        pipeline.build_universe()
    """

    def __init__(self, config: PipelineConfig) -> None:
        self.config = config

        self.market_raw: pd.DataFrame | None = None
        self.fundamentals_raw: pd.DataFrame | None = None

        self.market_clean: pd.DataFrame | None = None
        self.market_clean_report: CleaningReport | None = None
        self.fundamentals_clean: pd.DataFrame | None = None
        self.fundamentals_clean_report: CleaningReport | None = None

        self.benchmark_aligned: pd.Series | None = None
        self.benchmark_alignment_report: CalendarAlignmentReport | None = None
        self.risk_free_aligned: pd.Series | None = None
        self.risk_free_alignment_report: CalendarAlignmentReport | None = None

        self.beta_report: RollingBetaReport | None = None

        self.universe: pd.DataFrame | None = None
        self.universe_report: UniverseReport | None = None
        self.market_universe: pd.DataFrame | None = None

        self.market_fundamentals_joined: pd.DataFrame | None = None
        self.as_of_join_report: AsOfJoinReport | None = None

        self.treated: pd.DataFrame | None = None
        self.outlier_report: OutlierTreatmentReport | None = None

        self.scored: pd.DataFrame | None = None
        self.score_report: RawScoreReport | None = None

        self.neutralized: pd.DataFrame | None = None
        self.neutralization_report: NeutralizationReport | None = None

        self.final: pd.DataFrame | None = None
        self.final_signal_report: FinalSignalReport | None = None

        self.pure_alpha: pd.DataFrame | None = None
        self.pure_alpha_report: PureAlphaReport | None = None

        self.portfolio_volatility: pd.Series | None = None
        self.portfolio_volatility_report: HistoricalVolatilityReport | None = None
        self.isovol: pd.DataFrame | None = None
        self.isovol_report: IsovolReport | None = None

    @classmethod
    def from_config(cls, path: str | Path) -> BacktestPipeline:
        return cls(load_pipeline_config(path))

    def run(self) -> BacktestPipeline:
        """Run every stage in order. Returns ``self`` for chaining."""
        self.load_data()
        self.clean()
        self.align_benchmark_and_risk_free()
        self.compute_beta()
        self.build_universe()
        self.join_market_fundamentals()
        self.treat_outliers()
        self.construct_signals()
        self.neutralize()
        self.finalize()
        self.construct_pure_alpha()
        self.estimate_portfolio_volatility()
        self.apply_isovol()
        return self

    def load_data(self) -> None:
        self.market_raw, self.fundamentals_raw = read_data_sources(self.config.data_sources)

    def clean(self) -> None:
        self._require(self.market_raw is not None, "load_data")
        assert self.market_raw is not None
        assert self.fundamentals_raw is not None
        self.market_clean, self.market_clean_report = clean_market_data(self.market_raw)
        self.fundamentals_clean, self.fundamentals_clean_report = clean_fundamentals(
            self.fundamentals_raw
        )

    def align_benchmark_and_risk_free(self) -> None:
        """Align benchmark/risk-free return series onto market's own date
        calendar (ADR-0016; ``calendar.py``'s ``align_to_calendar``).

        A standalone stage, not folded into ``compute_beta``, so a future
        consumer besides beta can reuse ``benchmark_aligned``/
        ``risk_free_aligned`` directly rather than recomputing the same
        alignment itself.

        If ``config.beta`` is absent, this is a no-op: both stay ``None`` --
        same convention as every other optional stage (``config.beta``
        currently owns the only configured benchmark/risk-free paths; a
        future consumer needing this independently of beta would need its
        own config section, not yet built).
        """
        self._require(self.market_clean is not None, "clean")
        assert self.market_clean is not None

        if self.config.beta is None:
            self.benchmark_alignment_report = None
            self.risk_free_alignment_report = None
            return

        benchmark_returns = read_benchmark_returns(
            self.config.beta.benchmark_path,
            level_column=self.config.beta.benchmark_level_column,
            max_ffill=self.config.beta.benchmark_max_ffill,
        )
        risk_free_returns = read_risk_free_returns(
            self.config.beta.risk_free_path,
            rate_column=self.config.beta.risk_free_rate_column,
            max_ffill=self.config.beta.risk_free_max_ffill,
        )

        market_calendar = pd.Index(sorted(self.market_clean[_DATE_COLUMN].unique()))
        self.benchmark_aligned, self.benchmark_alignment_report = align_to_calendar(
            benchmark_returns,
            market_calendar,
            max_ffill=self.config.beta.benchmark_calendar_max_ffill,
        )
        self.risk_free_aligned, self.risk_free_alignment_report = align_to_calendar(
            risk_free_returns,
            market_calendar,
            max_ffill=self.config.beta.risk_free_calendar_max_ffill,
        )

    def compute_beta(self) -> None:
        """Rolling market beta on the full cleaned market panel (before
        ``build_universe`` restricts to eligible rows -- see module docstring).

        If ``config.beta`` is absent, this is a no-op: ``market_clean`` gets no
        ``beta`` column and ``beta_report`` stays ``None``, matching config.py's
        documented "omitting the section means beta is not computed" contract.
        Consumes ``benchmark_aligned``/``risk_free_aligned`` (ADR-0016) rather
        than reading and aligning them itself.
        """
        self._require(self.market_clean is not None, "clean")
        assert self.market_clean is not None

        if self.config.beta is None:
            self.beta_report = None
            return

        self._require(
            self.benchmark_aligned is not None, "align_benchmark_and_risk_free"
        )
        assert self.benchmark_aligned is not None
        assert self.risk_free_aligned is not None

        beta, self.beta_report = rolling_beta(
            self.market_clean,
            self.benchmark_aligned,
            self.risk_free_aligned,
            window=self.config.beta.window,
            min_periods=self.config.beta.min_periods,
        )
        self.market_clean = self.market_clean.assign(beta=beta)

    def build_universe(self) -> None:
        self._require(self.market_clean is not None, "clean")
        assert self.market_clean is not None
        self.universe, self.universe_report = build_universe(
            self.market_clean, self.config.universe.filters
        )
        self.market_universe = self.market_clean.merge(
            self.universe, on=["security_id", "date"], how="inner"
        )

    def join_market_fundamentals(
        self, *, max_staleness: pd.Timedelta | None = DEFAULT_MAX_STALENESS
    ) -> None:
        self._require(self.market_universe is not None, "build_universe")
        self._require(self.fundamentals_clean is not None, "clean")
        assert self.market_universe is not None
        assert self.fundamentals_clean is not None

        self.market_fundamentals_joined, self.as_of_join_report = as_of_join(
            self.market_universe, self.fundamentals_clean, max_staleness=max_staleness
        )

    def treat_outliers(self) -> None:
        self._require(self.market_fundamentals_joined is not None, "join_market_fundamentals")
        assert self.market_fundamentals_joined is not None

        self.treated, self.outlier_report = treat_outliers(
            self.market_fundamentals_joined,
            self.config.outlier_treatment.treatments,
            date_column=_DATE_COLUMN,
        )

    def construct_signals(self) -> None:
        self._require(self.treated is not None, "treat_outliers")
        assert self.treated is not None

        self.scored, self.score_report = compute_raw_scores(
            self.treated, self.config.signal_construction.scores, date_column=_DATE_COLUMN
        )
        if self.config.signal_construction.combination is not None:
            combination = self.config.signal_construction.combination
            self.scored = combine_scores(
                self.scored, combination.columns, output_column=combination.output_column
            )

    def neutralize(self) -> None:
        """Cross-sectional OLS neutralization of already-scored signal columns.

        Always runs, even with an empty ``neutralization`` config section --
        consistent with ``treat_outliers``/``construct_signals``, an empty
        ``signal_columns``/``exposures`` config degenerates to a no-op copy
        rather than being skipped outright. An exposure referencing a column
        that was never computed (e.g. ``beta`` with no ``beta`` config section)
        surfaces as ``neutralize_signals``'s own "unknown column" error.
        """
        self._require(self.scored is not None, "construct_signals")
        assert self.scored is not None

        self.neutralized, self.neutralization_report = neutralize_signals(
            self.scored,
            self.config.neutralization.signal_columns,
            self.config.neutralization.exposures,
            date_column=_DATE_COLUMN,
        )

    def finalize(self) -> None:
        """Post-neutralization cross-sectional standardization (guide ch. 11's
        standardization sub-section; ADR-0013).

        Always runs, even with an empty ``final_signal`` config section --
        same "empty config degenerates to a no-op copy" convention as every
        other optional stage. A ``standardizations`` entry referencing a
        column that doesn't exist (e.g. neutralization was never configured
        for it) surfaces as ``standardize_final_signal``'s own "unknown
        column" error.
        """
        self._require(self.neutralized is not None, "neutralize")
        assert self.neutralized is not None

        self.final, self.final_signal_report = standardize_final_signal(
            self.neutralized,
            self.config.final_signal.standardizations,
            date_column=_DATE_COLUMN,
        )

    def construct_pure_alpha(self) -> None:
        """Direct, closed-form Pure Alpha long-short portfolio construction
        (ADR-0014; docs/backtesting/12.2_direct_pure_alpha_construction.md).

        If ``config.pure_alpha`` is absent, this is a no-op: ``pure_alpha``
        stays ``None`` and ``pure_alpha_report`` stays ``None`` -- same
        "None means the whole stage is skipped" convention as
        ``compute_beta``. Produces the pre-isovol structural Pure Alpha
        portfolio; ``apply_isovol`` risk-scales it afterward.
        """
        self._require(self.final is not None, "finalize")
        assert self.final is not None

        if self.config.pure_alpha is None:
            self.pure_alpha_report = None
            return

        self.pure_alpha, self.pure_alpha_report = construct_pure_alpha_portfolio(
            self.final,
            self.config.pure_alpha.signal_column,
            self.config.pure_alpha.mapping,
            self.config.pure_alpha.exposures,
            gross_exposure=self.config.pure_alpha.gross_exposure,
            date_column=_DATE_COLUMN,
        )

    def estimate_portfolio_volatility(self) -> None:
        """Historical ex-ante Pure Alpha portfolio volatility via the ``Xw``
        shortcut (ADR-0015;
        docs/backtesting/12.3_historical_portfolio_volatility_xw.md).

        If ``config.isovol`` is absent, this is a no-op: ``portfolio_volatility``/
        ``portfolio_volatility_report`` stay ``None``, same "None means the
        whole stage is skipped" convention as ``compute_beta``/
        ``construct_pure_alpha``. Checked against ``self.final`` (not
        ``construct_pure_alpha``'s own state, which is itself ambiguous
        between "skipped" and "not yet run") -- same pattern
        ``construct_pure_alpha`` itself uses for ``compute_beta``.
        """
        self._require(self.final is not None, "finalize")

        if self.config.isovol is None:
            self.portfolio_volatility_report = None
            return

        if self.config.pure_alpha is None:
            raise ValueError(
                "config.isovol is present but config.pure_alpha is absent; isovol has no "
                "Pure Alpha portfolio to estimate risk for"
            )
        assert self.pure_alpha is not None
        assert self.market_clean is not None

        weight_column = f"{self.config.pure_alpha.signal_column}_pure_alpha"
        self.portfolio_volatility, self.portfolio_volatility_report = (
            historical_portfolio_volatility(
                self.market_clean,
                self.pure_alpha,
                weight_column,
                window=self.config.isovol.window,
                min_periods=self.config.isovol.min_periods,
                date_column=_DATE_COLUMN,
            )
        )

    def apply_isovol(self) -> None:
        """Generic isovol volatility-targeting scaling (ADR-0015;
        docs/backtesting/12.3_isovol.md), consuming whatever
        ``estimate_portfolio_volatility`` produced without knowing how it was
        estimated -- a future non-historical estimator would only change
        that stage, not this one.

        If ``config.isovol`` is absent, this is a no-op: ``isovol``/
        ``isovol_report`` stay ``None``.
        """
        self._require(self.final is not None, "finalize")

        if self.config.isovol is None:
            self.isovol_report = None
            return

        self._require(self.portfolio_volatility is not None, "estimate_portfolio_volatility")
        assert self.pure_alpha is not None
        assert self.portfolio_volatility is not None
        assert self.config.pure_alpha is not None

        weight_column = f"{self.config.pure_alpha.signal_column}_pure_alpha"
        self.isovol, self.isovol_report = apply_isovol_scaling(
            self.pure_alpha,
            weight_column,
            self.portfolio_volatility,
            target_volatility_annualized=self.config.isovol.target_volatility_annualized,
            periods_per_year=self.config.isovol.periods_per_year,
            max_leverage=self.config.isovol.max_leverage,
            date_column=_DATE_COLUMN,
        )

    @staticmethod
    def _require(condition: bool, prerequisite_stage: str) -> None:
        if not condition:
            raise PipelineStateError(f"call {prerequisite_stage}() before this stage")