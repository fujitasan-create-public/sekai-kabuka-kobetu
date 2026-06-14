import logging

import yfinance as yf

from app.application.interfaces.stock_service import IStockDataService
from app.domain.entities.stock import OHLCVBar, StockQuote

logger = logging.getLogger(__name__)

_QUOTE_FIELDS = [
    "longName",
    "shortName",
    "currency",
    "exchange",
    "trailingPE",
    "forwardPE",
    "priceToBook",
    "marketCap",
    "dividendYield",
    "trailingEps",
    "fiftyTwoWeekHigh",
    "fiftyTwoWeekLow",
    "volume",
    "averageVolume",
    "beta",
    "sector",
    "industry",
]


class YFinanceStockService(IStockDataService):
    async def get_quote(self, ticker: str) -> StockQuote:
        try:
            info = yf.Ticker(ticker).get_info()
        except Exception as e:
            logger.error("quote fetch failed for %s: %s", ticker, e)
            info = {}

        return StockQuote(
            ticker=ticker,
            long_name=_safe(info.get("longName")),
            short_name=_safe(info.get("shortName")),
            currency=_safe(info.get("currency")),
            exchange=_safe(info.get("exchange")),
            trailing_pe=_safe(info.get("trailingPE")),
            forward_pe=_safe(info.get("forwardPE")),
            price_to_book=_safe(info.get("priceToBook")),
            market_cap=_safe(info.get("marketCap")),
            dividend_yield=_safe_yield(info.get("dividendYield")),
            trailing_eps=_safe(info.get("trailingEps")),
            fifty_two_week_high=_safe(info.get("fiftyTwoWeekHigh")),
            fifty_two_week_low=_safe(info.get("fiftyTwoWeekLow")),
            volume=_safe(info.get("volume")),
            average_volume=_safe(info.get("averageVolume")),
            beta=_safe(info.get("beta")),
            sector=_safe(info.get("sector")),
            industry=_safe(info.get("industry")),
        )

    async def get_ohlcv(self, ticker: str, period: str, interval: str) -> list[OHLCVBar]:
        try:
            hist = yf.Ticker(ticker).history(period=period, interval=interval)
        except Exception as e:
            logger.error("history fetch failed for %s: %s", ticker, e)
            return []

        if hist.empty:
            return []

        bars: list[OHLCVBar] = []
        for ts, row in hist.iterrows():
            bars.append(
                OHLCVBar(
                    t=int(ts.timestamp() * 1000),
                    o=_safe_float(row.get("Open")),
                    h=_safe_float(row.get("High")),
                    l=_safe_float(row.get("Low")),
                    c=_safe_float(row.get("Close")),
                    v=_safe_float(row.get("Volume")),
                )
            )
        return bars


def _safe(v):  # type: ignore[return]
    if v is None:
        return None
    if isinstance(v, float) and v != v:
        return None
    return v


def _safe_yield(v):  # type: ignore[return]
    if v is None or (isinstance(v, float) and v != v) or v == 0:
        return None
    return v / 100


def _safe_float(v) -> float | None:  # type: ignore[return]
    try:
        if v is None:
            return None
        f = float(v)
        return None if (f != f) else f
    except (TypeError, ValueError):
        return None
