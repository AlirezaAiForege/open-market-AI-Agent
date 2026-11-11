"""Trailing indicators with explicit Wilder initialization and no future bars."""
import math
from collections.abc import Sequence
from openmarket_ai.market_data import Bar


def _validate(values: Sequence[float], period: int, extra: int = 0) -> None:
    """Reject invalid periods, insufficient history, and unsupported prices."""
    if isinstance(period, bool) or not isinstance(period, int) or period < 1:
        raise ValueError("period must be a positive integer")
    if len(values) < period + extra:
        raise ValueError("not enough bars for indicator warm-up")
    if any(not math.isfinite(x) or x <= 0 or x > 1e12 for x in values):
        raise ValueError("prices must be finite, positive, and at most 1e12")


def sma(values: Sequence[float], period: int) -> float:
    """Arithmetic mean of the last period closes."""
    _validate(values, period)
    return math.fsum(values[-period:]) / period


def rsi(values: Sequence[float], period: int = 14) -> float:
    """Wilder RSI: seed period changes, then alpha=1/period; flat RSI=50."""
    _validate(values, period, extra=1)
    changes = [b - a for a, b in zip(values, values[1:])]
    gain = math.fsum(max(x, 0) for x in changes[:period]) / period
    loss = math.fsum(max(-x, 0) for x in changes[:period]) / period
    for change in changes[period:]:
        gain = (gain * (period - 1) + max(change, 0)) / period
        loss = (loss * (period - 1) + max(-change, 0)) / period
    if gain == loss == 0:
        return 50.0
    if loss == 0:
        return 100.0
    return 100 - 100 / (1 + gain / loss)


def atr(bars: Sequence[Bar], period: int = 14) -> float:
    """Wilder ATR seeded by period true ranges after the first previous-close bar."""
    _validate([bar.close for bar in bars], period, extra=1)
    ranges = []
    for previous, bar in zip(bars, bars[1:]):
        _validate([bar.low, bar.high, bar.open], 1)
        if not bar.low <= min(bar.open, bar.close) <= max(bar.open, bar.close) <= bar.high:
            raise ValueError("inconsistent OHLC prices")
        ranges.append(max(bar.high - bar.low, abs(bar.high - previous.close), abs(bar.low - previous.close)))
    average = math.fsum(ranges[:period]) / period
    for value in ranges[period:]:
        average = (average * (period - 1) + value) / period
    return average
