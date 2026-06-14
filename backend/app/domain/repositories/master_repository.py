from abc import ABC, abstractmethod

from app.domain.entities.ticker import TickerInfo


class IMasterRepository(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 30) -> list[TickerInfo]: ...

    @abstractmethod
    def get_all(self) -> list[TickerInfo]: ...

    def warm_up(self) -> None:
        """Pre-load data eagerly. Override if the repository is lazy-loaded."""
