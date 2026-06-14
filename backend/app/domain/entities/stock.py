from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class OHLCVBar:
    t: int
    o: float | None
    h: float | None
    l: float | None
    c: float | None
    v: float | None


@dataclass(frozen=True)
class StockQuote:
    ticker: str
    long_name: str | None
    short_name: str | None
    currency: str | None
    exchange: str | None
    trailing_pe: float | None
    forward_pe: float | None
    price_to_book: float | None
    market_cap: float | None
    dividend_yield: float | None
    trailing_eps: float | None
    fifty_two_week_high: float | None
    fifty_two_week_low: float | None
    volume: float | None
    average_volume: float | None
    beta: float | None
    sector: str | None
    industry: str | None


@dataclass
class StockSnapshot:
    ticker: str
    price: float
    change: float
    change_pct: float
    intraday: list[dict[str, Any]]
    last_updated: float


@dataclass
class IndicatorResult:
    ticker: str
    type: str
    data: list[dict[str, Any]] = field(default_factory=list)
