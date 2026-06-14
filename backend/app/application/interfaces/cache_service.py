from abc import ABC, abstractmethod

from app.domain.entities.stock import StockSnapshot


class ICacheService(ABC):
    @abstractmethod
    def set_snapshot(self, ticker: str, snapshot: StockSnapshot) -> None: ...

    @abstractmethod
    def get_snapshot(self, ticker: str) -> StockSnapshot | None: ...

    @abstractmethod
    def get_all_snapshots(self) -> dict[str, StockSnapshot]: ...
