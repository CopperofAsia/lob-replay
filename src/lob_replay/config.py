from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path

DEFAULT_TZ = "Asia/Shanghai"

@dataclass(frozen=True)
class Paths:
    data_dir: Path
    level2_csv: Path
    order_csv: Path
    trade_csv: Path

def resolve_paths(data_dir: str | Path) -> Paths:
    d = Path(data_dir)
    return Paths(
        data_dir=d,
        level2_csv=d / "df_level2.csv",
        order_csv=d / "df_order.csv",
        trade_csv=d / "df_trade.csv",
    )
