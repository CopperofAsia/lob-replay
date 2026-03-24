from __future__ import annotations
import pandas as pd
from datetime import datetime
from ..book.orderbook import OrderBook
from ..types import LOBSnapshot

class ReplayEngine:
    """
    给定一只股票（或合约）的：
    某个时间点之前最近的一条 L2 快照（top10 档），以及
    这之后一段时间内的订单、成交事件，
    在内存里“回放”这段时间的订单簿变化，返回目标时间点的盘口快照。
    """
    def __init__(self, level2: pd.DataFrame, orders: pd.DataFrame, trades: pd.DataFrame):
        self.level2 = level2
        self.orders = orders
        self.trades = trades


    def snapshot_at(self, symbol: str, t: datetime) -> dict:
        """返回 <=t 的最近快照行（dict）。"""
        df = self.level2
        d = df[(df["symbol"] == symbol) & (df["dt"] <= t)]
        if d.empty:
            raise ValueError("no snapshot <= t")
        return d.iloc[-1].to_dict()

    def events_between(self, symbol: str, t0: datetime, t1: datetime):
        """生成 (t0, t1] 内的 order/trade 事件，按时间排序后合并回放。"""
        o = self.orders[(self.orders["symbol"] == symbol) & (self.orders["dt"] > t0) & (self.orders["dt"] <= t1)]
        x = self.trades[(self.trades["symbol"] == symbol) & (self.trades["dt"] > t0) & (self.trades["dt"] <= t1)]

        # 统一成同一列名便于 merge-sort
        o2 = o.assign(kind="order")
        x2 = x.assign(kind="trade")
        e = pd.concat([o2, x2], ignore_index=True).sort_values(["dt", "kind"])
        return e

    def query(self, symbol: str, t: datetime) -> LOBSnapshot:
        snap = self.snapshot_at(symbol, t)
        t0 = snap["dt"]

        book = OrderBook()
        book.reset_from_snapshot(snap)

        e = self.events_between(symbol, t0, t)
        for row in e.itertuples(index=False):
            if row.kind == "order":
                if row.order_type == "place":
                    book.add_order(row.number, row.side, float(row.price), int(row.quantity))
                elif row.order_type == "cancel":
                    book.cancel_order(row.number)
            else:  # trade
                book.last = float(row.price)
                book.volume += int(row.quantity)
                book.amount += float(row.price) * int(row.quantity)

                # 成交扣减两边订单（若订单不存在则忽略，保证健壮性）
                book.fill_order(row.buy_no, int(row.quantity))
                book.fill_order(row.sell_no, int(row.quantity))

        bids, asks = book.top10()
        return {
            "symbol": symbol,
            "ts": t.isoformat(),
            "last": book.last,
            "volume": book.volume,
            "amount": book.amount,
            "bids": bids,
            "asks": asks,
        }