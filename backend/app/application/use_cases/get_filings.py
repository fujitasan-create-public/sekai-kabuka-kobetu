from app.application.interfaces.filing_service import IFilingService
from app.domain.entities.filing import Filing


class GetFilingsUseCase:
    def __init__(self, filing_service: IFilingService) -> None:
        self._service = filing_service

    async def execute(self, ticker: str) -> list[Filing]:
        return await self._service.get_filings(ticker)
