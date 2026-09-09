"""Domain objects for eligibility-based universe construction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

#: Filters requiring no `value` -- everything else must supply one.
_NULLARY_OPERATORS = frozenset({"is_null", "is_not_null"})

#: The complete set of supported filter operators.
OPERATORS = _NULLARY_OPERATORS | frozenset({"==", "!=", ">", ">=", "<", "<=", "in", "not_in"})


@dataclass(frozen=True)
class EligibilityFilter:
    """One eligibility condition: ``column`` (must exist in the target DataFrame)
    ``operator`` ``value``, e.g. ``price >= 5.0`` or ``exchcd in [1, 2, 3]``.
    """

    column: str
    operator: str
    value: Any = None

    def __post_init__(self) -> None:
        if self.operator not in OPERATORS:
            raise ValueError(
                f"unknown eligibility filter operator {self.operator!r}; supported: "
                f"{sorted(OPERATORS)}"
            )
        if self.operator not in _NULLARY_OPERATORS and self.value is None:
            raise ValueError(
                f"eligibility filter with operator {self.operator!r} requires a 'value'"
            )


@dataclass(frozen=True)
class FilterDiagnostic:
    """How many rows one filter removed, applied in sequence after prior filters."""

    column: str
    operator: str
    value: Any
    n_rows_before: int
    n_rows_dropped: int
    n_rows_after: int


@dataclass(frozen=True)
class UniverseReport:
    n_input_rows: int
    n_eligible_rows: int
    filter_diagnostics: tuple[FilterDiagnostic, ...]
