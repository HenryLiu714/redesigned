from src.Context import Context
from src.Types import *
from src.Events import OrderEvent, MarketEvent

from src.Alert import send_alert

from db.operations import create_position, update_position, get_open_positions

from db import models

class Portfolio(object):
    def __init__(self):
        self.context: Context = None
        self.open_positions: dict[str, Position] = {}
        self.max_positions = 5

        # Retrieve open positions from database and populate self.open_positions
        open_positions_from_db = get_open_positions()
        for position in open_positions_from_db:
            self.open_positions[position.symbol] = Position(symbol=position.symbol, position_id=str(position.id), quantity=position.quantity, entry_price=position.open_price)

    def on_market_update(self, event: MarketEvent):
        pass

    def on_signal(self, signal: Signal):
        if len(self.open_positions) >= self.max_positions:
            send_alert(f"Received signal for {signal.symbol} but max positions already open. Ignoring signal.")
            return

        if signal.strategy_id == "SniperStrategy":
            cash = self.context.get_cash()
            quantity = int(cash / signal.value)

            order = Order(symbol=signal.symbol, quantity=quantity, order_type=OrderType.LIMIT, direction=Direction.LONG, order_intent=OrderIntent.OPEN, price=round(signal.value, 2))
            self.send_order(order)

    def on_fill(self, fill: Fill):
        # Add the fill to the open positions if it is an opening fill, otherwise remove it from the open positions
        if fill.symbol not in self.open_positions:
            # Create database entry
            new_position: models.Position = create_position(
                symbol=fill.symbol,
                status='OPEN',
                side=fill.side,
                open_time=self.context.current_time(),
                open_price=fill.fill_price,
                quantity=fill.quantity
            )

            self.open_positions[fill.symbol] = Position(symbol=fill.symbol,
                                                        position_id=str(new_position.id),
                                                        quantity=fill.quantity,
                                                        entry_price=fill.fill_price,
                                                        entry_time=self.context.current_time())

        else:
            # Update database entry
            update_position(
                position_id=int(self.open_positions[fill.symbol].position_id),
                status='CLOSED',
                close_time=self.context.current_time(),
                close_price=fill.fill_price,
                commission_close=fill.commission
            )

            self.open_positions.pop(fill.symbol)

    def send_order(self, order: Order):
        order_event = OrderEvent(order=order)
        self.context.event_sink.publish(order_event)

    def set_context(self, context: Context):
        self.context = context