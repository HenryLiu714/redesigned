from datetime import datetime, timezone, timedelta, date

from alpaca.trading.client import TradingClient

from src.Events import *



class EventSink(object):
    def publish(self, event: Event):
        pass

class Context(object):
    def __init__(self, event_sink: EventSink, trading_client: TradingClient):
        self.event_sink = event_sink
        self.trading_client = trading_client

    def current_time(self) -> datetime:
        """
        Returns the current UTC time.
        Using timezone-aware objects prevents many common bugs.
        """
        return datetime.now(timezone.utc)

    def get_start_of_week(self) -> datetime:
        """
        Returns the start of the current week (Monday at 00:00:00) in UTC.
        """
        start_of_week = date.today() - timedelta(days=date.today().weekday())
        return start_of_week

    def get_cash(self)->float:
        account = self.trading_client.get_account()
        return float(account.cash)