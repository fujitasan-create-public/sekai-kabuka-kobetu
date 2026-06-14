from abc import ABC, abstractmethod

from app.domain.entities.filing import Filing


class IFilingService(ABC):
    @abstractmethod
    async def get_filings(self, ticker: str) -> list[Filing]: ...
