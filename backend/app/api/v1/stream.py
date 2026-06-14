"""SSE endpoint for near-realtime ticker updates."""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse

from app.api.dependencies import get_broadcaster, get_cache_service
from app.application.interfaces.broadcaster import IBroadcaster
from app.application.interfaces.cache_service import ICacheService

logger = logging.getLogger(__name__)
router = APIRouter(tags=["stream"])


@router.get("/stream")
async def stream(
    request: Request,
    tickers: str = Query(..., description="カンマ区切り銘柄コード例: 7203.T,6758.T"),
    broadcaster: IBroadcaster = Depends(get_broadcaster),
    cache: ICacheService = Depends(get_cache_service),
) -> StreamingResponse:
    ticker_list = [t.strip() for t in tickers.split(",") if t.strip()]
    await broadcaster.register_tickers(ticker_list)

    q: asyncio.Queue[dict[str, Any]] = asyncio.Queue()
    broadcaster.add_client(q)

    async def generator():
        try:
            initial = {}
            for t in ticker_list:
                snap = cache.get_snapshot(t)
                if snap is not None:
                    initial[t] = {
                        "ticker": snap.ticker,
                        "price": snap.price,
                        "change": snap.change,
                        "change_pct": snap.change_pct,
                        "intraday": snap.intraday,
                        "last_updated": snap.last_updated,
                    }
                else:
                    initial[t] = None
            yield f"data: {json.dumps(initial)}\n\n"

            while True:
                if await request.is_disconnected():
                    break
                try:
                    update = await asyncio.wait_for(q.get(), timeout=30.0)
                    filtered = {k: v for k, v in update.items() if k in set(ticker_list)}
                    if filtered:
                        yield f"data: {json.dumps(filtered)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            broadcaster.remove_client(q)
            await broadcaster.unregister_tickers(ticker_list)

    return StreamingResponse(
        generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )
