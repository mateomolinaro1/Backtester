"""Calendar alignment: reindexing a date-indexed series onto an explicit
target calendar, with a bounded forward-fill (ADR-0016).

Distinct from ``asof.py``'s ``as_of_join``, a different alignment technique
for a different problem: ``as_of_join`` is a backward-looking,
staleness-tolerant match between two DataFrames on different date semantics
(market's daily date vs. funda's report-vintage ``available_date``).
``align_to_calendar`` instead reindexes a single series onto a calendar
that's already known (typically market's own unique trading dates) and
forward-fills genuinely missing rows, up to a limit -- a date present in the
calendar but entirely absent from the series' own index becomes null after
the reindex, then gets filled from the last available prior value if within
``max_ffill``.

This is a second, independent fill stage from a source reader's own
``max_ffill`` (e.g. ``read_benchmark_returns``/``read_risk_free_returns``,
ADR-0012): that fill only ever sees rows the source's own file actually has
-- it fills null *values* at *existing* index positions. A date missing as a
*row* entirely (not just null) survives a source-level fill untouched, no
matter how large it's set; only reindexing onto an external calendar first
turns "row doesn't exist" into "row exists and is null," which forward-fill
can then act on. Originally embedded directly in ``timeseries.py``'s
``rolling_beta`` (ADR-0012 addendum); extracted here once a second consumer
was expected (ADR-0016) -- a standalone, reusable primitive rather than
logic duplicated inside every function that needs a series aligned to
market's calendar.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CalendarAlignmentReport:
    n_calendar_dates: int
    #: Calendar dates where series had no value at all (row absent from its
    #: own index) before this function's forward-fill ran.
    n_missing_before_fill: int
    #: Of those, how many got filled from a prior value within max_ffill.
    n_filled: int
    #: Calendar dates still null after the fill (gap longer than max_ffill,
    #: or no prior value existed yet to fill from).
    n_missing_after_fill: int


def align_to_calendar(
    series: pd.Series,
    calendar: pd.DatetimeIndex,
    *,
    max_ffill: int | None = 5,
) -> tuple[pd.Series, CalendarAlignmentReport]:
    """Reindex ``series`` onto ``calendar``, forward-filling gaps up to
    ``max_ffill`` consecutive missing calendar dates.

    ``series`` is expected to already be as clean as its own source allows
    (e.g. already passed through a source-level ``max_ffill``/dedup, see
    module docstring) -- this only addresses gaps relative to ``calendar``,
    not gaps within ``series``'s own native index. ``max_ffill=None`` (or
    ``0``) disables filling, returning the strict reindex.
    """
    if not isinstance(series.index, pd.DatetimeIndex):
        raise ValueError("series must be indexed by date (a DatetimeIndex)")
    if series.index.has_duplicates:
        raise ValueError(
            "series has duplicate dates in its index; deduplicate before calling "
            "align_to_calendar"
        )

    on_calendar = series.reindex(calendar)
    n_missing_before = int(on_calendar.isna().sum())
    if max_ffill:
        on_calendar = on_calendar.ffill(limit=max_ffill)
    n_missing_after = int(on_calendar.isna().sum())

    report = CalendarAlignmentReport(
        n_calendar_dates=len(calendar),
        n_missing_before_fill=n_missing_before,
        n_filled=n_missing_before - n_missing_after,
        n_missing_after_fill=n_missing_after,
    )
    return on_calendar, report