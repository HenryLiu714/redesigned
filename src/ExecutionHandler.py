
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from db import (
    create_order
)

from src.Alert import send_alert
from src.Types import *

POSITION_INTENT_MAP = {
    (Direction.LONG, OrderIntent.OPEN): "buy_to_open",
    (Direction.LONG, OrderIntent.CLOSE): "buy_to_close",
    (Direction.SHORT, OrderIntent.OPEN): "sell_to_open",
    (Direction.SHORT, OrderIntent.CLOSE): "sell_to_close"
}

class ExecutionHandler(object):
    def __init__(self, trading_client: TradingClient):
        self.trading_client = trading_client

    def execute_order(self, order: Order):
        # Execute order, and store active order in database (by alpaca ID)
        order_response = None

        try:
            if order.order_type == OrderType.MARKET:
                market_order_data = MarketOrderRequest(
                    symbol=order.symbol,
                    qty=order.quantity,
                    side=OrderSide.BUY if order.side == Direction.LONG else OrderSide.SELL,
                    time_in_force=TimeInForce.GTC,
                    position_intent = POSITION_INTENT_MAP.get((order.side, order.order_intent))
                )

                order_response = self.trading_client.submit_order(
                    order_data=market_order_data
                )

            elif order.order_type == OrderType.LIMIT:
                limit_order_data = LimitOrderRequest(
                    symbol=order.symbol,
                    qty=order.quantity,
                    side=OrderSide.BUY if order.direction == Direction.LONG else OrderSide.SELL,
                    time_in_force=TimeInForce.DAY, # Limit orders only valid for the day
                    limit_price=order.price,
                    position_intent = POSITION_INTENT_MAP.get((order.direction, order.order_intent))
                )

                order_response = self.trading_client.submit_order(
                    order_data=limit_order_data
                )

        except Exception as e:
            send_alert(f"Order execution failed for {order.symbol}: {str(e)}")