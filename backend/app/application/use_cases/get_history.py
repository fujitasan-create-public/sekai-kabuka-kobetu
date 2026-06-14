from __future__ import annotations

from datetime import date, datetime, time as dtime, timedelta, timezone

from app.application.interfaces.stock_service import IStockDataService
from app.domain.entities.stock import OHLCVBar

JST = timezone(timedelta(hours=9))
_LUNCH_START = dtime(11, 30)
_LUNCH_END = dtime(12, 30)

VALID_INTERVALS = {"1m", "5m", "15m", "30m", "1h", "1d", "1wk", "1mo"}
VALID_RANGES = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "max"}


class GetHistoryUseCase:
    def __init__(self, stock_service: IStockDataService) -> None:
        self._service = stock_service

    async def execute(
        self, ticker: str, period: str, interval: str
    ) -> list[OHLCVBar]:
        bars = await self._service.get_ohlcv(ticker, period, interval)
        if interval in {"1m", "5m", "15m", "30m"} and bars:
            bars = _insert_lunch_break(bars, interval)
        return bars


def _insert_lunch_break(bars: list[OHLCVBar], interval: str) -> list[OHLCVBar]:
    """12:30 JST 以降の最初のバー直前に昼休みの null バーを挿入する。"""
    step_ms = {"1m": 1, "5m": 5, "15m": 15, "30m": 30}.get(interval, 1) * 60 * 1000

    result: list[OHLCVBar] = []
    inserted_dates: set[date] = set()

    for bar in bars:
        dt_jst = datetime.fromtimestamp(bar.t / 1000, tz=JST)
        d = dt_jst.date()

        if d not in inserted_dates and dt_jst.time() >= _LUNCH_END:
            inserted_dates.add(d)
            null_start = (
                int(datetime(d.year, d.month, d.day, 11, 30, tzinfo=JST).timestamp() * 1000)
                + step_ms
            )
            null_end = int(
                datetime(d.year, d.month, d.day, 12, 30, tzinfo=JST).timestamp() * 1000
            )
            t = null_start
            while t < null_end:
                result.append(OHLCVBar(t=t, o=None, h=None, l=None, c=None, v=None))
                t += step_ms

        result.append(bar)

    return result
