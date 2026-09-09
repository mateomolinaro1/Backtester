"""Investment universe construction: threshold-based eligibility filtering.

The eligible universe at each date is a filtered subset of whatever is in the
cleaned market data -- U_t = {i in U_t^raw : E_{i,t} = 1} in the guide's
notation. Filters are evaluated per (security_id, date) row, so U_t is
recomputed at the same daily granularity as the underlying data; there is no
periodic-reconstitution or entry/exit-buffer logic here (deferred -- see
ADR-0005). No filters at all is a valid, common case: it means the caller's
data source is already the intended universe (see ADR-0005's "Case 1").

Index-membership-table eligibility (a security is in-universe because it is a
constituent of some external index as of date t) is out of scope here --
that's treated as an upstream data-supply concern, the same boundary already
drawn for raw data acquisition (see project memory: data-scope-pit).
"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from backtester.universe.types import EligibilityFilter, FilterDiagnostic, UniverseReport

_OPERATORS = {
    "==": lambda s, v: s == v,
    "!=": lambda s, v: s != v,
    ">": lambda s, v: s > v,
    ">=": lambda s, v: s >= v,
    "<": lambda s, v: s < v,
    "<=": lambda s, v: s <= v,
    "in": lambda s, v: s.isin(v),
    "not_in": lambda s, v: ~s.isin(v),
    "is_null": lambda s, v: s.isna(),
    "is_not_null": lambda s, v: s.notna(),
}


def build_universe(
    market: pd.DataFrame, filters: Sequence[EligibilityFilter]
) -> tuple[pd.DataFrame, UniverseReport]:
    """Apply eligibility filters to cleaned market data.

    Returns the eligible universe as a ``(security_id, date)`` membership
    table -- not the filtered market data itself. Universe membership is kept
    distinct from market data on purpose (per CLAUDE.md's canonical
    vocabulary): downstream modules join against this table rather than
    receiving a pre-merged frame.

    Filters are applied sequentially, each narrowing what the previous filter
    left (logical AND), matching the guide's U_t^(0) -> U_t^(1) -> ... -> U_t
    pipeline. Every filter's ``column`` must already exist in ``market`` --
    there is no implicit derivation of eligibility columns (e.g. market cap)
    here; the caller supplies them already computed.
    """
    unknown_columns = [f.column for f in filters if f.column not in market.columns]
    if unknown_columns:
        raise ValueError(
            f"universe filter references unknown column(s) {unknown_columns}; "
            f"available columns: {sorted(market.columns)}"
        )

    n_input_rows = len(market)
    eligible_mask = pd.Series(True, index=market.index)
    diagnostics: list[FilterDiagnostic] = []

    for f in filters:
        n_before = int(eligible_mask.sum())
        filter_mask = _OPERATORS[f.operator](market[f.column], f.value)
        eligible_mask &= filter_mask
        n_after = int(eligible_mask.sum())
        diagnostics.append(
            FilterDiagnostic(
                column=f.column,
                operator=f.operator,
                value=f.value,
                n_rows_before=n_before,
                n_rows_dropped=n_before - n_after,
                n_rows_after=n_after,
            )
        )

    universe = market.loc[eligible_mask, ["security_id", "date"]].reset_index(drop=True)

    report = UniverseReport(
        n_input_rows=n_input_rows,
        n_eligible_rows=len(universe),
        filter_diagnostics=tuple(diagnostics),
    )
    return universe, report
