# OpenMarket AI - Historical Research

Mode: SYNTHETIC_RESEARCH
Signal: ABSTAIN (research only)

## Dataset and provenance

- symbol: SYNTHETIC
- source: bundled invented fixture
- data_license: MIT synthetic fixture
- venue: none
- instrument_type: synthetic
- quote_currency: DEMO
- timeframe: 1d
- synthetic: True
- sha256: 88277b767af920c250c13c9bdb11b8b3479871f8ebccf21d30e060ab27e6c56d
- bar_count: 80
- first_timestamp_utc: 2020-01-01T00:00:00+00:00
- last_timestamp_utc: 2020-03-20T00:00:00+00:00
- last_close: 109.4672
- irregular_intervals: 0
- freshness: HISTORICAL\_NOT\_VERIFIED\_LIVE
- closed_bars: SYNTHETIC\_FIXED\_FIXTURE

## Computed observations

Last close > SMA20 > SMA50 (upward historical alignment).

- sma20: 106.472185
- sma50: 105.44072
- rsi14: 80.2876952154
- atr14: 2.2

## Conditional research scenarios

- bullish: Research hypothesis only: a later closed bar above SMA20 above SMA50 would maintain upward alignment.
- bearish: Research hypothesis only: a later closed bar below SMA20 below SMA50 would maintain downward alignment.
- neutral: Mixed or equal moving averages indicate no directional alignment under this rule.

## Limitations

- SYNTHETIC DATA: invented fixture for software demonstrations, not market history.
- Historical observations only; data freshness and source authenticity are not independently verified.
- Metadata and closed-bar status are user declarations; licensing is not verified by this software.
- Indicators share price inputs and are not independent confirmations or proof of an edge.
- RSI extremes are not automatic reversal signals; ATR measures range, not direction.
- No news, fundamentals, AI inference, backtest, execution costs, or profitability evaluation.
- No entry, stop-loss, price targets, orders, or personalized investment advice.

## Methodology

Trailing SMA20/SMA50; Wilder RSI14 seeded by 14 changes; Wilder ATR14 seeded by 14 true ranges after the first bar. Flat RSI=50. Only supplied closed bars are used.

Software version: 0.2.0
