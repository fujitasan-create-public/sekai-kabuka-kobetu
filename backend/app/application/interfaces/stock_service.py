from abc import ABC, abstractmethod

from app.domain.entities.stock import OHLCVBar, StockQuote


class IStockDataService(ABC):
    @abstractmethod
    async def get_quote(self, ticker: str) -> StockQuote: ...

    @abstractmethod
    async def get_ohlcv(self, ticker: str, period: str, interval: str) -> list[OHLCVBar]: ...
