"""Auditable historical observations, never an execution or prediction engine."""
import html
from dataclasses import asdict, dataclass
from openmarket_ai import __version__
from openmarket_ai.indicators import atr, rsi, sma
from openmarket_ai.market_data import Dataset, TIMEFRAMES
from openmarket_ai.research import create_demo_report


@dataclass(frozen=True)
class Metadata:
    symbol: str
    source: str
    data_license: str
    venue: str
    instrument_type: str
    quote_currency: str
    timeframe: str
    synthetic: bool = False


def _metadata(metadata: Metadata) -> dict:
    data = asdict(metadata)
    data["symbol"] = create_demo_report(metadata.symbol).symbol
    for key in ("source", "data_license", "venue", "instrument_type", "quote_currency"):
        value = data[key]
        if not isinstance(value, str) or not value.strip() or len(value) > 300 or not value.isprintable():
            raise ValueError(f"{key} must be a nonempty single line of at most 300 characters")
        data[key] = value.strip()
    if metadata.timeframe not in TIMEFRAMES:
        raise ValueError("unsupported timeframe")
    return data


def build_report(dataset: Dataset, metadata: Metadata) -> dict:
    context = _metadata(metadata)
    bars = dataset.bars
    if len(bars) < 50:
        raise ValueError("at least 50 closed bars are required (SMA50 warm-up)")
    closes = [bar.close for bar in bars]
    indicators = {"sma20": sma(closes, 20), "sma50": sma(closes, 50),
                  "rsi14": rsi(closes), "atr14": atr(bars)}
    step = TIMEFRAMES[metadata.timeframe]
    intervals = [(b.timestamp - a.timestamp).total_seconds() for a, b in zip(bars, bars[1:])]
    irregular = sum(delta != step for delta in intervals)
    if any(delta < step or delta % step != 0 for delta in intervals):
        raise ValueError("timestamps are inconsistent with the declared timeframe")
    if closes[-1] > indicators["sma20"] > indicators["sma50"]:
        observation = "Last close > SMA20 > SMA50 (upward historical alignment)."
    elif closes[-1] < indicators["sma20"] < indicators["sma50"]:
        observation = "Last close < SMA20 < SMA50 (downward historical alignment)."
    else:
        observation = "Moving-average alignment is mixed or flat."
    warnings = [
        "Historical observations only; data freshness and source authenticity are not independently verified.",
        "Metadata and closed-bar status are user declarations; licensing is not verified by this software.",
        "Indicators share price inputs and are not independent confirmations or proof of an edge.",
        "RSI extremes are not automatic reversal signals; ATR measures range, not direction.",
        "No news, fundamentals, AI inference, backtest, execution costs, or profitability evaluation.",
        "No entry, stop-loss, price targets, orders, or personalized investment advice.",
    ]
    if metadata.synthetic:
        warnings.insert(0, "SYNTHETIC DATA: invented fixture for software demonstrations, not market history.")
    if irregular:
        warnings.append(f"{irregular} irregular intervals detected; these may be session closures or missing bars. No bars were filled.")
    return {
        "schema_version": "1.0", "software_version": __version__,
        "mode": "SYNTHETIC_RESEARCH" if metadata.synthetic else "HISTORICAL_RESEARCH",
        "signal": "ABSTAIN", "metadata": context,
        "data": {"sha256": dataset.sha256, "bar_count": len(bars),
                 "first_timestamp_utc": bars[0].timestamp.isoformat(),
                 "last_timestamp_utc": bars[-1].timestamp.isoformat(),
                 "last_close": closes[-1], "irregular_intervals": irregular,
                 "freshness": "HISTORICAL_NOT_VERIFIED_LIVE", "closed_bars": "SYNTHETIC_FIXED_FIXTURE" if metadata.synthetic else "USER_CONFIRMED"},
        "indicators": indicators, "observation": observation,
        "scenarios": {
            "bullish": "Research hypothesis only: a later closed bar above SMA20 above SMA50 would maintain upward alignment.",
            "bearish": "Research hypothesis only: a later closed bar below SMA20 below SMA50 would maintain downward alignment.",
            "neutral": "Mixed or equal moving averages indicate no directional alignment under this rule.",
        },
        "warnings": warnings,
        "methodology": "Trailing SMA20/SMA50; Wilder RSI14 seeded by 14 changes; Wilder ATR14 seeded by 14 true ranges after the first bar. Flat RSI=50. Only supplied closed bars are used.",
    }


def _safe(value: object) -> str:
    text = html.escape(str(value), quote=True)
    for character in ("\\", chr(96), "*", "_", "[", "]", "|", "#", "!"):
        text = text.replace(character, "\\" + character)
    return text


def to_markdown(report: dict) -> str:
    lines = ["# OpenMarket AI - Historical Research", "", f"Mode: {report['mode']}",
             "Signal: ABSTAIN (research only)", "", "## Dataset and provenance", ""]
    for key, value in report["metadata"].items():
        lines.append(f"- {key}: {_safe(value)}")
    for key, value in report["data"].items():
        lines.append(f"- {key}: {_safe(value)}")
    lines.extend(["", "## Computed observations", "", report["observation"], ""])
    for key, value in report["indicators"].items():
        lines.append(f"- {key}: {value:.6f}")
    lines.extend(["", "## Conditional research scenarios", ""])
    for key, value in report["scenarios"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Limitations", ""])
    lines.extend(f"- {warning}" for warning in report["warnings"])
    lines.extend(["", "## Methodology", "", report["methodology"],
                  "", f"Software version: {report['software_version']}", ""])
    return "\n".join(lines)
