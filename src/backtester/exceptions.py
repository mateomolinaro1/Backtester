"""Custom exception and warning types shared across the backtester.

Kept in one place rather than scattered per-module so callers have a single,
stable import path for anything they might want to catch or filter by type.
Most validation failures throughout the codebase are still plain
``ValueError`` -- nothing currently needs to catch those by a more specific
type. A type belongs here once something (a caller, a test) actually
distinguishes it from a generic error, not preemptively.
"""

from __future__ import annotations


class AmbiguousDataSourceConfigWarning(UserWarning):
    """A ``data_sources`` config specifies both 'combined' and 'market'/'fundamentals'.

    'combined' takes precedence; this warns about which key(s) were ignored
    rather than silently dropping them.
    """
