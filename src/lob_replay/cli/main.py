from __future__ import annotations
import argparse
import json
import pandas as pd
from datetime import datetime
from ..config import resolve_paths, DEFAULT_TZ
from ..io.loader import load_all
from ..engine.replay_engine import ReplayEngine

def main():
    p = argparse.ArgumentParser(description="LOB replay query (top10) using snapshot+order+trade.")
    p.add_argument("--symbol", required=True, help="e.g. SH.510050")
    p.add_argument("--ts", required=True, help='e.g. "2024-02-07 09:30:05" (local exchange time)')
    p.add_argument("--data-dir", default="data", help="dir containing df_level2.csv/df_order.csv/df_trade.csv")
    p.add_argument("--tz", default=DEFAULT_TZ, help="timezone name")
    args = p.parse_args()

    paths = resolve_paths(args.data_dir)
    level2, orders, trades = load_all(paths.level2_csv, paths.order_csv, paths.trade_csv, tz=args.tz)
    eng = ReplayEngine(level2, orders, trades)

    # t = datetime.fromisoformat(args.ts)
    t = pd.Timestamp(args.ts)
    if t.tzinfo is None:
        t = t.tz_localize(args.tz)   # 默认为 DEFAULT_TZ
    else:
        t = t.tz_convert(args.tz)

    out = eng.query(args.symbol, t)
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
