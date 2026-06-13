import logging
from datetime import datetime, time as dtime, timezone, timedelta

import yfinance as yf
from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["history"])

VALID_INTERVALS = {"1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"}
VALID_RANGES = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"}

JST = timezone(timedelta(hours=9))
# 東証昼休み: 11:30〜12:30 JST
_LUNCH_START = dtime(11, 30)
_LUNCH_END   = dtime(12, 30)


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

    # 分足 intraday の場合、東証昼休み（11:30-12:30 JST）に null バーを挿入して
    # lightweight-charts がギャップを描画できるようにする
    if interval in {"1m", "5m", "15m", "30m"} and data:
        data = _insert_lunch_break(data, interval)

    return {"ticker": ticker, "interval": interval, "range": range, "data": data}


def _insert_lunch_break(data: list[dict], interval: str) -> list[dict]:
    """12:30 JST 以降の最初のバーの直前に、11:30〜12:29 JST の null バーを挿入する。"""
    step_ms = {"1m": 1, "5m": 5, "15m": 15, "30m": 30}.get(interval, 1) * 60 * 1000

    result: list[dict] = []
    inserted_dates: set = set()

    for bar in data:
        dt_jst = datetime.fromtimestamp(bar["t"] / 1000, tz=JST)
        date = dt_jst.date()

        # 12:30 以降の最初のバーが来たとき、直前に昼休み null を挿入
        if date not in inserted_dates and dt_jst.time() >= _LUNCH_END:
            inserted_dates.add(date)
            # 11:30 に実バーがある場合の重複を防ぐため、1ステップ後から開始
            null_start = int(datetime(date.year, date.month, date.day, 11, 30, tzinfo=JST).timestamp() * 1000) + step_ms
            null_end   = int(datetime(date.year, date.month, date.day, 12, 30, tzinfo=JST).timestamp() * 1000)
            t = null_start
            while t < null_end:
                result.append({"t": t, "o": None, "h": None, "l": None, "c": None, "v": None})
                t += step_ms

        result.append(bar)

    return result


def _safe_float(v) -> float | None:  # type: ignore[return]
    try:
        if v is None:
            return None
        f = float(v)
        return None if (f != f) else f  # NaN check
    except (TypeError, ValueError):
        return None
