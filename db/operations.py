"""Database operations for trading tables."""

from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError

from .connection import get_db_session
from .models import Fill, Order, Trade


# ===== FILL OPERATIONS =====

def create_fill(order_id: str, quantity: float, price: float, filled_at: Optional[datetime] = None) -> Optional[Fill]:
    """Create a new fill record."""
    try:
        with get_db_session() as session:
            fill = Fill(
                order_id=order_id,
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
            fills = session.query(Fill).filter(Fill.order_id == order_id).all()
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
                order_id=order_id,
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
            order = session.query(Order).filter(Order.order_id == order_id).first()
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

            session.query(Order).filter(Order.order_id == order_id).update(update_data)
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


# ===== TRADE OPERATIONS =====

def create_trade(
    time: datetime,
    ticker: str,
    quantity: float,
    price: float,
    side: Optional[str] = None,
    commission: float = 0,
    strategy_id: Optional[str] = None,
    status: str = "open"
) -> Optional[Trade]:
    """Create a new trade record."""
    try:
        with get_db_session() as session:
            trade = Trade(
                time=time,
                ticker=ticker,
                side=side,
                quantity=quantity,
                price=price,
                commission=commission,
                strategy_id=strategy_id,
                status=status
            )
            session.add(trade)
            session.flush()
            session.refresh(trade)
            # Access attributes before session closes
            _ = trade.trade_id
            session.expunge(trade)
            return trade
    except SQLAlchemyError as e:
        print(f"Error creating trade: {e}")
        return None


def get_trade_by_id(trade_id: UUID) -> Optional[Trade]:
    """Get a trade by its ID."""
    try:
        with get_db_session() as session:
            trade = session.query(Trade).filter(Trade.trade_id == trade_id).first()
            if trade:
                session.expunge(trade)
            return trade
    except SQLAlchemyError as e:
        print(f"Error getting trade: {e}")
        return None


def get_trades_by_ticker(ticker: str) -> List[Trade]:
    """Get all trades for a specific ticker."""
    try:
        with get_db_session() as session:
            trades = session.query(Trade).filter(Trade.ticker == ticker).all()
            for trade in trades:
                session.expunge(trade)
            return trades
    except SQLAlchemyError as e:
        print(f"Error getting trades: {e}")
        return []


def get_trades_by_strategy(strategy_id: str) -> List[Trade]:
    """Get all trades for a specific strategy."""
    try:
        with get_db_session() as session:
            trades = session.query(Trade).filter(Trade.strategy_id == strategy_id).all()
            for trade in trades:
                session.expunge(trade)
            return trades
    except SQLAlchemyError as e:
        print(f"Error getting trades: {e}")
        return []


def get_trades_by_status(status: str) -> List[Trade]:
    """Get all trades with a specific status."""
    try:
        with get_db_session() as session:
            trades = session.query(Trade).filter(Trade.status == status).all()
            for trade in trades:
                session.expunge(trade)
            return trades
    except SQLAlchemyError as e:
        print(f"Error getting trades: {e}")
        return []


def update_trade_status(trade_id: UUID, status: str) -> bool:
    """Update trade status."""
    try:
        with get_db_session() as session:
            session.query(Trade).filter(Trade.trade_id == trade_id).update({"status": status})
            return True
    except SQLAlchemyError as e:
        print(f"Error updating trade: {e}")
        return False


def get_all_trades(limit: Optional[int] = None) -> List[Trade]:
    """Get all trades, optionally limited."""
    try:
        with get_db_session() as session:
            query = session.query(Trade).order_by(Trade.time.desc())
            if limit:
                query = query.limit(limit)
            trades = query.all()
            for trade in trades:
                session.expunge(trade)
            return trades
    except SQLAlchemyError as e:
        print(f"Error getting trades: {e}")
        return []


def get_open_trades() -> List[Trade]:
    """Get all open trades."""
    return get_trades_by_status("open")


def close_trade(trade_id: UUID) -> bool:
    """Close a trade by setting status to closed."""
    return update_trade_status(trade_id, "closed")
