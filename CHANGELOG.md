# Release notes

## 0.2.0 - Offline historical research MVP

Added local UTF-8 OHLCV CSV validation, explicit instrument/source context, trailing SMA20/SMA50, Wilder RSI14 and ATR14, historical alignment observations, and conditional research descriptions. Reports include data timestamps, input SHA-256, version, limitations, and an ABSTAIN status.

Added Markdown/JSON export with no-overwrite behavior, a clearly synthetic bundled example, numeric and invalid-data tests, and Persian end-user instructions. The no-argument demo remains available.

This is a usable offline research MVP. It does not implement the entire long-term AI platform vision. Live data providers, news and fundamentals, model adapters, backtesting, and a public service remain future work. No orders or account integration are present.
