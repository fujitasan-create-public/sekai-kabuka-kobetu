from app.application.interfaces.stock_service import IStockDataService
from app.domain.entities.stock import StockQuote


class GetQuoteUseCase:
    def __init__(self, stock_service: IStockDataService) -> None:
        self._service = stock_service

    async def execute(self, ticker: str) -> StockQuote:
        return await self._service.get_quote(ticker)
