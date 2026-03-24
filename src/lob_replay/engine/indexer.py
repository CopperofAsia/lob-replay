from __future__ import annotations
import pandas as pd

def build_symbol_groups(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Split a big dataframe into per-symbol frames (sorted)."""
    out: dict[str, pd.DataFrame] = {}
    for sym, g in df.groupby("symbol", sort=False):
        out[str(sym)] = g.sort_values("dt").reset_index(drop=True)
    return out
