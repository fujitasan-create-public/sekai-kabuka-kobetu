from dataclasses import dataclass


@dataclass(frozen=True)
class TickerInfo:
    name: str
    ticker: str
    market: str
