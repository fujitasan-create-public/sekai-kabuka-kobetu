from abc import ABC, abstractmethod

from app.domain.entities.stock import IndicatorResult


class IIndicatorService(ABC):
    @abstractmethod
    async def calculate(
        self,
        ticker: str,
        indicator_type: str,
        interval: str,
        period_range: str,
        period: int = 14,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
    ) -> IndicatorResult: ...
