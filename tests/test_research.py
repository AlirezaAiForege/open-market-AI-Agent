"""Verify report disclosure, validation, and the installed command line."""

import subprocess
import sys

import pytest

from openmarket_ai.research import create_demo_report


def test_demo_abstains_without_market_data():
    report = create_demo_report()
    assert report.symbol == "XAUUSD"
    assert report.mode == "DEMO"
    assert report.data_status == "NO_MARKET_DATA"
    assert report.signal == "ABSTAIN"
    text = report.to_markdown()
    assert "No market data was loaded" in text
    assert "No orders are placed" in text
    assert "Sources: none (offline demo)" in text
    assert "not personalized investment advice" in text


def test_symbol_normalization_and_reproducibility():
    assert create_demo_report("  btcusd  ") == create_demo_report("BTCUSD")
    assert create_demo_report().to_markdown() == create_demo_report().to_markdown()


@pytest.mark.parametrize("symbol", ["", "  ", "X" * 21, "XAU\nUSD", "<script>", "طلا"])
def test_invalid_symbols_are_rejected(symbol):
    with pytest.raises(ValueError):
        create_demo_report(symbol)


def test_non_string_symbol_is_rejected():
    with pytest.raises(TypeError):
        create_demo_report(None)


def test_module_command_line():
    result = subprocess.run(
        [sys.executable, "-m", "openmarket_ai", "--symbol", "btcusd"],
        capture_output=True, text=True, check=False, timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert "Symbol: BTCUSD" in result.stdout
    assert "Signal: ABSTAIN" in result.stdout


def test_invalid_command_line_symbol():
    result = subprocess.run(
        [sys.executable, "-m", "openmarket_ai", "--symbol", ""],
        capture_output=True, text=True, check=False, timeout=10,
    )
    assert result.returncode == 2
    assert "symbol must contain" in result.stderr
