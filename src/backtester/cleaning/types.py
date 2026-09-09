"""Shared result type for the data-cleaning functions."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

#: (permno, date) for market cleaning; (permno, public_date) for funda cleaning.
QuarantinedKey = tuple[int, pd.Timestamp]


@dataclass(frozen=True)
class CleaningReport:
    """Auditable summary of what a cleaning function did to its input.

    ``dropped_reasons`` maps a short reason code to a row count; ``quarantined_keys``
    lists the exact keys that were removed, so a quarantine can be traced back to
    specific securities/dates without re-deriving it from the row counts.
    """

    n_input_rows: int
    n_output_rows: int
    dropped_reasons: dict[str, int]
    quarantined_keys: tuple[QuarantinedKey, ...]
    notes: tuple[str, ...] = ()
