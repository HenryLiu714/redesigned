"""Database package for trading infrastructure."""

from .connection import (
    engine,
    SessionLocal,
    Base,
    get_db,
    get_db_session,
    test_connection
)

from .models import (
    Fill,
    Order,
    Trade,
    OrderStatus,
    TradeStatus
)

from .operations import (
    # Fill operations
    create_fill,
    get_fill_by_id,
    get_fills_by_order,
    get_all_fills,

    # Order operations
    create_order,
    get_order_by_id,
    get_orders_by_symbol,
    get_orders_by_status,
    update_order_status,
    get_all_orders,

    # Trade operations
    create_trade,
    get_trade_by_id,
    get_trades_by_ticker,
    get_trades_by_strategy,
    get_trades_by_status,
    update_trade_status,
    get_all_trades,
    get_open_trades,
    close_trade
)

__all__ = [
    # Connection
    "engine",
    "SessionLocal",
    "Base",
    "get_db",
    "get_db_session",
    "test_connection",

    # Models
    "Fill",
    "Order",
    "Trade",
    "OrderStatus",
    "TradeStatus",

    # Fill operations
    "create_fill",
    "get_fill_by_id",
    "get_fills_by_order",
    "get_all_fills",

    # Order operations
    "create_order",
    "get_order_by_id",
    "get_orders_by_symbol",
    "get_orders_by_status",
    "update_order_status",
    "get_all_orders",

    # Trade operations
    "create_trade",
    "get_trade_by_id",
    "get_trades_by_ticker",
    "get_trades_by_strategy",
    "get_trades_by_status",
    "update_trade_status",
    "get_all_trades",
    "get_open_trades",
    "close_trade"
]
