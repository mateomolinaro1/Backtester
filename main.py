"""Run the full backtesting pipeline from a JSON config file.

Usage:
    python main.py
    python main.py --config config/backtest.combined.example.json
"""

from __future__ import annotations

import argparse

from backtester.pipeline import BacktestPipeline


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        default="config/backtest.example.json",
        help="path to the pipeline JSON config (default: config/backtest.example.json)",
    )
    args = parser.parse_args()

    pipeline = BacktestPipeline.from_config(args.config).run()

    assert pipeline.isovol is not None
    assert pipeline.isovol_report is not None
    report = pipeline.isovol_report
    print(f"config:            {args.config}")
    print(f"final rows:        {len(pipeline.isovol)}")
    print(f"n_dates:           {report.n_dates}")
    print(f"n_scaled:          {report.n_scaled}")
    print(f"n_capped_by_leverage: {report.n_capped_by_leverage}")
    print(f"mean_scale_factor: {report.mean_scale_factor}")
    print(pipeline.isovol.head())


if __name__ == "__main__":
    main()
