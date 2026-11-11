"""Independent numeric checks and invalid-data/CLI regression coverage."""
import hashlib
import json
import subprocess
import sys
from dataclasses import replace
from datetime import datetime, timezone
from importlib.resources import files
import pytest
from openmarket_ai.historical import Metadata, build_report, to_markdown
from openmarket_ai.indicators import atr, rsi, sma
from openmarket_ai.market_data import Bar, Dataset, parse_csv

HEADER = "timestamp,open,high,low,close,volume\n"
ROW = "2020-01-01T00:00:00Z,100,102,99,101,0\n"
META = Metadata("XAUUSD", "test fixture", "MIT", "test", "synthetic", "USD", "1d", True)


def fixture():
    return parse_csv(files("openmarket_ai").joinpath("fixtures/synthetic_ohlcv.csv").read_bytes())


def test_trailing_sma_known_arithmetic():
    assert sma(list(range(1, 61)), 20) == 50.5
    assert sma(list(range(1, 61)), 50) == 35.5


def test_wilder_rsi_seed_and_recursive_update():
    assert rsi([1, 2, 4, 3], 3) == pytest.approx(75)
    assert rsi([1, 2, 4, 3, 5], 3) == pytest.approx(100 - 100 / 7)
    assert rsi([10] * 15) == 50
    assert rsi(list(range(1, 16))) == 100
    assert rsi(list(range(15, 0, -1))) == 0


def test_atr_includes_previous_close_gap():
    stamp = datetime(2020, 1, 1, tzinfo=timezone.utc)
    bars = [Bar(stamp, 100, 102, 99, 101), Bar(stamp, 110, 112, 109, 110),
            Bar(stamp, 108, 110, 107, 108)]
    # TRs are 11 and 3, so their arithmetic seed is 7.
    assert atr(bars, 2) == 7
    assert atr(bars + [Bar(stamp, 108, 109, 107, 108)], 2) == 4.5


@pytest.mark.parametrize("period", [0, -1, 1.5, True])
def test_invalid_period(period):
    with pytest.raises(ValueError):
        sma([1, 2, 3], period)


@pytest.mark.parametrize("values", [[1], [float("nan")] * 20, [float("inf")] * 20, [0] * 20])
def test_invalid_indicator_input(values):
    with pytest.raises(ValueError):
        rsi(values)


def test_timezone_normalization_and_hash():
    raw = (HEADER + ROW.replace("00:00:00Z", "03:30:00+03:30")).encode()
    result = parse_csv(raw)
    assert result.bars[0].timestamp == datetime(2020, 1, 1, tzinfo=timezone.utc)
    assert result.sha256 == hashlib.sha256(raw).hexdigest()
    assert result.bars[0].volume == 0


def test_optional_volume():
    result = parse_csv(b"timestamp,open,high,low,close\n2020-01-01T00:00:00Z,100,102,99,101\n")
    assert result.bars[0].volume is None


@pytest.mark.parametrize("raw", [
    b"", HEADER.encode(), b"timestamp,open,high,low,close,close\n",
    (HEADER + ROW + ROW).encode(),
    (HEADER + ROW.replace("00:00:00Z", "00:00:00")).encode(),
    (HEADER + ROW.replace("2020", "2999")).encode(),
    (HEADER + ROW.replace(",102,", ",NaN,")).encode(),
    (HEADER + ROW.replace(",99,", ",-99,")).encode(),
    (HEADER + ROW.replace(",102,", ",100,")).encode(),
    (HEADER + ROW.replace(",0\n", ",-1\n")).encode(),
    (HEADER + ROW.replace(",0\n", ",inf\n")).encode(),
    (HEADER + ROW.replace(",100,", ",0,")).encode(),
    (HEADER + ROW.replace(",0\n", "\n")).encode(),
    (HEADER + ROW.replace(",0\n", ",0,extra\n")).encode(), b"\xff\xfe",
])
def test_bad_csv_is_rejected(raw):
    with pytest.raises(ValueError):
        parse_csv(raw)


def test_reverse_order_is_rejected():
    with pytest.raises(ValueError, match="increasing"):
        parse_csv((HEADER + ROW.replace("01-01", "01-02") + ROW).encode())


def test_resource_limits(monkeypatch):
    import openmarket_ai.market_data as module
    monkeypatch.setattr(module, "MAX_BYTES", 4)
    with pytest.raises(ValueError, match="MiB"):
        parse_csv((HEADER + ROW).encode())
    monkeypatch.setattr(module, "MAX_BYTES", 1000)
    monkeypatch.setattr(module, "MAX_ROWS", 0)
    with pytest.raises(ValueError, match="rows"):
        parse_csv((HEADER + ROW).encode())


def test_report_provenance_and_safety():
    data = fixture()
    report = build_report(data, META)
    assert report["signal"] == "ABSTAIN"
    assert report["mode"] == "SYNTHETIC_RESEARCH"
    assert report["data"]["sha256"] == data.sha256
    assert report["data"]["bar_count"] == 80
    assert report["data"]["freshness"] == "HISTORICAL_NOT_VERIFIED_LIVE"
    assert any("SYNTHETIC DATA" in item for item in report["warnings"])
    assert "No entry, stop-loss" in to_markdown(report)
    assert json.loads(json.dumps(report, allow_nan=False)) == report


def test_causal_prefix_and_warmup():
    data = fixture()
    prefix = Dataset(data.bars[:50], "prefix")
    before = build_report(prefix, META)
    build_report(data, META)
    assert build_report(prefix, META) == before
    with pytest.raises(ValueError, match="50"):
        build_report(Dataset(data.bars[:49], "short"), META)


def test_gap_disclosure_and_timeframe_validation():
    data = fixture()
    gap = Dataset(data.bars[:30] + data.bars[31:], "gap")
    assert build_report(gap, META)["data"]["irregular_intervals"] == 1
    with pytest.raises(ValueError, match="timeframe"):
        build_report(data, replace(META, timeframe="7d"))
    with pytest.raises(ValueError, match="source"):
        build_report(data, replace(META, source="bad\nmetadata"))


def test_metadata_markup_is_escaped():
    report = build_report(fixture(), replace(META, source="![img](https://example.com/x)"))
    assert "\\!\\[img\\]" in to_markdown(report)


def cli(*args):
    return subprocess.run([sys.executable, "-m", "openmarket_ai", *args],
                          capture_output=True, text=True, timeout=15, check=False)


def test_example_cli_and_export(tmp_path):
    output = tmp_path / "report.json"
    result = cli("--example", "--format", "json", "--output", str(output))
    assert result.returncode == 0, result.stderr
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["mode"] == "SYNTHETIC_RESEARCH"
    assert report["metadata"]["symbol"] == "SYNTHETIC"
    original = output.read_bytes()
    assert cli("--example", "--output", str(output)).returncode == 2
    assert output.read_bytes() == original


def test_user_csv_requires_provenance_and_closed_bars(tmp_path):
    source = tmp_path / "bars.csv"
    source.write_bytes(files("openmarket_ai").joinpath("fixtures/synthetic_ohlcv.csv").read_bytes())
    assert cli("--csv", str(source)).returncode == 2
    args = ("--csv", str(source), "--source", "test", "--data-license", "MIT",
            "--venue", "none", "--instrument-type", "test", "--quote-currency", "USD",
            "--timeframe", "1d")
    assert cli(*args).returncode == 2
    result = cli(*args, "--closed-bars", "--format", "json")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["mode"] == "HISTORICAL_RESEARCH"
    assert json.loads(result.stdout)["signal"] == "ABSTAIN"


def test_example_uses_no_network(monkeypatch):
    import socket
    from openmarket_ai.__main__ import main
    def blocked(*args, **kwargs):
        raise AssertionError("network forbidden")
    monkeypatch.setattr(socket, "socket", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
    assert main(["--example"]) == 0


def test_malformed_csv_header():
    with pytest.raises(ValueError, match="CSV"):
        parse_csv(b'"unterminated')


def test_timestamp_underflow():
    with pytest.raises(ValueError, match="timestamp"):
        parse_csv((HEADER + ROW.replace("2020-01-01T00:00:00Z", "0001-01-01T00:00:00+01:00")).encode())
