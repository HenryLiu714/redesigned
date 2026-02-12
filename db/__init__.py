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
    Position,
    Universe,
    OrderStatus
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

    # Position operations
    create_position,
    get_position_by_id,
    get_positions_by_symbol,
    get_positions_by_status,
    update_position,
    delete_position,
    get_open_positions,

    # Universe operations
    create_universe,
    get_universe_by_snapshot_id,
    get_universe_by_week,
    get_active_universe,
    get_universe_by_symbol,
    update_universe_status,
    delete_universe,

    # Generic table operations
    get_latest_entries
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
    "Position",
    "Universe",
    "OrderStatus",


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

    # Position operations
    "create_position",
    "get_position_by_id",
    "get_positions_by_symbol",
    "get_positions_by_status",
    "update_position",
    "delete_position",
    "get_open_positions",

    # Universe operations
    "create_universe",
    "get_universe_by_snapshot_id",
    "get_universe_by_week",
    "get_active_universe",
    "get_universe_by_symbol",
    "update_universe_status",
    "delete_universe",

    # Generic table operations
    "get_latest_entries"
]
