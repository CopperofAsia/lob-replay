from datetime import datetime
from src.lob_replay.config import resolve_paths
from src.lob_replay.io.loader import load_all
from src.lob_replay.engine.replay_engine import ReplayEngine

def test_query_runs():
    paths = resolve_paths("data")
    level2, orders, trades = load_all(paths.level2_csv, paths.order_csv, paths.trade_csv)
    eng = ReplayEngine(level2, orders, trades)
    out = eng.query("SH.510050", datetime.fromisoformat("2024-02-07T09:30:05+08:00"))
    assert out["symbol"] == "SH.510050"
    assert len(out["bids"]) == 10
    assert len(out["asks"]) == 10

if __name__ == "__main__":
    test_query_runs()