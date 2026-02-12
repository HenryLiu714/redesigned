from src.Types import *
from src.Events import MarketEvent, SignalEvent
from src.Context import *

import pandas as pd
import pandas_ta_classic as ta

from db.operations import get_active_universe, get_latest_entries

class Strategy(object):
    def __init__(self, name):
        self.name = name
        self.context: Context = None

    def on_update(self, event: MarketEvent):
        pass

    def send_signal(self, signal: Signal):
        signal_event = SignalEvent(signal=signal)
        self.context.event_sink.publish(signal_event)

    def set_context(self, context: Context):
        self.context = context

class SniperStrategy(Strategy):
    def __init__(self):
        super().__init__(name="SniperStrategy")

    def check_entry_criteria(self, latest_data: pd.DataFrame) -> bool:
        # Returns target entry price
        rsi = ta.rsi(latest_data["close"], length=2)

        return rsi.iloc[-1] <= 10

    def calculate_entry_price(self, latest_data: pd.DataFrame) -> float:
        atr = ta.atr(latest_data["high"], latest_data["low"], latest_data["close"], length=14)
        return latest_data["close"].iloc[-1] - atr.iloc[-1]

    def on_update(self, event: MarketEvent):
        # Retrieve current stock universe
        current_week = self.context.get_start_of_week()
        universe = get_active_universe(current_week)

        # For each stock, check if it meets entry criteria, if it does send a signal to enter position
        for stock in universe:
            table_name = stock.price_source_table
            symbol = stock.symbol

            # Gather latest 250 entries
            latest_data = get_latest_entries(table_name=table_name, symbol=symbol, n=30)

            if latest_data is None or len(latest_data) < 30:
                continue

            # Check if entry criteria is met, if it is send signal to enter position
            #!TODO: Flip this conditional
            if not self.check_entry_criteria(latest_data):
                entry_price = self.calculate_entry_price(latest_data)

                signal = Signal(strategy_id=self.name, symbol=symbol, value=entry_price)
                self.send_signal(signal)