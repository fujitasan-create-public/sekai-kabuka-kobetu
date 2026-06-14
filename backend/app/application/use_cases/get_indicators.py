from app.application.interfaces.indicator_service import IIndicatorService
from app.domain.entities.stock import IndicatorResult


class GetIndicatorsUseCase:
    def __init__(self, indicator_service: IIndicatorService) -> None:
        self._service = indicator_service

    async def execute(
        self,
        ticker: str,
        indicator_type: str,
        interval: str,
        period_range: str,
        period: int = 14,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
    ) -> IndicatorResult:
        return await self._service.calculate(
            ticker=ticker,
            indicator_type=indicator_type,
            interval=interval,
            period_range=period_range,
            period=period,
            fast=fast,
            slow=slow,
            signal=signal,
        )
