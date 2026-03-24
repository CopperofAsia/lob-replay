from __future__ import annotations
import pandas as pd

def drop_invalid_price_qty(df: pd.DataFrame, price_col: str = "price", qty_col: str = "quantity") -> pd.DataFrame:
    if price_col in df.columns:
        df = df[df[price_col].notna()]
        df = df[df[price_col] > 0]
    if qty_col in df.columns:
        df = df[df[qty_col].notna()]
        df = df[df[qty_col] > 0]
    return df

def dedup(df: pd.DataFrame, subset: list[str]) -> pd.DataFrame:
    return df.drop_duplicates(subset=subset, keep="last") if subset else df

def standardize_side(df: pd.DataFrame, col: str = "side") -> pd.DataFrame:
    """
    side 统一成 "buy" 或 "sell"
    """
    if col not in df.columns:
        return df
    m = {"B": "buy", "S": "sell", "BUY": "buy", "SELL": "sell", "buy": "buy", "sell": "sell", 1: "buy", -1: "sell"}
    df[col] = df[col].map(lambda x: m.get(x, x))
    return df

def standardize_order_type(df: pd.DataFrame, col: str = "order_type") -> pd.DataFrame:
    """
    order_type 统一成 "place" 或 "cancel"
    """
    if col not in df.columns:
        return df
    m = {"A": "place", "D": "cancel", "place": "place", "cancel": "cancel", "NEW": "place", "CANCEL": "cancel"}
    df[col] = df[col].map(lambda x: m.get(x, x))
    return df
