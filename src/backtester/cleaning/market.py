"""Cleaning for daily market data (canonical schema, see data/schema.py).

Validates structural integrity only: key uniqueness and non-implausible
price/volume values. This does not touch statistical outliers (see the
outlier-treatment module) and does not impute missing returns — a missing
return is either an expected artifact of a new listing or something that
needs investigating, never a value to fabricate.
"""

from __future__ import annotations

import pandas as pd

from backtester.cleaning.types import CleaningReport

_REQUIRED_COLUMNS = ("security_id", "date", "price", "volume", "return")


def clean_market_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """Validate and clean daily market data.

    Raises if the ``(security_id, date)`` key is not unique (no resolution rule
    is established for this source; a future duplicate must be diagnosed, not
    silently dropped). Drops rows with non-positive price or negative volume.
    """
    missing_cols = [c for c in _REQUIRED_COLUMNS if c not in raw.columns]
    if missing_cols:
        raise ValueError(f"market data is missing required columns: {missing_cols}")

    n_input_rows = len(raw)

    duplicate_mask = raw.duplicated(["security_id", "date"], keep=False)
    if duplicate_mask.any():
        example = raw.loc[duplicate_mask, ["security_id", "date"]].drop_duplicates().head(5)
        raise ValueError(
            "market data has duplicate (security_id, date) keys with no established "
            f"resolution rule; first offending keys:\n{example.to_string(index=False)}"
        )

    invalid_mask = (raw["price"] <= 0) | (raw["volume"] < 0)
    dropped_reasons = {
        "non_positive_price": int((raw["price"] <= 0).sum()),
        "negative_volume": int((raw["volume"] < 0).sum()),
    }
    quarantined_keys = tuple(
        (int(security_id), pd.Timestamp(date))
        for security_id, date in raw.loc[invalid_mask, ["security_id", "date"]].itertuples(
            index=False, name=None
        )
    )

    cleaned = raw.loc[~invalid_mask].reset_index(drop=True)

    notes = _null_return_notes(cleaned)

    report = CleaningReport(
        n_input_rows=n_input_rows,
        n_output_rows=len(cleaned),
        dropped_reasons=dropped_reasons,
        quarantined_keys=quarantined_keys,
        notes=notes,
    )
    return cleaned, report


def _null_return_notes(cleaned: pd.DataFrame) -> tuple[str, ...]:
    null_return_mask = cleaned["return"].isna()
    n_null_return = int(null_return_mask.sum())
    if n_null_return == 0:
        return ()

    first_obs_date = cleaned.groupby("security_id")["date"].transform("min")
    is_first_obs = cleaned["date"].eq(first_obs_date)
    n_unexplained = int((null_return_mask & ~is_first_obs).sum())
    n_expected = n_null_return - n_unexplained
    return (
        f"{n_null_return} null return values: {n_expected} align with a security's first "
        f"observation (expected, no prior price to compute a return from), "
        f"{n_unexplained} do not and should be investigated",
    )
