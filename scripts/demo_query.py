from datetime import datetime
from zoneinfo import ZoneInfo

from src.lob_replay.config import resolve_paths, DEFAULT_TZ
from src.lob_replay.io.loader import load_all
from src.lob_replay.engine.replay_engine import ReplayEngine

if __name__ == "__main__":
    paths = resolve_paths("data/sample")
    level2, orders, trades = load_all(paths.level2_csv, paths.order_csv, paths.trade_csv)
    eng = ReplayEngine(level2, orders, trades)

    symbol = "SH.510050"
    t = datetime.fromisoformat("2024-02-07 09:30:05").replace(tzinfo=ZoneInfo(DEFAULT_TZ))
    out = eng.query(symbol, t)
    print(out)
