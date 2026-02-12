"""Database operations for trading tables."""

from typing import List, Optional, Dict, Any
from datetime import datetime, date
import pandas as pd

from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError

from .connection import get_db_session
from .models import Fill, Order, Position, Universe


def _normalize_order_id(order_id: object) -> str:
    """Normalize order_id values to string for text-based DB columns."""
    return str(order_id) if order_id is not None else ""


# ===== FILL OPERATIONS =====

def create_fill(order_id: str, quantity: float, price: float, filled_at: Optional[datetime] = None) -> Optional[Fill]:
    """Create a new fill record."""
    try:
        with get_db_session() as session:
            fill = Fill(
                order_id=_normalize_order_id(order_id),
                quantity=quantity,
                price=price,
                filled_at=filled_at
            )
            session.add(fill)
            session.flush()
            session.refresh(fill)
            # Access attributes before session closes
            fill_id = fill.fill_id
            session.expunge(fill)
            return fill
    except SQLAlchemyError as e:
        print(f"Error creating fill: {e}")
        return None


def get_fill_by_id(fill_id: int) -> Optional[Fill]:
    """Get a fill by its ID."""
    try:
        with get_db_session() as session:
            fill = session.query(Fill).filter(Fill.fill_id == fill_id).first()
            if fill:
                session.expunge(fill)
            return fill
    except SQLAlchemyError as e:
        print(f"Error getting fill: {e}")
        return None


def get_fills_by_order(order_id: str) -> List[Fill]:
    """Get all fills for a specific order."""
    try:
        with get_db_session() as session:
            fills = session.query(Fill).filter(Fill.order_id == _normalize_order_id(order_id)).all()
            for fill in fills:
                session.expunge(fill)
            return fills
    except SQLAlchemyError as e:
        print(f"Error getting fills: {e}")
        return []


def get_all_fills(limit: Optional[int] = None) -> List[Fill]:
    """Get all fills, optionally limited."""
    try:
        with get_db_session() as session:
            query = session.query(Fill).order_by(Fill.filled_at.desc())
            if limit:
                query = query.limit(limit)
            fills = query.all()
            for fill in fills:
                session.expunge(fill)
            return fills
    except SQLAlchemyError as e:
        print(f"Error getting fills: {e}")
        return []


# ===== ORDER OPERATIONS =====

def create_order(
    order_id: str,
    symbol: str,
    quantity_ordered: float,
    status: Optional[str] = "pending",
    quantity_filled: float = 0
) -> Optional[Order]:
    """Create a new order record."""
    try:
        with get_db_session() as session:
            order = Order(
                order_id=_normalize_order_id(order_id),
                symbol=symbol,
                quantity_ordered=quantity_ordered,
                status=status,
                quantity_filled=quantity_filled
            )
            session.add(order)
            session.flush()
            session.refresh(order)
            # Access attributes before session closes
            _ = order.order_id
            session.expunge(order)
            return order
    except SQLAlchemyError as e:
        print(f"Error creating order: {e}")
        return None


def get_order_by_id(order_id: str) -> Optional[Order]:
    """Get an order by its ID."""
    try:
        with get_db_session() as session:
            order = session.query(Order).filter(Order.order_id == _normalize_order_id(order_id)).first()
            if order:
                session.expunge(order)
            return order
    except SQLAlchemyError as e:
        print(f"Error getting order: {e}")
        return None


def get_orders_by_symbol(symbol: str) -> List[Order]:
    """Get all orders for a specific symbol."""
    try:
        with get_db_session() as session:
            orders = session.query(Order).filter(Order.symbol == symbol).all()
            for order in orders:
                session.expunge(order)
            return orders
    except SQLAlchemyError as e:
        print(f"Error getting orders: {e}")
        return []


def get_orders_by_status(status: str) -> List[Order]:
    """Get all orders with a specific status."""
    try:
        with get_db_session() as session:
            orders = session.query(Order).filter(Order.status == status).all()
            for order in orders:
                session.expunge(order)
            return orders
    except SQLAlchemyError as e:
        print(f"Error getting orders: {e}")
        return []


def update_order_status(order_id: str, status: str, quantity_filled: Optional[float] = None) -> bool:
    """Update order status and optionally quantity filled."""
    try:
        with get_db_session() as session:
            update_data = {"status": status}
            if quantity_filled is not None:
                update_data["quantity_filled"] = quantity_filled

            session.query(Order).filter(Order.order_id == _normalize_order_id(order_id)).update(update_data)
            return True
    except SQLAlchemyError as e:
        print(f"Error updating order: {e}")
        return False


def get_all_orders(limit: Optional[int] = None) -> List[Order]:
    """Get all orders, optionally limited."""
    try:
        with get_db_session() as session:
            query = session.query(Order).order_by(Order.created_at.desc())
            if limit:
                query = query.limit(limit)
            orders = query.all()
            for order in orders:
                session.expunge(order)
            return orders
    except SQLAlchemyError as e:
        print(f"Error getting orders: {e}")
        return []


# ===== POSITION OPERATIONS =====

def create_position(
    symbol: str,
    status: str,
    side: str,
    open_time: datetime,
    open_price: float,
    quantity: float,
    strategy_tag: Optional[str] = None,
    commission_open: float = 0,
    close_time: Optional[datetime] = None,
    close_price: Optional[float] = None,
    commission_close: float = 0,
    tags: Optional[Dict[str, Any]] = None,
    notes: Optional[str] = None
) -> Optional[Position]:
    """Create a new position record."""
    try:
        with get_db_session() as session:
            position = Position(
                symbol=symbol,
                strategy_tag=strategy_tag,
                status=status,
                side=side,
                open_time=open_time,
                open_price=open_price,
                quantity=quantity,
                commission_open=commission_open,
                close_time=close_time,
                close_price=close_price,
                commission_close=commission_close,
                tags=tags,
                notes=notes
            )
            session.add(position)
            session.flush()
            session.refresh(position)
            _ = position.id
            session.expunge(position)
            return position
    except SQLAlchemyError as e:
        print(f"Error creating position: {e}")
        return None


def get_position_by_id(position_id: int) -> Optional[Position]:
    """Get a position by its ID."""
    try:
        with get_db_session() as session:
            position = session.query(Position).filter(Position.id == position_id).first()
            if position:
                session.expunge(position)
            return position
    except SQLAlchemyError as e:
        print(f"Error getting position: {e}")
        return None


def get_positions_by_symbol(symbol: str) -> List[Position]:
    """Get all positions for a specific symbol."""
    try:
        with get_db_session() as session:
            positions = session.query(Position).filter(Position.symbol == symbol).all()
            for position in positions:
                session.expunge(position)
            return positions
    except SQLAlchemyError as e:
        print(f"Error getting positions: {e}")
        return []


def get_positions_by_status(status: str) -> List[Position]:
    """Get all positions with a specific status."""
    try:
        with get_db_session() as session:
            positions = session.query(Position).filter(Position.status == status).all()
            for position in positions:
                session.expunge(position)
            return positions
    except SQLAlchemyError as e:
        print(f"Error getting positions: {e}")
        return []


def update_position(position_id: int, **updates: Any) -> bool:
    """Update a position record by ID."""
    allowed_fields = {
        "symbol",
        "strategy_tag",
        "status",
        "side",
        "open_time",
        "open_price",
        "quantity",
        "commission_open",
        "close_time",
        "close_price",
        "commission_close",
        "tags",
        "notes"
    }
    update_data = {key: value for key, value in updates.items() if key in allowed_fields}
    if not update_data:
        return False
    try:
        with get_db_session() as session:
            session.query(Position).filter(Position.id == position_id).update(update_data)
            return True
    except SQLAlchemyError as e:
        print(f"Error updating position: {e}")
        return False


def delete_position(position_id: int) -> bool:
    """Delete a position by ID."""
    try:
        with get_db_session() as session:
            deleted = session.query(Position).filter(Position.id == position_id).delete()
            return bool(deleted)
    except SQLAlchemyError as e:
        print(f"Error deleting position: {e}")
        return False


def get_open_positions() -> List[Position]:
    """Get all open positions."""
    return get_positions_by_status("OPEN")


# ===========================
# Universe Operations
# ===========================

def create_universe(week_start_date: date, symbol: str, is_active: bool = True, price_source_table: Optional[str] = None) -> Optional[Universe]:
    """Create a new universe entry."""
    try:
        with get_db_session() as session:
            universe = Universe(
                week_start_date=week_start_date,
                symbol=symbol,
                is_active=is_active,
                price_source_table=price_source_table
            )
            session.add(universe)
            session.flush()
            session.expunge(universe)
            return universe
    except SQLAlchemyError as e:
        print(f"Error creating universe: {e}")
        return None


def get_universe_by_snapshot_id(snapshot_id: int) -> Optional[Universe]:
    """Get a universe entry by snapshot ID."""
    try:
        with get_db_session() as session:
            universe = session.query(Universe).filter(Universe.snapshot_id == snapshot_id).first()
            if universe:
                session.expunge(universe)
            return universe
    except SQLAlchemyError as e:
        print(f"Error fetching universe by snapshot_id: {e}")
        return None


def get_universe_by_week(week_start_date: date) -> List[Universe]:
    """Get all universe entries for a specific week."""
    try:
        with get_db_session() as session:
            universes = session.query(Universe).filter(Universe.week_start_date == week_start_date).all()
            for universe in universes:
                session.expunge(universe)
            return universes
    except SQLAlchemyError as e:
        print(f"Error fetching universe by week: {e}")
        return []


def get_active_universe(week_start_date: date) -> List[Universe]:
    """Get all active universe entries for a specific week."""
    try:
        with get_db_session() as session:
            universes = session.query(Universe).filter(
                Universe.week_start_date == week_start_date,
                Universe.is_active == True
            ).all()
            for universe in universes:
                session.expunge(universe)
            return universes
    except SQLAlchemyError as e:
        print(f"Error fetching active universe: {e}")
        return []


def get_universe_by_symbol(symbol: str) -> List[Universe]:
    """Get all universe entries for a specific symbol."""
    try:
        with get_db_session() as session:
            universes = session.query(Universe).filter(Universe.symbol == symbol).order_by(Universe.week_start_date.desc()).all()
            for universe in universes:
                session.expunge(universe)
            return universes
    except SQLAlchemyError as e:
        print(f"Error fetching universe by symbol: {e}")
        return []


def update_universe_status(snapshot_id: int, is_active: bool) -> bool:
    """Update the is_active status of a universe entry."""
    try:
        with get_db_session() as session:
            session.query(Universe).filter(Universe.snapshot_id == snapshot_id).update({"is_active": is_active})
            return True
    except SQLAlchemyError as e:
        print(f"Error updating universe status: {e}")
        return False


def delete_universe(snapshot_id: int) -> bool:
    """Delete a universe entry by snapshot ID."""
    try:
        with get_db_session() as session:
            deleted = session.query(Universe).filter(Universe.snapshot_id == snapshot_id).delete()
            return bool(deleted)
    except SQLAlchemyError as e:
        print(f"Error deleting universe: {e}")
        return False


# ===========================
# Generic Table Operations
# ===========================

def get_latest_entries(table_name: str, symbol: str, n: int = 10) -> pd.DataFrame:
    """
    Retrieve the latest n entries from a table, filtered by symbol, sorted by time (ascending).
    
    Args:
        table_name: Full table name as string (e.g., "trading.fills", "trading.orders")
        symbol: Symbol to filter by
        n: Number of entries to retrieve (default 10)
    
    Returns:
        DataFrame containing rows sorted by time ascending (most recent last)
    """
    try:
        with get_db_session() as session:
            from sqlalchemy import text
            
            # Build raw SQL query to handle arbitrary table names
            # Assumes tables have 'symbol' and 'time' columns
            # First get n most recent, then sort ascending so latest is last row
            query_sql = f"""
                SELECT * FROM (
                    SELECT * FROM {table_name}
                    WHERE symbol = :symbol
                    ORDER BY time DESC
                    LIMIT :limit
                ) AS recent
                ORDER BY time ASC
            """
            
            result = session.execute(
                text(query_sql),
                {"symbol": symbol, "limit": n}
            )
            
            # Convert to DataFrame
            df = pd.DataFrame([dict(row._mapping) for row in result])
            return df
    except SQLAlchemyError as e:
        print(f"Error retrieving latest entries from {table_name}: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error executing query on {table_name}: {e}")
        return pd.DataFrame()


