"""Canonical column schemas and per-source column mappings.

Domain logic (cleaning and everything built on top of it) only ever sees the
canonical column names below. A new data source is supported by constructing a
new ``*ColumnMapping`` instance (canonical name -> that source's actual column
name) and passing it to the corresponding ``read_*`` function in ``io.py`` --
no changes to cleaning or any other downstream module are required.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketColumnMapping:
    """Canonical market-data columns -> a source's actual column names."""

    security_id: str = "permno"
    date: str = "date"
    price: str = "prc"
    volume: str = "vol"
    return_: str = "ret"

    def source_to_canonical(self) -> dict[str, str]:
        return {
            self.security_id: "security_id",
            self.date: "date",
            self.price: "price",
            self.volume: "volume",
            self.return_: "return",
        }


@dataclass(frozen=True)
class FundamentalsColumnMapping:
    """Canonical fundamentals columns -> a source's actual column names."""

    security_id: str = "permno"
    company_id: str = "gvkey"
    annual_report_date: str = "adate"
    quarterly_report_date: str = "qdate"
    available_date: str = "public_date"
    ticker: str = "ticker"
    cusip: str = "cusip"

    def source_to_canonical(self) -> dict[str, str]:
        return {
            self.security_id: "security_id",
            self.company_id: "company_id",
            self.annual_report_date: "annual_report_date",
            self.quarterly_report_date: "quarterly_report_date",
            self.available_date: "available_date",
            self.ticker: "ticker",
            self.cusip: "cusip",
        }


#: Default mapping for the WRDS/CRSP extracts already in data/ (identity mapping --
#: today's source column names already match what they represent).
WRDS_MARKET_COLUMNS = MarketColumnMapping()

#: Default mapping for the WRDS Financial Ratios (funda) extract already in data/.
WRDS_FUNDAMENTALS_COLUMNS = FundamentalsColumnMapping()

#: Named presets a JSON config can select by name instead of spelling out a full
#: custom mapping (see config.py). Add an entry here once a new source is used
#: repeatedly enough to be worth naming; a one-off source can still be used via a
#: fully custom mapping without ever being added here.
MARKET_COLUMN_PRESETS: dict[str, MarketColumnMapping] = {
    "wrds": WRDS_MARKET_COLUMNS,
}

FUNDAMENTALS_COLUMN_PRESETS: dict[str, FundamentalsColumnMapping] = {
    "wrds": WRDS_FUNDAMENTALS_COLUMNS,
}
