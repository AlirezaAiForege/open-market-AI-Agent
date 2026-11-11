"""Strict local OHLCV ingestion; no network or brokerage access."""
import csv
import hashlib
import io
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

MAX_BYTES = 20 * 1024 * 1024
MAX_ROWS = 100_000
TIMEFRAMES = {"1m": 60, "5m": 300, "15m": 900, "30m": 1800,
              "1h": 3600, "4h": 14400, "1d": 86400, "7d": 604800}


@dataclass(frozen=True)
class Bar:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None


@dataclass(frozen=True)
class Dataset:
    bars: tuple[Bar, ...]
    sha256: str


def _number(value: str, field: str, line: int) -> float:
    try:
        number = float(value)
    except (ValueError, TypeError) as exc:
        raise ValueError(f"row {line}: invalid {field}") from exc
    if not math.isfinite(number) or number > 1e12 or number < 0:
        raise ValueError(f"row {line}: {field} must be finite and within supported bounds")
    if field != "volume" and number == 0:
        raise ValueError(f"row {line}: prices must be positive")
    return number


def parse_csv(raw: bytes, *, now: datetime | None = None) -> Dataset:
    """Require UTF-8, positive finite prices, and increasing aware timestamps."""
    if len(raw) > MAX_BYTES:
        raise ValueError("CSV exceeds 20 MiB")
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("CSV must use UTF-8 encoding") from exc
    reader = csv.DictReader(io.StringIO(text), strict=True)
    required = {"timestamp", "open", "high", "low", "close"}
    try:
        fields = reader.fieldnames or []
    except csv.Error as exc:
        raise ValueError(f"invalid CSV header: {exc}") from exc
    if len(fields) != len(set(fields)) or set(fields) not in (required, required | {"volume"}):
        raise ValueError("CSV needs timestamp,open,high,low,close and optional volume headers")
    cutoff = now if now is not None else datetime.now(timezone.utc)
    if cutoff.tzinfo is None or cutoff.utcoffset() is None:
        raise ValueError("now must include a timezone")
    bars = []
    try:
        for line, row in enumerate(reader, start=2):
            if len(bars) >= MAX_ROWS:
                raise ValueError("CSV exceeds 100000 rows")
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"row {line}: wrong number of columns")
            try:
                stamp = datetime.fromisoformat(row["timestamp"].strip().replace("Z", "+00:00"))
            except ValueError as exc:
                raise ValueError(f"row {line}: invalid ISO timestamp") from exc
            if stamp.tzinfo is None or stamp.utcoffset() is None:
                raise ValueError(f"row {line}: timestamp must include a timezone")
            try:
                stamp = stamp.astimezone(timezone.utc)
            except (OverflowError, ValueError) as exc:
                raise ValueError(f"row {line}: timestamp outside supported range") from exc
            if stamp > cutoff:
                raise ValueError(f"row {line}: future timestamps are not historical data")
            if bars and stamp <= bars[-1].timestamp:
                raise ValueError(f"row {line}: timestamps must be unique and increasing")
            prices = {key: _number(row[key], key, line) for key in ("open", "high", "low", "close")}
            if not prices["low"] <= min(prices["open"], prices["close"]) <= max(prices["open"], prices["close"]) <= prices["high"]:
                raise ValueError(f"row {line}: inconsistent OHLC prices")
            volume = _number(row["volume"], "volume", line) if "volume" in row else None
            bars.append(Bar(timestamp=stamp, volume=volume, **prices))
    except csv.Error as exc:
        raise ValueError(f"invalid CSV: {exc}") from exc
    if not bars:
        raise ValueError("CSV has no data rows")
    return Dataset(tuple(bars), hashlib.sha256(raw).hexdigest())


def load_csv(path: str | Path) -> Dataset:
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    return parse_csv(raw)
