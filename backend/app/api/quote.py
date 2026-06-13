import logging

import yfinance as yf
from fastapi import APIRouter, Query

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["quote"])

_FIELDS = [
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


@router.get("/quote")
def get_quote(ticker: str = Query(...)) -> dict:
    try:
        info = yf.Ticker(ticker).get_info()
    except Exception as e:
        logger.error("quote fetch failed for %s: %s", ticker, e)
        info = {}

    result: dict = {"ticker": ticker}
    for field in _FIELDS:
        val = info.get(field)
        result[field] = _safe(val)
    return result


def _safe(v):  # type: ignore[return]
    if v is None:
        return None
    if isinstance(v, float) and v != v:  # NaN
        return None
    return v
