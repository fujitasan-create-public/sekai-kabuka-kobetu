from app.application.interfaces.cache_service import ICacheService
from app.domain.entities.stock import StockSnapshot


class InMemoryCache(ICacheService):
    def __init__(self) -> None:
        self._store: dict[str, StockSnapshot] = {}

    def set_snapshot(self, ticker: str, snapshot: StockSnapshot) -> None:
        self._store[ticker] = snapshot

    def get_snapshot(self, ticker: str) -> StockSnapshot | None:
        return self._store.get(ticker)

    def get_all_snapshots(self) -> dict[str, StockSnapshot]:
        return dict(self._store)
