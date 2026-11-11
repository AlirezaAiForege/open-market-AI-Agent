"""Offline demo and validated historical CSV research command line."""
import argparse
import json
from dataclasses import asdict
from importlib.resources import files
from pathlib import Path
from openmarket_ai import __version__
from openmarket_ai.historical import Metadata, build_report, to_markdown
from openmarket_ai.market_data import TIMEFRAMES, load_csv, parse_csv
from openmarket_ai.research import create_demo_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="OpenMarket AI offline research MVP")
    parser.add_argument("--version", action="version", version=__version__)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--csv", type=Path, help="Local UTF-8 OHLCV file")
    inputs.add_argument("--example", action="store_true", help="Use bundled SYNTHETIC data")
    parser.add_argument("--symbol", default="XAUUSD", help="Instrument label")
    parser.add_argument("--source", help="User-declared data source")
    parser.add_argument("--data-license", help="User-declared data usage terms")
    parser.add_argument("--venue")
    parser.add_argument("--instrument-type")
    parser.add_argument("--quote-currency")
    parser.add_argument("--timeframe", choices=TIMEFRAMES)
    parser.add_argument("--closed-bars", action="store_true", help="Confirm all CSV bars are closed")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--output", type=Path, help="Create a new UTF-8 report; never overwrite")
    args = parser.parse_args(argv)
    try:
        if args.csv:
            names = ("source", "data_license", "venue", "instrument_type", "quote_currency", "timeframe")
            missing = ["--" + name.replace("_", "-") for name in names if not getattr(args, name)]
            if missing or not args.closed_bars:
                raise ValueError("CSV research requires " + ", ".join(missing + ([] if args.closed_bars else ["--closed-bars"])))
            dataset = load_csv(args.csv)
            metadata = Metadata(symbol=args.symbol, **{name: getattr(args, name) for name in names})
            report = build_report(dataset, metadata)
        elif args.example:
            raw = files("openmarket_ai").joinpath("fixtures/synthetic_ohlcv.csv").read_bytes()
            dataset = parse_csv(raw)
            metadata = Metadata("SYNTHETIC", "bundled invented fixture", "MIT synthetic fixture",
                                "none", "synthetic", "DEMO", "1d", synthetic=True)
            report = build_report(dataset, metadata)
        else:
            demo = create_demo_report(args.symbol)
            report = asdict(demo)
        if args.format == "json":
            text = json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
        else:
            text = to_markdown(report) if args.csv or args.example else demo.to_markdown()
        if args.output:
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(text)
            print(f"Saved report: {args.output}")
        else:
            print(text, end="")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
