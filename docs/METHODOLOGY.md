# Research methodology and limits (v0.2)

The program has no network adapters, AI inference, broker APIs, or order execution. It computes deterministic observations on user-supplied closed bars. Context and licensing are user declarations, not independently verified facts. The bundled 80-bar daily CSV is invented software test data, distributed under this repository's MIT license.

## Calculation conventions

- SMA20 and SMA50 use trailing arithmetic means of close. Reports require at least 50 bars.
- RSI14 uses the first 14 close-to-close gains and losses as arithmetic seeds, followed by Wilder smoothing: new average = (previous average * 13 + new observation) / 14. With no gains or losses the project returns 50; no losses with positive gains returns 100. Initialization can differ from other platforms.
- ATR14 takes true range = max(high-low, abs(high-previous close), abs(low-previous close)). The first bar supplies only a previous close. The next 14 true ranges seed an arithmetic mean; later bars use Wilder smoothing. ATR is expressed in the input price units and is not directional.
- Observed alignment compares last close, SMA20, and SMA50. Three conditional descriptions are hypotheses, not forecasts or actionable trading signals. Signal remains ABSTAIN.
- No bars are imputed. Interval multiples are disclosed; irregular spacing could reflect valid closures or missing data. A calendar, corporate actions, contract rolls, and daylight-saving transitions are not modeled. The caller must standardize the input appropriately.
- No adjusted-price treatment is inferred. No volume analytics or exchange-wide volume claims are made.
- No backtest or trading costs are computed. There is no claim of predictive validity or profitability.

## References

Formula references checked on 2026-11-11:

- [TradingView RSI documentation](https://www.tradingview.com/support/solutions/43000502338-relative-strength-index-rsi/)
- [TradingView ATR documentation](https://www.tradingview.com/support/solutions/43000501823-average-true-range-atr/)

The project documents its own initialization and flat-series conventions rather than claiming bit-for-bit equivalence to any chart platform.

## Data contract

UTF-8 CSV, exact lowercase timestamp/open/high/low/close headers, optional volume. Timestamps must have explicit timezone offsets, normalize to UTC, be strictly increasing, and not be in the future when imported. Prices must be finite and positive, at most 1e12; low <= open/close <= high. Volume, if present, must be finite, nonnegative, and at most 1e12. Limits: 20 MiB and 100000 rows. Historical data freshness, authenticity, and licensing cannot be established by a checksum. The SHA-256 records exact input bytes for reproducibility.

## Release acceptance

Tests include hand-calculated arithmetic and Wilder updates, timezone normalization, rejected malformed data, provenance, missing intervals, warm-up, offline example execution, required context, and refusal to overwrite reports. CI installs the package and runs tests and both entry points on Linux/Python 3.10 and 3.14 and Windows/Python 3.14. A wheel installation must include the synthetic fixture. No private or licensed market datasets are committed.
