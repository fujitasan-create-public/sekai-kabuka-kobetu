"""SSE broadcaster: poller puts updates here, SSE clients consume them."""
import asyncio
from typing import Any

_clients: list[asyncio.Queue[dict[str, Any]]] = []
_watched: set[str] = set()
_watched_lock = asyncio.Lock()


def add_client(q: "asyncio.Queue[dict[str, Any]]") -> None:
    _clients.append(q)


def remove_client(q: "asyncio.Queue[dict[str, Any]]") -> None:
    try:
        _clients.remove(q)
    except ValueError:
        pass


async def register_tickers(tickers: list[str]) -> None:
    async with _watched_lock:
        _watched.update(tickers)


async def unregister_tickers(tickers: list[str]) -> None:
    async with _watched_lock:
        for t in tickers:
            _watched.discard(t)


def get_watched() -> set[str]:
    return set(_watched)


async def broadcast(data: dict[str, Any]) -> None:
    for q in list(_clients):
        await q.put(data)
