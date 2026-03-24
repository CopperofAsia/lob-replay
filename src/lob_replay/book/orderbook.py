from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Tuple, Literal

Side = Literal["buy", "sell"]

@dataclass
class OrderBook:
    """
    OrderBook 用来在内存里维护一个简单的限价订单簿（10 档行情），
    并支持用订单事件去更新它。
    保存盘口聚合量：
    bid_qty: 每个买价 → 该价位累积的买量。
    ask_qty: 每个卖价 → 该价位累积的卖量。
    维护所有未成交订单：
    orders: 订单号 → (side, price, qty) 即 买卖方向、价格、数量
    """
    bid_qty: Dict[float, int] = field(default_factory=dict)
    ask_qty: Dict[float, int] = field(default_factory=dict)
    orders: Dict[str, Tuple[Side, float, int]] = field(default_factory=dict)

    last: float = 0.0
    volume: int = 0
    amount: float = 0.0

    def reset_from_snapshot(self, snap_row: dict) -> None:
        """
        订单簿内部只会重建“快照里给出的前 10 档聚合量”。
        如果真实市场有更深的挂单（第 11 档、第 20 档…），快照本身就没记录，
        这个函数也就无法恢复，等价于被“抹去”。
        """
        self.bid_qty.clear()
        self.ask_qty.clear()
        self.orders.clear()  # given snapshot csv has no per-order mapping

        self.last = float(snap_row.get("last", 0.0))
        self.volume = int(snap_row.get("volume", 0))
        self.amount = float(snap_row.get("amount", 0.0))

        for i in range(1, 11):
            bp = float(snap_row.get(f"bp{i}", 0.0) or 0.0)
            bv = int(snap_row.get(f"bv{i}", 0) or 0)
            ap = float(snap_row.get(f"ap{i}", 0.0) or 0.0)
            av = int(snap_row.get(f"av{i}", 0) or 0)

            if bp > 0 and bv > 0:
                self.bid_qty[bp] = self.bid_qty.get(bp, 0) + bv
            if ap > 0 and av > 0:
                self.ask_qty[ap] = self.ask_qty.get(ap, 0) + av

    def add_order(self, order_no: str, side: Side, price: float, qty: int) -> None:
        if qty <= 0 or price <= 0:
            return
        self.orders[order_no] = (side, price, qty)
        # 先根据买卖方向选出要操作的那一侧盘口字典，
        # 然后后面的代码只对这个局部变量 book 做统一处理，
        # 避免重复写 if/else。
        book = self.bid_qty if side == "buy" else self.ask_qty
        book[price] = book.get(price, 0) + qty

    def cancel_order(self, order_no: str) -> None:
        """
        取消订单：
        1. 先尝试从 orders 里删除该订单（pop 操作）。
        2. 如果 orders 里没有这个订单（pop 返回 None），直接返回。
        3. 如果 orders 里有这个订单，则获取它的 (side, price, qty) 信息。
        4. 根据买卖方向选出要操作的那一侧盘口字典，然后对该盘口字典执行扣减操作。
        5. 如果扣减后该价位累积量归零，则从盘口字典里移除该价位。
        """
        info = self.orders.pop(order_no, None)
        if info is None:
            return
        side, price, qty = info
        book = self.bid_qty if side == "buy" else self.ask_qty
        book[price] = max(0, book.get(price, 0) - qty)
        if book.get(price, 0) == 0:
            book.pop(price, None)

    def fill_order(self, order_no: str, fill_qty: int) -> None:
        """
        成交扣减两边订单（若订单不存在则忽略，保证健壮性）
        使用时需对 buy_no 和 sell_no 都调用一次，
        因为一个成交同时涉及买方和卖方。
        """
        if fill_qty <= 0:
            return
        info = self.orders.get(order_no)
        if info is None:
            return
        side, price, remain = info
        dec = min(remain, fill_qty)
        remain2 = remain - dec

        book = self.bid_qty if side == "buy" else self.ask_qty
        book[price] = max(0, book.get(price, 0) - dec)
        if book.get(price, 0) == 0:
            book.pop(price, None)

        if remain2 <= 0:
            self.orders.pop(order_no, None)
        else:
            self.orders[order_no] = (side, price, remain2)

    def top10(self):
        # 把 bid_qty 按价格从高到低排序取前 10 档。
        bids = sorted(self.bid_qty.items(), key=lambda x: x[0], reverse=True)[:10]
        # 把 ask_qty 按价格从低到高排序取前 10 档。
        asks = sorted(self.ask_qty.items(), key=lambda x: x[0])[:10]
        bid_list = [{"price": float(p), "qty": int(q)} for p, q in bids]
        ask_list = [{"price": float(p), "qty": int(q)} for p, q in asks]
        while len(bid_list) < 10:
            bid_list.append({"price": 0.0, "qty": 0})
        while len(ask_list) < 10:
            ask_list.append({"price": 0.0, "qty": 0})
        return bid_list, ask_list
