"""Periodic poller: fetches yfinance data for watched tickers, updates cache, broadcasts."""
import asyncio
import logging
import time

import yfinance as yf

from app.data import broadcaster, cache

logger = logging.getLogger(__name__)

POLL_INTERVAL = 30  # seconds
_backoff = POLL_INTERVAL


async def poll_once() -> None:
    global _backoff
    watched = broadcaster.get_watched()
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
                    cached = cache.get_snapshot(sym)
                    if cached:
                        updates[sym] = cached
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

                snap = {
                    "ticker": sym,
                    "price": current,
                    "change": round(change, 4),
                    "change_pct": round(change_pct, 4),
                    "intraday": intraday,
                    "last_updated": time.time(),
                }
                cache.set_snapshot(sym, snap)
                updates[sym] = snap

            except Exception as e:
                logger.warning("Failed to fetch %s: %s", sym, e)
                cached = cache.get_snapshot(sym)
                if cached:
                    updates[sym] = cached

        if updates:
            await broadcaster.broadcast(updates)

        _backoff = POLL_INTERVAL  # reset on success

    except Exception as e:
        logger.error("Poll batch failed: %s", e)
        # Exponential backoff, max 5 min
        _backoff = min(_backoff * 2, 300)


async def run_poller() -> None:
    while True:
        await asyncio.sleep(_backoff)
        await poll_once()
