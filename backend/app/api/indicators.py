import logging

import ta
import yfinance as yf
from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["indicators"])

VALID_TYPES = {"macd", "rsi", "sma", "ema"}


@router.get("/indicators")
def get_indicators(
    ticker: str = Query(...),
    type: str = Query(..., description="macd|rsi|sma|ema"),
    interval: str = Query(default="1d"),
    range: str = Query(default="6mo"),
    period: int = Query(default=14),
    fast: int = Query(default=12),
    slow: int = Query(default=26),
    signal: int = Query(default=9),
) -> dict:
    if type not in VALID_TYPES:
        raise HTTPException(400, f"type must be one of {VALID_TYPES}")

    try:
        hist = yf.Ticker(ticker).history(period=range, interval=interval)
    except Exception as e:
        logger.error("indicator fetch failed for %s: %s", ticker, e)
        raise HTTPException(500, "Failed to fetch price data")

    if hist.empty:
        return {"ticker": ticker, "type": type, "data": []}

    close = hist["Close"].dropna()
    timestamps = [int(ts.timestamp() * 1000) for ts in close.index]

    try:
        if type == "rsi":
            values = ta.momentum.RSIIndicator(close=close, window=period).rsi()
            return _series_response(ticker, type, timestamps, values.tolist())

        elif type == "macd":
            ind = ta.trend.MACD(close=close, window_slow=slow, window_fast=fast, window_sign=signal)
            macd_vals = ind.macd().tolist()
            sig_vals = ind.macd_signal().tolist()
            hist_vals = ind.macd_diff().tolist()
            data = [
                {
                    "t": t,
                    "macd": _sf(macd_vals[i]),
                    "signal": _sf(sig_vals[i]),
                    "histogram": _sf(hist_vals[i]),
                }
                for i, t in enumerate(timestamps)
            ]
            return {"ticker": ticker, "type": type, "data": data}

        elif type == "sma":
            values = ta.trend.SMAIndicator(close=close, window=period).sma_indicator()
            return _series_response(ticker, type, timestamps, values.tolist())

        elif type == "ema":
            values = ta.trend.EMAIndicator(close=close, window=period).ema_indicator()
            return _series_response(ticker, type, timestamps, values.tolist())

    except Exception as e:
        logger.error("indicator calc failed for %s %s: %s", ticker, type, e)
        raise HTTPException(500, "Indicator calculation failed")

    return {"ticker": ticker, "type": type, "data": []}


def _series_response(ticker: str, type: str, timestamps: list, values: list) -> dict:
    data = [{"t": t, "v": _sf(v)} for t, v in zip(timestamps, values)]
    return {"ticker": ticker, "type": type, "data": data}


def _sf(v) -> float | None:  # type: ignore[return]
    try:
        f = float(v)
        return None if (f != f) else f
    except (TypeError, ValueError):
        return None
