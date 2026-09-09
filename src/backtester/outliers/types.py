"""Domain objects for cross-sectional outlier detection and treatment.

``OutlierTreatment`` is an abstract base class, not a type alias -- each
concrete treatment knows how to compute its own per-date bounds via
``compute_bounds()``, so callers (``treat.py``) never branch on which
concrete type they're holding.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd

from backtester.stats import MAD_SCALE, cross_sectional_median_mad

_VALID_ACTIONS = frozenset({"winsorize", "truncate"})


@dataclass(frozen=True, kw_only=True)
class OutlierTreatment(ABC):
    """One cross-sectional outlier treatment: how to compute per-date bounds
    for ``column``, and what to do (``action``) with values outside them.
    """

    column: str
    action: str = "winsorize"

    def __post_init__(self) -> None:
        if self.action not in _VALID_ACTIONS:
            raise ValueError(
                f"unknown outlier treatment action {self.action!r}; supported: "
                f"{sorted(_VALID_ACTIONS)}"
            )

    @abstractmethod
    def compute_bounds(
        self, series: pd.Series, dates: pd.Series
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        """Per-date ``(lower, upper, degenerate)`` bounds, broadcast to each row.

        ``degenerate`` marks rows whose date's bounds are undefined (e.g. MAD
        == 0) -- those rows must be left untreated by the caller, never
        silently clipped to a degenerate bound.
        """

    @property
    @abstractmethod
    def method_name(self) -> str: ...


@dataclass(frozen=True, kw_only=True)
class QuantileOutlierTreatment(OutlierTreatment):
    """Cap/null values outside ``[lower_quantile, upper_quantile]``, computed from
    the cross-section of ``column`` on each date independently.
    """

    lower_quantile: float
    upper_quantile: float

    def __post_init__(self) -> None:
        super().__post_init__()
        if not (0.0 <= self.lower_quantile < self.upper_quantile <= 1.0):
            raise ValueError(
                f"lower_quantile ({self.lower_quantile}) must be < upper_quantile "
                f"({self.upper_quantile}), both within [0, 1]"
            )

    def compute_bounds(
        self, series: pd.Series, dates: pd.Series
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        grouped = series.groupby(dates)
        lower = grouped.transform(lambda s: s.quantile(self.lower_quantile))
        upper = grouped.transform(lambda s: s.quantile(self.upper_quantile))
        degenerate = pd.Series(False, index=series.index)
        return lower, upper, degenerate

    @property
    def method_name(self) -> str:
        return "quantile"


@dataclass(frozen=True, kw_only=True)
class MadOutlierTreatment(OutlierTreatment):
    """Cap/null values more than ``multiplier`` robust-scaled MADs from the
    cross-sectional median of ``column``, computed on each date independently.

    A date whose cross-sectional MAD is exactly zero (common with small groups
    or many tied values) is left untreated rather than silently dividing by
    zero -- per the guide, "a silent division by zero should never determine
    the resulting signal."
    """

    multiplier: float

    def __post_init__(self) -> None:
        super().__post_init__()
        if self.multiplier <= 0:
            raise ValueError(f"multiplier must be positive, got {self.multiplier}")

    def compute_bounds(
        self, series: pd.Series, dates: pd.Series
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        median, mad = cross_sectional_median_mad(series, dates)
        degenerate = mad == 0
        scale = MAD_SCALE * mad
        lower = median - self.multiplier * scale
        upper = median + self.multiplier * scale
        return lower, upper, degenerate

    @property
    def method_name(self) -> str:
        return "mad"


@dataclass(frozen=True)
class TreatmentDiagnostic:
    column: str
    method: str
    action: str
    n_input_rows: int
    n_treated_lower: int
    n_treated_upper: int
    #: MAD-only: number of distinct dates skipped because that date's MAD was 0.
    n_degenerate_dates: int


@dataclass(frozen=True)
class OutlierTreatmentReport:
    diagnostics: tuple[TreatmentDiagnostic, ...]