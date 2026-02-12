"""SQLAlchemy models for trading schema tables."""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Date, Boolean, Enum, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
import enum

from .connection import Base


# Enum types for order_status
class OrderStatus(str, enum.Enum):
    """Order status enum."""
    pending = "pending"
    filled = "filled"
    cancelled = "cancelled"
    partial = "partial"


class Fill(Base):
    """Model for trading.fills table."""
    __tablename__ = "fills"
    __table_args__ = {"schema": "trading"}

    fill_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(String, nullable=False)
    quantity = Column(Numeric, nullable=False)
    price = Column(Numeric, nullable=False)
    filled_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

    def __repr__(self):
        return f"<Fill(fill_id={self.fill_id}, order_id='{self.order_id}', quantity={self.quantity}, price={self.price})>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "fill_id": self.fill_id,
            "order_id": self.order_id,
            "quantity": float(self.quantity) if self.quantity else None,
            "price": float(self.price) if self.price else None,
            "filled_at": self.filled_at.isoformat() if self.filled_at else None
        }


class Order(Base):
    """Model for trading.orders table."""
    __tablename__ = "orders"
    __table_args__ = {"schema": "trading"}

    order_id = Column(String, primary_key=True)
    status = Column(
        String,
        nullable=True,
        server_default=text("'pending'::trading.order_status")
    )
    quantity_ordered = Column(Numeric, nullable=False)
    quantity_filled = Column(Numeric, nullable=True, server_default=text("0"))
    symbol = Column(String, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("CURRENT_TIMESTAMP")
    )

    def __repr__(self):
        return f"<Order(order_id='{self.order_id}', symbol='{self.symbol}', status='{self.status}')>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "order_id": self.order_id,
            "status": self.status,
            "quantity_ordered": float(self.quantity_ordered) if self.quantity_ordered else None,
            "quantity_filled": float(self.quantity_filled) if self.quantity_filled else None,
            "symbol": self.symbol,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Position(Base):
    """Model for trading.positions table."""
    __tablename__ = "positions"
    __table_args__ = {"schema": "trading"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(12), nullable=False)
    strategy_tag = Column(String(50), nullable=True)

    status = Column(String(10), nullable=False)
    side = Column(String(10), nullable=False)

    open_time = Column(DateTime(timezone=True), nullable=False)
    open_price = Column(Numeric(18, 4), nullable=False)
    quantity = Column(Numeric(18, 8), nullable=False)
    commission_open = Column(Numeric(10, 4), nullable=True, server_default=text("0"))

    close_time = Column(DateTime(timezone=True), nullable=True)
    close_price = Column(Numeric(18, 4), nullable=True)
    commission_close = Column(Numeric(10, 4), nullable=True, server_default=text("0"))

    tags = Column(JSONB, nullable=True)
    notes = Column(Text, nullable=True)

    def __repr__(self):
        return (
            f"<Position(id={self.id}, symbol='{self.symbol}', status='{self.status}', "
            f"side='{self.side}', quantity={self.quantity})>"
        )

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "strategy_tag": self.strategy_tag,
            "status": self.status,
            "side": self.side,
            "open_time": self.open_time.isoformat() if self.open_time else None,
            "open_price": float(self.open_price) if self.open_price else None,
            "quantity": float(self.quantity) if self.quantity else None,
            "commission_open": float(self.commission_open) if self.commission_open else None,
            "close_time": self.close_time.isoformat() if self.close_time else None,
            "close_price": float(self.close_price) if self.close_price else None,
            "commission_close": float(self.commission_close) if self.commission_close else None,
            "tags": self.tags,
            "notes": self.notes
        }


class Universe(Base):
    """Model for trading.universe table."""
    __tablename__ = "universe"
    __table_args__ = {"schema": "trading"}

    snapshot_id = Column(Integer, primary_key=True, autoincrement=True)
    week_start_date = Column(Date, nullable=False)
    symbol = Column(String(12), nullable=False)
    is_active = Column(Boolean, nullable=True, server_default=text("TRUE"))
    price_source_table = Column(String, nullable=True)

    def __repr__(self):
        return (
            f"<Universe(snapshot_id={self.snapshot_id}, week_start_date={self.week_start_date}, "
            f"symbol='{self.symbol}', is_active={self.is_active}, price_source_table='{self.price_source_table}')>"
        )

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "snapshot_id": self.snapshot_id,
            "week_start_date": self.week_start_date.isoformat() if self.week_start_date else None,
            "symbol": self.symbol,
            "is_active": self.is_active,
            "price_source_table": self.price_source_table
        }
