from dotenv import load_dotenv
import os

from alpaca.trading.client import TradingClient
from alpaca.trading.stream import TradingStream

from Strategy import Strategy
from Portfolio import Portfolio
from ExecutionHandler import ExecutionHandler
from Context import Context, EventSink
from Events import *
from Types import *

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

    def publish(self, event: Event):
        self.event_queue.append(event)

    def set_strategy(self, strategy: Strategy):
        self.strategy = strategy
        self.strategy.set_context(Context(event_sink=self))

    def set_portfolio(self, portfolio: Portfolio):
        self.portfolio = portfolio
        self.portfolio.set_context(Context(event_sink=self))

    async def handle_trading_stream_updates(self, data):
        # !TODO: Parse data, convert to Event, and push to event queue
        pass

    def handle_update(self, event: Event):
        # Push event to event queue
        self.event_queue.append(event)

        # Run until event queue is empty
        while self.event_queue:
            current_event = self.event_queue.pop(0)

            if event.type == EventType.MARKET:
                self.strategy.on_update(current_event)
            elif event.type == EventType.SIGNAL:
                self.portfolio.on_signal(current_event)
            elif event.type == EventType.ORDER:
                self.execution_handler.execute_order(current_event)
            elif event.type == EventType.FILL:
                self.portfolio.on_fill(current_event)

    def run(self):
        self.trading_stream.run()