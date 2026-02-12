from dotenv import load_dotenv
import os

from src.Alert import send_alert

from alpaca.trading.client import TradingClient
from alpaca.trading.stream import TradingStream

from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone

from src.Strategy import Strategy
from src.Portfolio import Portfolio
from src.ExecutionHandler import ExecutionHandler
from src.Context import Context, EventSink
from db import create_fill, create_order
from src.Events import *
from src.Types import *

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET = os.getenv("ALPACA_SECRET")

class Engine(EventSink):
    def __init__(self):
        self.strategy: Strategy = None
        self.portfolio: Portfolio = None

        self.event_queue: list[Event] = []

        self.trading_client: TradingClient = TradingClient(ALPACA_API_KEY, ALPACA_SECRET, paper=True)
        self.trading_stream: TradingStream = TradingStream(ALPACA_API_KEY, ALPACA_SECRET, paper=True)

        self.trading_stream.subscribe_trade_updates(self.handle_trading_stream_updates)

        self.execution_handler: ExecutionHandler = ExecutionHandler(self.trading_client)

        self.scheduler = BackgroundScheduler()
        self.market_tz = timezone("America/New_York")

    def schedule_tasks(self):
        self.scheduler.add_job(
            self.generate_market_open_event,
            trigger="cron",
            day_of_week="mon-fri",
            hour=9,
            minute=30,
            timezone=self.market_tz,
            id="market_open_event"
        )

        self.scheduler.start()

    def generate_market_open_event(self):
        event = MarketEvent()

        self.handle_update(event)

    def publish(self, event: Event):
        self.event_queue.append(event)

    def set_strategy(self, strategy: Strategy):
        self.strategy = strategy
        self.strategy.set_context(Context(event_sink=self, trading_client=self.trading_client))

    def set_portfolio(self, portfolio: Portfolio):
        self.portfolio = portfolio
        self.portfolio.set_context(Context(event_sink=self, trading_client=self.trading_client))
    async def handle_trading_stream_updates(self, data):
        try:
            if data.event == "new":
                create_order(order_id=data.order.id, symbol=data.order.symbol, quantity_ordered=float(data.order.qty), status="pending")

                send_alert(f"New order event received from trading stream. \n {data.order.symbol} {data.order.qty} @ {data.order.limit_price if data.order.limit_price else 'MKT'}")

            elif data.event == "fill" or data.event == "partial_fill":
                raw_side = data.order.side.upper()
                side_map = {
                    "BUY": "LONG",
                    "SELL": "SHORT",
                    "LONG": "LONG",
                    "SHORT": "SHORT"
                }
                normalized_side = side_map.get(raw_side, raw_side)

                event = FillEvent(
                    timestamp=data.timestamp.timestamp() if hasattr(data.timestamp, "timestamp") else float(data.timestamp),
                    fill=Fill(
                        symbol=data.order.symbol,
                        quantity=float(data.qty),
                        side=normalized_side,
                        fill_price=float(data.price),
                        commission=0.0 # Alpaca does not provide commission data
                    )
                )

                # TODO: Move to portfolio
                create_fill(order_id=data.order.id, quantity=float(data.qty), price=float(data.price), filled_at=data.timestamp)

                self.handle_update(event)

        except Exception as e:
            print(f"Error processing trading stream update: {str(e)}")
            send_alert(f"Error processing trading stream update: {str(e)}")

    def handle_update(self, event: Event):
        # Push event to event queue
        self.event_queue.append(event)

        # Run until event queue is empty
        while self.event_queue:
            current_event = self.event_queue.pop(0)

            if current_event.event_type == EventType.MARKET:
                self.strategy.on_update(current_event)
                self.portfolio.on_market_update(current_event)
            elif current_event.event_type == EventType.SIGNAL:
                send_alert(f"{current_event.signal.strategy_id}: {current_event.signal.symbol} @ {current_event.signal.value}")
                self.portfolio.on_signal(current_event.signal)
            elif current_event.event_type == EventType.ORDER:
                send_alert(f"New order submitted. \n {current_event.order.symbol} {current_event.order.quantity} @ {current_event.order.price if current_event.order.price else 'MKT'}")
                self.execution_handler.execute_order(current_event.order)
            elif current_event.event_type == EventType.FILL:
                send_alert(f"New fill received. \n {current_event.fill.symbol} {current_event.fill.quantity} @ {current_event.fill.fill_price}")
                self.portfolio.on_fill(current_event.fill)

    def run(self):
        self.generate_market_open_event()

        self.schedule_tasks()
        self.trading_stream.run()