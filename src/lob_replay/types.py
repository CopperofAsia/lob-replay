from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, TypedDict

Side = Literal["buy", "sell"]
OrderType = Literal["place", "cancel"]

@dataclass(frozen=True)
class OrderEvent:
    ts: datetime
    symbol: str
    order_no: str
    side: Side
    price: float
    qty: int
    typ: OrderType  # place/cancel

@dataclass(frozen=True)
class TradeEvent:
    ts: datetime
    symbol: str
    price: float
    qty: int
    buy_no: str
    sell_no: str

class LOBSnapshot(TypedDict):
    symbol: str
    ts: str
    last: float
    volume: int
    amount: float
    bids: list[dict]   # [{"price":..., "qty":...}] len=10
    asks: list[dict]   # [{"price":..., "qty":...}] len=10
