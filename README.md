# LOB Replay (snapshot + order + trade)

Reconstruct **top-10 LOB** at any second using:
- 3-second snapshots (`df_level2.csv`)
- order events (`df_order.csv`): place/cancel
- trade events (`df_trade.csv`)

## Quickstart

```bash
python -m src.lob_replay.cli.main --symbol SH.510050 --ts "2024-02-07 09:30:05" --data-dir data/sample
```

You can change "2024-02-07 09:30:05" to other time strings you want.

## Output

A JSON-like dict with:
- `last` / `volume` / `amount`
- `bids[10]`, `asks[10]` each item: `{"price": float, "qty": int}`
