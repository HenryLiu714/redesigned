from pydantic import BaseModel
from src.Types import *

from datetime import datetime

class Event(BaseModel):
    event_type: str
    timestamp: float = datetime.now().timestamp()

class MarketEvent(Event):
    event_type: str = "MARKET"

class SignalEvent(Event):
    event_type: str = "SIGNAL"
    signal: Signal

class OrderEvent(Event):
    event_type: str = "ORDER"
    order: Order

class FillEvent(Event):
    event_type: str = "FILL"
    fill: Fill