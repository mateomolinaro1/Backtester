"""Generate synthetic Parquet files that mirror the schema of the real data/
extracts, for exercising the backtester on a machine that doesn't have the
real (licensed) WRDS/CRSP data.

This produces the same 4 files, with the same column names, dtypes, and
index structure as the real ones -- but every value (ids, names, tickers,
prices, ratios) is randomly generated and carries no economic meaning:

- wrds_gross_query.parquet         (daily market panel)
- wrds_funda_gross_query.parquet   (quarterly fundamentals panel)
- risk_free_returns.parquet        (daily risk-free return series)
- russell_returns.parquet          (daily benchmark index levels)

Usage:
    python scripts/generate_synthetic_data.py
    python scripts/generate_synthetic_data.py --output-dir data --force

By default files are written to data/ but an existing file is never
overwritten unless --force is passed, so this is safe to run on a machine
that already has the real extracts.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# Real GICS sector codes (gsector) with a human-readable description, matching
# the column pair (gsector, gicdesc) in the real fundamentals extract.
_GICS_SECTORS = [
    ("10", "Energy"),
    ("15", "Materials"),
    ("20", "Industrials"),
    ("25", "Consumer Discretionary"),
    ("30", "Consumer Staples"),
    ("35", "Health Care"),
    ("40", "Financials"),
    ("45", "Information Technology"),
    ("50", "Communication Services"),
    ("55", "Utilities"),
    ("60", "Real Estate"),
]

#: (canonical_name, code_column, desc_column) for each Fama-French industry
#: granularity present in the real extract. Values are synthetic cluster ids,
#: not the real FF industry taxonomy -- only the schema (object desc + float
#: code, consistent per security) is reproduced.
_FF_GRANULARITIES = ["ffi5", "ffi10", "ffi12", "ffi17", "ffi30", "ffi38", "ffi48", "ffi49"]

#: Ordered fundamentals columns, matching data/wrds_funda_gross_query.parquet.
_FUNDA_RATIO_COLUMNS = [
    "capei", "be", "bm", "evm", "pe_op_basic", "pe_op_dil", "pe_exi", "pe_inc",
    "ps", "pcf", "dpr", "npm", "opmbd", "opmad", "gpm", "ptpm", "cfm", "roa",
    "roe", "roce", "efftax", "aftret_eq", "aftret_invcapx", "aftret_equity",
    "pretret_noa", "pretret_earnat", "gprof", "equity_invcap", "debt_invcap",
    "totdebt_invcap", "capital_ratio", "int_debt", "int_totdebt", "cash_lt",
    "invt_act", "rect_act", "debt_at", "debt_ebitda", "short_debt", "curr_debt",
    "lt_debt", "profit_lct", "ocf_lct", "cash_debt", "fcf_ocf", "lt_ppent",
    "dltt_be", "debt_assets", "debt_capital", "de_ratio", "intcov",
    "intcov_ratio", "cash_ratio", "quick_ratio", "curr_ratio",
    "cash_conversion", "inv_turn", "at_turn", "rect_turn", "pay_turn",
    "sale_invcap", "sale_equity", "sale_nwc", "rd_sale", "adv_sale",
    "staff_sale", "accrual", "ret_crsp",
]

#: (mean, std) for ratio columns worth a plausible scale (everything else in
#: _FUNDA_RATIO_COLUMNS falls back to a generic standard-normal draw). Keyed
#: subset chosen for the columns exercised by config/backtest.example.json
#: and common financial-ratio magnitudes.
_RATIO_SCALES: dict[str, tuple[float, float]] = {
    "bm": (0.6, 0.4),
    "roa": (0.05, 0.08),
    "roe": (0.1, 0.15),
    "gpm": (0.35, 0.2),
    "npm": (0.08, 0.12),
    "de_ratio": (1.0, 0.8),
    "curr_ratio": (1.5, 0.8),
    "quick_ratio": (1.0, 0.6),
    "pe_exi": (20.0, 12.0),
    "ps": (2.5, 2.0),
    "evm": (12.0, 8.0),
    "divyield": (0.02, 0.02),
    "ptb": (3.0, 2.0),
    "peg_trailing": (1.5, 1.0),
}

_NAN_RATE = 0.02


def _security_metadata(rng: np.random.Generator, n: int) -> pd.DataFrame:
    """One synthetic identity per security, shared across all 4 files."""
    permno = rng.choice(np.arange(10000, 99999), size=n, replace=False)
    gvkey = rng.choice(np.arange(100000, 999999), size=n, replace=False).astype(str)
    permco = permno + 1  # arbitrary but stable link, mirrors real permno->permco pairing
    sector_idx = rng.integers(0, len(_GICS_SECTORS), size=n)
    ff_cluster = rng.integers(0, 8, size=n)
    return pd.DataFrame(
        {
            "permno": permno,
            "gvkey": gvkey,
            "permco": permco,
            "ticker": [f"SYN{i:04d}" for i in range(n)],
            "comnam": [f"SYNTHETIC COMPANY {i:04d}" for i in range(n)],
            "cusip": [f"SYN{i:05d}0" for i in range(n)],
            "exchcd": rng.choice([1, 2, 3], size=n),
            "gsector": [_GICS_SECTORS[j][0] for j in sector_idx],
            "gicdesc": [_GICS_SECTORS[j][1] for j in sector_idx],
            "ff_cluster": ff_cluster,
            "start_price": rng.uniform(5.0, 300.0, size=n),
            "shrout": rng.uniform(1e4, 5e6, size=n),
        }
    )


def _with_nans(rng: np.random.Generator, values: np.ndarray, rate: float = _NAN_RATE) -> np.ndarray:
    values = values.astype(float).copy()
    mask = rng.random(values.shape) < rate
    values[mask] = np.nan
    return values


def generate_market_panel(
    rng: np.random.Generator, securities: pd.DataFrame, dates: pd.DatetimeIndex
) -> pd.DataFrame:
    """Build a daily market panel matching wrds_gross_query.parquet's schema."""
    frames = []
    for _, sec in securities.iterrows():
        n_days = len(dates)
        daily_ret = rng.normal(0.0004, 0.02, size=n_days)
        prc = sec["start_price"] * np.cumprod(1.0 + daily_ret)
        shrout = sec["shrout"] * (1.0 + rng.normal(0.0, 0.0005, size=n_days).cumsum())
        vol = np.abs(rng.normal(0.02, 0.01, size=n_days)) * shrout
        frames.append(
            pd.DataFrame(
                {
                    "ticker": sec["ticker"],
                    "exchcd": sec["exchcd"],
                    "comnam": sec["comnam"],
                    "cusip": sec["cusip"],
                    "ncusip": sec["cusip"],
                    "permno": sec["permno"],
                    "permco": sec["permco"],
                    "namedt": dates[0],
                    "nameendt": pd.Timestamp(dates[-1]) + pd.DateOffset(years=5),
                    "date": dates,
                    "ret": daily_ret,
                    "prc": prc,
                    "shrout": shrout,
                    "vol": vol,
                }
            )
        )
    panel = pd.concat(frames, ignore_index=True)
    panel["market_cap"] = panel["prc"] * panel["shrout"] * 1000.0
    panel["mcap_rank"] = (
        panel.groupby("date")["market_cap"].rank(ascending=False, method="first").astype(int)
    )
    return panel.astype({"exchcd": "int64", "permno": "int64", "permco": "int64"})


def generate_funda_panel(
    rng: np.random.Generator, securities: pd.DataFrame, quarter_ends: pd.DatetimeIndex
) -> pd.DataFrame:
    """Build a quarterly fundamentals panel matching wrds_funda_gross_query.parquet."""
    frames = []
    for _, sec in securities.iterrows():
        # Each security only has a random contiguous sub-range of history,
        # mirroring the uneven per-permno row counts in the real extract.
        start = rng.integers(0, max(1, len(quarter_ends) - 4))
        stop = rng.integers(start + 1, len(quarter_ends) + 1)
        qdates = quarter_ends[start:stop]
        n = len(qdates)
        if n == 0:
            continue
        lag_days = rng.integers(45, 76, size=n)
        public_date = qdates + pd.to_timedelta(lag_days, unit="D")

        row: dict[str, object] = {
            "gvkey": sec["gvkey"],
            "permno": sec["permno"],
            "adate": qdates,
            "qdate": qdates,
            "public_date": public_date,
        }
        for col in _FUNDA_RATIO_COLUMNS:
            mean, std = _RATIO_SCALES.get(col, (0.0, 1.0))
            row[col] = _with_nans(rng, rng.normal(mean, std, size=n))
        row["gsector"] = sec["gsector"]
        row["gicdesc"] = sec["gicdesc"]
        row["mktcap"] = sec["start_price"] * sec["shrout"] * 1000.0 * (1.0 + rng.normal(0, 0.1, size=n))
        row["price"] = sec["start_price"] * (1.0 + rng.normal(0, 0.1, size=n))
        for col in ("ptb", "peg_trailing", "divyield"):
            mean, std = _RATIO_SCALES[col]
            row[col] = _with_nans(rng, rng.normal(mean, std, size=n))
        for gran in _FF_GRANULARITIES:
            row[f"{gran}_desc"] = f"FFIND_{sec['ff_cluster']}"
            row[gran] = float(sec["ff_cluster"])
        row["ticker"] = sec["ticker"]
        row["cusip"] = sec["cusip"]
        frames.append(pd.DataFrame(row))
    funda = pd.concat(frames, ignore_index=True)
    return funda.astype({"gvkey": "object", "permno": "int64"})


def generate_risk_free_returns(rng: np.random.Generator, dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Build a daily risk-free return series matching risk_free_returns.parquet."""
    rf = pd.DataFrame(
        {"rf_returns": rng.uniform(0.00002, 0.00015, size=len(dates))},
        index=pd.DatetimeIndex(dates, name="date"),
    )
    return rf


def generate_russell_returns(rng: np.random.Generator, dates: pd.DatetimeIndex) -> pd.DataFrame:
    """Build a daily benchmark level series matching russell_returns.parquet."""
    daily_ret = rng.normal(0.0003, 0.011, size=len(dates))
    level = 750.0 * np.cumprod(1.0 + daily_ret)
    ew_ret = rng.normal(0.0003, 0.012, size=len(dates))
    ew_level = 980.0 * np.cumprod(1.0 + ew_ret)
    return pd.DataFrame({"Russell 1000": level, "Russell 1000 EW": ew_level}, index=dates)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--n-securities", type=int, default=200)
    parser.add_argument(
        "--force", action="store_true", help="overwrite files that already exist"
    )
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    securities = _security_metadata(rng, args.n_securities)

    market_dates = pd.bdate_range("2020-01-02", "2024-12-31")
    quarter_ends = pd.date_range("2020-03-31", "2024-12-31", freq="QE")
    macro_dates = pd.bdate_range("2019-01-02", "2025-01-02")

    outputs = {
        "wrds_gross_query.parquet": generate_market_panel(rng, securities, market_dates),
        "wrds_funda_gross_query.parquet": generate_funda_panel(rng, securities, quarter_ends),
        "risk_free_returns.parquet": generate_risk_free_returns(rng, macro_dates),
        "russell_returns.parquet": generate_russell_returns(rng, macro_dates),
    }

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, df in outputs.items():
        dest = args.output_dir / filename
        if dest.exists() and not args.force:
            print(f"skip  {dest} (already exists; pass --force to overwrite)")
            continue
        df.to_parquet(dest)
        print(f"wrote {dest} ({len(df)} rows, {len(df.columns)} cols)")


if __name__ == "__main__":
    main()
