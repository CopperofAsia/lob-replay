from __future__ import annotations
from pathlib import Path
import pandas as pd
from ..timeutils import ensure_datetime_col
from .validators import drop_invalid_price_qty, dedup, standardize_side, standardize_order_type
from ..config import DEFAULT_TZ

def load_level2(path: str | Path, tz: str = DEFAULT_TZ) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = ensure_datetime_col(df, date_col="date", time_col="time", out_col="dt", tz=tz)
    # 按股票代码、时间排序
    df = df.sort_values(["symbol", "dt"]).reset_index(drop=True)
    # 去重
    df = dedup(df, ["symbol", "dt"])
    return df

def load_orders(path: str | Path, tz: str = DEFAULT_TZ) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = ensure_datetime_col(df, date_col="date", time_col="order_time", out_col="dt", tz=tz)
    df = standardize_side(df, "side")
    df = standardize_order_type(df, "order_type")
    df = drop_invalid_price_qty(df, price_col="price", qty_col="quantity")
    df["number"] = df["number"].astype(str)
    df = df.sort_values(["symbol", "dt"]).reset_index(drop=True)
    df = dedup(df, ["symbol", "dt", "number", "order_type"])
    return df

def load_trades(path: str | Path, tz: str = DEFAULT_TZ) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = ensure_datetime_col(df, date_col="date", time_col="trade_time", out_col="dt", tz=tz)
    df = drop_invalid_price_qty(df, price_col="price", qty_col="quantity")
    df["buy_no"] = df["buy_no"].astype(str)
    df["sell_no"] = df["sell_no"].astype(str)
    df = df.sort_values(["symbol", "dt"]).reset_index(drop=True)
    df = dedup(df, ["symbol", "dt", "number"])
    return df

def load_all(level2_csv: str | Path, order_csv: str | Path, trade_csv: str | Path, tz: str = DEFAULT_TZ):
    level2 = load_level2(level2_csv, tz=tz)
    orders = load_orders(order_csv, tz=tz)
    trades = load_trades(trade_csv, tz=tz)
    return level2, orders, trades
