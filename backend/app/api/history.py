import logging

import yfinance as yf
from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["history"])

VALID_INTERVALS = {"1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"}
VALID_RANGES = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"}


@router.get("/history")
def get_history(
    ticker: str = Query(...),
    interval: str = Query(default="1d"),
    range: str = Query(default="6mo"),
) -> dict:
    if interval not in VALID_INTERVALS:
        raise HTTPException(400, f"interval must be one of {VALID_INTERVALS}")
    if range not in VALID_RANGES:
        raise HTTPException(400, f"range must be one of {VALID_RANGES}")

    try:
        hist = yf.Ticker(ticker).history(period=range, interval=interval)
    except Exception as e:
        logger.error("history fetch failed for %s: %s", ticker, e)
        raise HTTPException(500, "Failed to fetch history")

    if hist.empty:
        return {"ticker": ticker, "interval": interval, "range": range, "data": []}

    data = []
    for ts, row in hist.iterrows():
        data.append(
            {
                "t": int(ts.timestamp() * 1000),
                "o": _safe_float(row.get("Open")),
                "h": _safe_float(row.get("High")),
                "l": _safe_float(row.get("Low")),
                "c": _safe_float(row.get("Close")),
                "v": _safe_float(row.get("Volume")),
            }
        )

    return {"ticker": ticker, "interval": interval, "range": range, "data": data}


def _safe_float(v) -> float | None:  # type: ignore[return]
    try:
        if v is None:
            return None
        f = float(v)
        return None if (f != f) else f  # NaN check
    except (TypeError, ValueError):
        return None
