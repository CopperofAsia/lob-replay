from __future__ import annotations
from datetime import datetime
import pandas as pd
from pandas import Timestamp

def _zfill9(x: int | str) -> str:
    s = str(int(x))  
    return s.zfill(9)  # 补齐9位（不足则在左侧补0）

def parse_hhmmssmmm(hhmmssmmm: int | str) -> tuple[int, int, int, int]:
    """
    Parse an exchange-style integer time stamp: HHMMSSmmm (9 digits).

    Example:
      84501000 -> "084501000" -> 8:45:01.000
    """
    s = _zfill9(hhmmssmmm)
    hh = int(s[0:2])
    mm = int(s[2:4])
    ss = int(s[4:6])
    ms = int(s[6:9])
    return hh, mm, ss, ms

def make_timestamp(yyyymmdd: int | str, hhmmssmmm: int | str, tz: str = "Asia/Shanghai") -> Timestamp:
    ymd = str(int(yyyymmdd))
    y, m, d = int(ymd[0:4]), int(ymd[4:6]), int(ymd[6:8])
    hh, mm, ss, ms = parse_hhmmssmmm(hhmmssmmm)
    # Python datetime 的最后一个参数是微秒，不是毫秒，所以乘以1000
    ts = pd.Timestamp(datetime(y, m, d, hh, mm, ss, ms * 1000))  
    if ts.tzinfo is None:
        # 如果时区信息为空，则本地化
        ts = ts.tz_localize(tz)
    else:
        # 如果时区信息不为空，则转换时区
        ts = ts.tz_convert(tz)
    return ts

def ensure_datetime_col(df: pd.DataFrame, date_col: str, time_col: str, out_col: str = "dt", tz: str = "Asia/Shanghai") -> pd.DataFrame:
    """
    给一个 DataFrame 自动生成一个“带时区信息的时间列”（默认叫 dt），
    兼容两种常见的原始时间格式。
    Create a timezone-aware datetime column.
    Supports two common formats found in the provided CSVs:
    1) `date_col` is yyyymmdd int and `time_col` is HHMMSSmmm int (e.g. level2 `time`)
    2) `time_col` is already an ISO datetime string with timezone (e.g. order_time/trade_time)
       In this case `date_col` is ignored.
    """
    # 如果已经存在该列，则直接返回
    if out_col in df.columns:
        return df

    # Case (2): already datetime-like strings
    # 条件 "-" in s and ":" in s 粗略判断：
    # 这个字符串长得像 "2024-02-07 09:30:05" 这种 ISO 格式时间，
    # 也可能是 "2024-02-07T09:30:05+08:00" 等。
    sample = df[time_col].dropna().astype(str).head(5).tolist()
    if any(("-" in s and ":" in s) for s in sample):
        dt = pd.to_datetime(df[time_col], errors="coerce", utc=False)
        # If it comes with tz, keep it; otherwise localize
        if getattr(dt.dt, "tz", None) is None:
            dt = dt.dt.tz_localize(tz)
        else:
            dt = dt.dt.tz_convert(tz)
        df[out_col] = dt
        return df

    # Case (1): date + HHMMSSmmm
    df[out_col] = [make_timestamp(d, t, tz=tz) for d, t in zip(df[date_col].to_numpy(), df[time_col].to_numpy())]
    return df

def floor_to_second(ts: Timestamp) -> Timestamp:
    # 向下取整到秒，毫秒、微秒部分被截掉
    return ts.floor("s")

def floor_to_3s(ts: Timestamp) -> Timestamp:
    # 用整除把当前时间的纳秒数向下取整到最接近的 3 秒整数倍
    epoch = ts.value  # ns
    step = 3 * 1_000_000_000
    floored = (epoch // step) * step
    return pd.Timestamp(floored, tz=ts.tz)
