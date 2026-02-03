"""SQLAlchemy models for trading schema tables."""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Enum, text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum

from .connection import Base


# Enum types for order_status and trade_status
class OrderStatus(str, enum.Enum):
    """Order status enum."""
    pending = "pending"
    filled = "filled"
    cancelled = "cancelled"
    partial = "partial"


class TradeStatus(str, enum.Enum):
    """Trade status enum."""
    open = "open"
    closed = "closed"


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


class Trade(Base):
    """Model for trading.trades table."""
    __tablename__ = "trades"
    __table_args__ = {"schema": "trading"}

    trade_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    time = Column(DateTime(timezone=True), nullable=False)
    ticker = Column(String, nullable=False)
    side = Column(String, nullable=True)
    quantity = Column(Numeric, nullable=False)
    price = Column(Numeric, nullable=False)
    commission = Column(Numeric, nullable=True, server_default=text("0"))
    strategy_id = Column(String, nullable=True)
    status = Column(
        String,
        nullable=True,
        server_default=text("'open'::trading.trade_status")
    )

    def __repr__(self):
        return f"<Trade(trade_id={self.trade_id}, ticker='{self.ticker}', side='{self.side}', quantity={self.quantity})>"

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "trade_id": str(self.trade_id),
            "time": self.time.isoformat() if self.time else None,
            "ticker": self.ticker,
            "side": self.side,
            "quantity": float(self.quantity) if self.quantity else None,
            "price": float(self.price) if self.price else None,
            "commission": float(self.commission) if self.commission else None,
            "strategy_id": self.strategy_id,
            "status": self.status
        }
