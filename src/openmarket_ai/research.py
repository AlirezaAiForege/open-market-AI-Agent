"""Offline demo reports. No market feed, model API, or order execution."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResearchReport:
    """A deterministic demonstration, never a market assessment."""

    symbol: str
    mode: str = "DEMO"
    data_status: str = "NO_MARKET_DATA"
    signal: str = "ABSTAIN"

    def to_markdown(self) -> str:
        """Render the report with explicit missing-data limitations."""
        return (
            "# OpenMarket AI Agent - Demo Research Report\n\n"
            f"- Symbol: {self.symbol}\n"
            f"- Mode: {self.mode}\n"
            f"- Data status: {self.data_status}\n"
            f"- Signal: {self.signal}\n\n"
            "## Observations\n"
            "This is a static educational demonstration. No market data was loaded.\n"
            "No live prices, indicators, forecasts, or AI analysis are available.\n\n"
            "## Scenarios and risk\n"
            "Bullish, bearish, and neutral scenarios cannot be evaluated without data.\n"
            "Entry, stop-loss, targets, and performance are unavailable.\n"
            "No orders are placed. No account credentials are required.\n\n"
            "## Sources and limitations\n"
            "Sources: none (offline demo). Data timestamp and timeframe: unavailable.\n"
            "This report is not personalized investment advice.\n"
        )


def create_demo_report(symbol: str = "XAUUSD") -> ResearchReport:
    """Normalize a display symbol without implying support for a market feed."""
    if not isinstance(symbol, str):
        raise TypeError("symbol must be a string")
    normalized = symbol.strip().upper()
    if not normalized or len(normalized) > 20:
        raise ValueError("symbol must contain 1 to 20 ASCII letters or digits")
    if not normalized.isascii() or not normalized.isalnum():
        raise ValueError("symbol must contain 1 to 20 ASCII letters or digits")
    return ResearchReport(symbol=normalized)
