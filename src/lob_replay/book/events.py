from __future__ import annotations
from .orderbook import OrderBook

"""
apply_order 和 apply_trade 是两个辅助函数，
分别用来处理订单事件和成交事件。
"""

def apply_order(book: OrderBook, row) -> None:
    if row.order_type == "place":
        book.add_order(str(row.number), str(row.side), float(row.price), int(row.quantity))
    elif row.order_type == "cancel":
        book.cancel_order(str(row.number))

def apply_trade(book: OrderBook, row) -> None:
    price = float(row.price)
    qty = int(row.quantity)
    book.last = price
    book.volume += qty
    book.amount += price * qty

    # decrement both sides if present in our in-memory mapping
    book.fill_order(str(row.buy_no), qty)
    book.fill_order(str(row.sell_no), qty)
