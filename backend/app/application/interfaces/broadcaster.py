from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any


class IBroadcaster(ABC):
    @abstractmethod
    def add_client(self, q: asyncio.Queue[dict[str, Any]]) -> None: ...

    @abstractmethod
    def remove_client(self, q: asyncio.Queue[dict[str, Any]]) -> None: ...

    @abstractmethod
    async def register_tickers(self, tickers: list[str]) -> None: ...

    @abstractmethod
    async def unregister_tickers(self, tickers: list[str]) -> None: ...

    @abstractmethod
    def get_watched(self) -> set[str]: ...

    @abstractmethod
    async def broadcast(self, data: dict[str, Any]) -> None: ...
