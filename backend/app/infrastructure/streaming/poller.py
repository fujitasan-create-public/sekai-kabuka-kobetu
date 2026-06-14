import asyncio
import logging
import time

import yfinance as yf

from app.application.interfaces.broadcaster import IBroadcaster
from app.application.interfaces.cache_service import ICacheService
from app.domain.entities.stock import StockSnapshot

logger = logging.getLogger(__name__)

_POLL_INTERVAL = 30


class Poller:
    def __init__(
        self,
        broadcaster: IBroadcaster,
        cache: ICacheService,
        poll_interval: int = _POLL_INTERVAL,
    ) -> None:
        self._broadcaster = broadcaster
        self._cache = cache
        self._poll_interval = poll_interval
        self._backoff = poll_interval

    async def run(self) -> None:
        while True:
            await asyncio.sleep(self._backoff)
            await self._poll_once()

    async def _poll_once(self) -> None:
        watched = self._broadcaster.get_watched()
        if not watched:
            return

        tickers_list = sorted(watched)
        try:
            batch = yf.Tickers(" ".join(tickers_list))
            updates: dict = {}
            for sym in tickers_list:
                try:
                    hist = batch.tickers[sym].history(period="1d", interval="1m")
                    if hist.empty:
                        cached = self._cache.get_snapshot(sym)
                        if cached:
                            updates[sym] = _snapshot_to_dict(cached)
                        continue

                    closes = hist["Close"].dropna()
                    opens = hist["Open"].dropna()
                    if closes.empty:
                        continue

                    current = float(closes.iloc[-1])
                    open_price = float(opens.iloc[0]) if not opens.empty else current
                    change = current - open_price
                    change_pct = (change / open_price * 100) if open_price != 0 else 0.0

                    intraday = [
                        {"t": int(ts.timestamp() * 1000), "c": float(row)}
                        for ts, row in closes.items()
                    ]

                    snap = StockSnapshot(
                        ticker=sym,
                        price=current,
                        change=round(change, 4),
                        change_pct=round(change_pct, 4),
                        intraday=intraday,
                        last_updated=time.time(),
                    )
                    self._cache.set_snapshot(sym, snap)
                    updates[sym] = _snapshot_to_dict(snap)

                except Exception as e:
                    logger.warning("Failed to fetch %s: %s", sym, e)
                    cached = self._cache.get_snapshot(sym)
                    if cached:
                        updates[sym] = _snapshot_to_dict(cached)

            if updates:
                await self._broadcaster.broadcast(updates)

            self._backoff = self._poll_interval

        except Exception as e:
            logger.error("Poll batch failed: %s", e)
            self._backoff = min(self._backoff * 2, 300)


def _snapshot_to_dict(snap: StockSnapshot) -> dict:
    return {
        "ticker": snap.ticker,
        "price": snap.price,
        "change": snap.change,
        "change_pct": snap.change_pct,
        "intraday": snap.intraday,
        "last_updated": snap.last_updated,
    }
