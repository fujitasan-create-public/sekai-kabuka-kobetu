from __future__ import annotations

import asyncio
from typing import Any

from app.application.interfaces.broadcaster import IBroadcaster


class InMemoryBroadcaster(IBroadcaster):
    def __init__(self) -> None:
        self._clients: list[asyncio.Queue[dict[str, Any]]] = []
        self._watched: set[str] = set()
        self._lock = asyncio.Lock()

    def add_client(self, q: asyncio.Queue[dict[str, Any]]) -> None:
        self._clients.append(q)

    def remove_client(self, q: asyncio.Queue[dict[str, Any]]) -> None:
        try:
            self._clients.remove(q)
        except ValueError:
            pass

    async def register_tickers(self, tickers: list[str]) -> None:
        async with self._lock:
            self._watched.update(tickers)

    async def unregister_tickers(self, tickers: list[str]) -> None:
        async with self._lock:
            for t in tickers:
                self._watched.discard(t)

    def get_watched(self) -> set[str]:
        return set(self._watched)

    async def broadcast(self, data: dict[str, Any]) -> None:
        for q in list(self._clients):
            await q.put(data)
