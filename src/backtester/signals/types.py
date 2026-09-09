"""Domain objects for cross-sectional raw score construction.

``ScoreTransform`` is an abstract base class, not a type alias -- each
concrete transform knows how to compute its own per-date raw score via
``compute_raw_score()``, so callers (``scoring.py``) never branch on which
concrete type they're holding.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd

from backtester.stats import MAD_SCALE, cross_sectional_median_mad

_VALID_DIRECTIONS = frozenset({1, -1})


@dataclass(frozen=True, kw_only=True)
class ScoreTransform(ABC):
    """One cross-sectional score transform for ``column``, oriented by
    ``direction`` (must be fixed ex ante -- see the guide's discussion of the
    direction convention, never inferred from what performed best).
    """

    column: str
    direction: int = 1

    def __post_init__(self) -> None:
        if self.direction not in _VALID_DIRECTIONS:
            raise ValueError(f"direction must be 1 or -1, got {self.direction}")

    @abstractmethod
    def compute_raw_score(
        self, series: pd.Series, dates: pd.Series
    ) -> tuple[pd.Series, pd.Series]:
        """Per-date ``(raw_score, degenerate)``.

        ``degenerate`` marks rows whose date's cross-section has zero scale
        (std or MAD == 0) -- those rows must get a null score, never a
        silent division-by-zero result.
        """

    @property
    @abstractmethod
    def method_name(self) -> str: ...


@dataclass(frozen=True, kw_only=True)
class ZScoreTransform(ScoreTransform):
    """Cross-sectional z-score: ``direction * (x - mean) / std``, computed from
    the cross-section of ``column`` on each date independently.

    A date whose cross-sectional standard deviation is exactly zero (all
    securities share the same value that day) is left as null rather than
    silently dividing by zero.
    """

    def compute_raw_score(
        self, series: pd.Series, dates: pd.Series
    ) -> tuple[pd.Series, pd.Series]:
        mean = series.groupby(dates).transform("mean")
        std = series.groupby(dates).transform("std")
        degenerate = std == 0
        raw_score = self.direction * (series - mean) / std
        return raw_score.where(~degenerate), degenerate

    @property
    def method_name(self) -> str:
        return "zscore"


@dataclass(frozen=True, kw_only=True)
class RobustZScoreTransform(ScoreTransform):
    """Cross-sectional robust z-score:
    ``direction * (x - median) / (1.4826 * MAD)``, computed from the
    cross-section of ``column`` on each date independently.

    A date whose cross-sectional MAD is exactly zero is left as null rather
    than silently dividing by zero.
    """

    def compute_raw_score(
        self, series: pd.Series, dates: pd.Series
    ) -> tuple[pd.Series, pd.Series]:
        median, mad = cross_sectional_median_mad(series, dates)
        degenerate = mad == 0
        raw_score = self.direction * (series - median) / (MAD_SCALE * mad)
        return raw_score.where(~degenerate), degenerate

    @property
    def method_name(self) -> str:
        return "robust_zscore"


@dataclass(frozen=True)
class ScoreDiagnostic:
    column: str
    method: str
    direction: int
    n_input_rows: int
    #: Number of distinct dates skipped because std (or MAD) was exactly 0.
    n_degenerate_dates: int


@dataclass(frozen=True)
class RawScoreReport:
    diagnostics: tuple[ScoreDiagnostic, ...]


@dataclass(frozen=True, kw_only=True)
class Exposure(ABC):
    """One column of the guide's exposure matrix B_t (ch. 10) -- how to turn
    ``column`` into one or more numeric regressor columns for a given date's
    cross-section. Each concrete exposure knows how to build its own
    column(s), so ``neutralize.py`` never branches on which concrete type it's
    holding.
    """

    column: str

    @abstractmethod
    def build_columns(self, data: pd.DataFrame) -> dict[str, pd.Series]:
        """One or more ``{name: values}`` regressor columns derived from
        ``data[self.column]``, aligned to ``data``'s index. A value that is
        missing/undefined for a row must come back as NaN (never silently
        dropped or zero-filled) -- ``neutralize_signals`` excludes any row with
        a NaN anywhere in the exposure matrix from that date's regression.
        """

    @property
    @abstractmethod
    def method_name(self) -> str: ...


@dataclass(frozen=True, kw_only=True)
class ContinuousExposure(Exposure):
    """A numeric column used as-is (e.g. beta, log market cap)."""

    def build_columns(self, data: pd.DataFrame) -> dict[str, pd.Series]:
        return {self.column: data[self.column]}

    @property
    def method_name(self) -> str:
        return "continuous"


@dataclass(frozen=True, kw_only=True)
class CategoricalExposure(Exposure):
    """A categorical column (e.g. industry) dummy-encoded per date, one
    category dropped to avoid collinearity with the intercept.

    Which category gets dropped doesn't affect the neutralized signal itself:
    for OLS with an intercept, dropping any single category from a set of
    mutually exclusive dummies spans the same column space regardless of
    choice, so the residual is invariant to it. This drops the
    lexicographically-first category present *that date* (not globally) --
    consistent with every other cross-sectional computation in this codebase
    never pooling categories across dates.
    """

    def build_columns(self, data: pd.DataFrame) -> dict[str, pd.Series]:
        raw = data[self.column]
        dummies = pd.get_dummies(raw, prefix=self.column, drop_first=True, dtype=float)
        is_null = raw.isna()
        for c in dummies.columns:
            dummies.loc[is_null, c] = float("nan")
        return {c: dummies[c] for c in sorted(dummies.columns)}

    @property
    def method_name(self) -> str:
        return "categorical"


@dataclass(frozen=True)
class NeutralizationDiagnostic:
    column: str
    exposure_columns: tuple[str, ...]
    n_input_rows: int
    #: Rows that actually received a neutral score (complete exposures, complete
    #: signal, non-degenerate date).
    n_valid_rows: int
    #: Distinct dates skipped: too few complete-case rows for the exposure
    #: matrix's rank, or the exposure matrix itself was rank-deficient that date.
    n_degenerate_dates: int
    #: Mean cross-sectional regression R^2 across non-degenerate dates -- a
    #: value near 1 means the exposures explain nearly all of the raw signal's
    #: cross-sectional variation (guide's explained-fraction diagnostic).
    mean_r_squared: float | None


@dataclass(frozen=True)
class NeutralizationReport:
    diagnostics: tuple[NeutralizationDiagnostic, ...]


@dataclass(frozen=True)
class FinalSignalDiagnostic:
    column: str
    method: str
    direction: int
    n_input_rows: int
    #: Number of distinct dates skipped because std (or MAD) was exactly 0.
    n_degenerate_dates: int


@dataclass(frozen=True)
class FinalSignalReport:
    diagnostics: tuple[FinalSignalDiagnostic, ...]