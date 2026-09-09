"""Cleaning for fundamentals data (canonical schema, see data/schema.py).

The (security_id, available_date) key is not naturally unique in the WRDS
source this was designed against: a small number of securities are linked to
two companies simultaneously, a known CRSP-Compustat link-table issue (see
project memory: funda-duplicate-gvkey-links). Two duplicate shapes are
recognized and resolved deterministically; anything else raises rather than
being silently guessed at.
"""

from __future__ import annotations

import pandas as pd

from backtester.cleaning.types import CleaningReport

_REQUIRED_COLUMNS = (
    "security_id",
    "company_id",
    "annual_report_date",
    "quarterly_report_date",
    "available_date",
    "ticker",
    "cusip",
)
_IDENTIFIER_ONLY_DIFF_COLUMNS = frozenset({"ticker", "cusip", "company_id"})


def clean_fundamentals(raw: pd.DataFrame) -> tuple[pd.DataFrame, CleaningReport]:
    """Validate and clean fundamentals data.

    For each duplicate ``(security_id, available_date)`` group of size 2:
      - if the two rows differ only in ``ticker``/``cusip``/``company_id``
        (identical financials, one row has a null ticker), keep the
        non-null-ticker row;
      - if the two rows differ in ``company_id`` and other substantive columns
        (a real dual-company conflict — the underlying financials genuinely
        disagree), quarantine both rows: there is no basis in this data for
        picking one;
      - any other shape (group size != 2, or a diff pattern that doesn't match
        either case above) raises.
    """
    missing_cols = [c for c in _REQUIRED_COLUMNS if c not in raw.columns]
    if missing_cols:
        raise ValueError(f"fundamentals data is missing required columns: {missing_cols}")

    n_input_rows = len(raw)
    _check_date_ordering(raw)

    rows_to_drop: list[int] = []
    quarantined_keys: list[tuple[int, pd.Timestamp]] = []
    n_ticker_resolved = 0

    duplicate_mask = raw.duplicated(["security_id", "available_date"], keep=False)
    for (security_id, available_date), group in raw.loc[duplicate_mask].groupby(
        ["security_id", "available_date"]
    ):
        if len(group) != 2:
            raise ValueError(
                f"fundamentals data has an unrecognized duplicate group of size "
                f"{len(group)} for (security_id={security_id}, "
                f"available_date={available_date}); no resolution rule exists"
            )

        diff_columns = _diff_columns(group.iloc[0], group.iloc[1])

        if diff_columns <= _IDENTIFIER_ONLY_DIFF_COLUMNS:
            null_ticker_rows = group.index[group["ticker"].isna()]
            non_null_ticker_rows = group.index[group["ticker"].notna()]
            if len(null_ticker_rows) != 1 or len(non_null_ticker_rows) != 1:
                raise ValueError(
                    "fundamentals data has an identifier-only duplicate group for "
                    f"(security_id={security_id}, available_date={available_date}) "
                    "without exactly one non-null ticker; no resolution rule exists"
                )
            rows_to_drop.append(int(null_ticker_rows[0]))
            n_ticker_resolved += 1
        elif "company_id" in diff_columns:
            rows_to_drop.extend(int(i) for i in group.index)
            quarantined_keys.append(
                (
                    int(group["security_id"].iloc[0]),
                    pd.Timestamp(group["available_date"].iloc[0]),
                )
            )
        else:
            raise ValueError(
                f"fundamentals data has an unrecognized duplicate pattern for "
                f"(security_id={security_id}, available_date={available_date}); "
                f"differing columns: {sorted(diff_columns)}"
            )

    cleaned = raw.drop(index=rows_to_drop).reset_index(drop=True)

    remaining_duplicates = int(cleaned.duplicated(["security_id", "available_date"]).sum())
    if remaining_duplicates:
        raise ValueError(
            f"{remaining_duplicates} duplicate (security_id, available_date) keys remain "
            "after resolution; this indicates a bug in the resolution logic"
        )

    report = CleaningReport(
        n_input_rows=n_input_rows,
        n_output_rows=len(cleaned),
        dropped_reasons={
            "duplicate_ticker_only_resolved": n_ticker_resolved,
            "duplicate_dual_company_quarantined_rows": len(rows_to_drop) - n_ticker_resolved,
        },
        quarantined_keys=tuple(quarantined_keys),
        notes=(),
    )
    return cleaned, report


def _check_date_ordering(raw: pd.DataFrame) -> None:
    # annual_report_date and quarterly_report_date are independent report vintages and
    # are not necessarily ordered relative to each other. What must hold is the actual
    # PIT constraint: neither reference date may be after the date the row becomes
    # available.
    bad_order = raw.loc[
        (raw["annual_report_date"] > raw["available_date"])
        | (raw["quarterly_report_date"] > raw["available_date"])
    ]
    if not bad_order.empty:
        first = bad_order[["security_id", "available_date"]].iloc[0].to_dict()
        raise ValueError(
            f"fundamentals data has {len(bad_order)} rows violating "
            "annual_report_date <= available_date and quarterly_report_date <= "
            f"available_date; first offending key: {first}"
        )


def _diff_columns(row_a: pd.Series, row_b: pd.Series) -> set[str]:
    return {
        col
        for col in row_a.index
        if not (row_a[col] == row_b[col] or (pd.isna(row_a[col]) and pd.isna(row_b[col])))
    }
