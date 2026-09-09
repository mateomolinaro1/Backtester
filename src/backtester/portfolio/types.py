"""Domain objects for direct Pure Alpha portfolio construction (guide ch. 13,
docs/backtesting/12.2_direct_pure_alpha_construction.md's "Recommended
Closed-Form Approach").

``WeightMapping`` mirrors ``ScoreTransform``'s pattern: an abstract base plus
concrete mapping functions, so callers (``construct.py``) never branch on
which concrete type they're holding.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True, kw_only=True)
class WeightMapping(ABC):
    """A signal-to-weight mapping function g: s_final -> raw mapped weight,
    applied element-wise (no cross-sectional dependency -- unlike
    ``ScoreTransform``, this never needs the ``dates`` grouping)."""

    @abstractmethod
    def map(self, signal: pd.Series) -> pd.Series: ...

    @property
    @abstractmethod
    def method_name(self) -> str: ...


@dataclass(frozen=True, kw_only=True)
class LinearWeightMapping(WeightMapping):
    """Identity mapping, g(s) = s. Any constant scaling factor would cancel
    out at the gross-exposure normalization stage, so none is exposed here."""

    def map(self, signal: pd.Series) -> pd.Series:
        return signal

    @property
    def method_name(self) -> str:
        return "linear"


@dataclass(frozen=True, kw_only=True)
class TanhWeightMapping(WeightMapping):
    """Bounded mapping, g(s) = tanh(kappa * s) -- limits the influence of
    extreme signal observations (guide's "Bounded Mapping", ch. 13)."""

    kappa: float = 1.0

    def map(self, signal: pd.Series) -> pd.Series:
        return np.tanh(self.kappa * signal)

    @property
    def method_name(self) -> str:
        return "tanh"


@dataclass(frozen=True)
class PureAlphaReport:
    """Diagnostics for one Pure Alpha construction run. Unlike
    ``NeutralizationReport``/``RawScoreReport``, this isn't a tuple of
    per-column diagnostics -- there is one Pure Alpha portfolio per run, not
    one per signal column.
    """

    signal_column: str
    mapping_method: str
    exposure_columns: tuple[str, ...]
    gross_exposure_target: float
    n_input_rows: int
    #: Rows that received a final pure_alpha weight (complete-case exposures,
    #: non-degenerate date -- mirrors NeutralizationDiagnostic.n_valid_rows).
    n_valid_rows: int
    n_degenerate_dates: int
    #: Worst (max abs, across all non-degenerate dates) net dollar exposure
    #: of the final pure_alpha weights -- should be ~0 up to floating point.
    max_abs_net_exposure: float | None
    #: Worst (max abs, across all configured exposures and dates) dot product
    #: of an exposure column with the final pure_alpha weights -- should be
    #: ~0 up to floating point for every configured exposure (e.g. beta).
    max_abs_projected_exposure: float | None
    #: Worst (max abs, across all non-degenerate dates) deviation of realized
    #: gross exposure (sum of |weights|) from ``gross_exposure_target``.
    max_gross_exposure_error: float | None