"""Command-line entry point for the offline demo."""

import argparse

from openmarket_ai.research import create_demo_report


def main(argv: list[str] | None = None) -> int:
    """Print an educational demo report to standard output."""
    parser = argparse.ArgumentParser(description="OpenMarket AI offline demo")
    parser.add_argument("--symbol", default="XAUUSD", help="Display label only")
    args = parser.parse_args(argv)
    try:
        report = create_demo_report(args.symbol)
    except ValueError as exc:
        parser.error(str(exc))
    print(report.to_markdown(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
