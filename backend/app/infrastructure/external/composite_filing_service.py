from app.application.interfaces.filing_service import IFilingService
from app.domain.entities.filing import Filing
from app.infrastructure.external.edinet_filing_service import EDINETFilingService
from app.infrastructure.external.sec_filing_service import SECFilingService
from app.infrastructure.external.tdnet_filing_service import TDNetFilingService


class CompositeFilingService(IFilingService):
    """日本株 → EDINET + TDnet、米国株 → SEC EDGAR にルーティングする。"""

    def __init__(
        self,
        sec: SECFilingService,
        edinet: EDINETFilingService,
        tdnet: TDNetFilingService,
    ) -> None:
        self._sec = sec
        self._edinet = edinet
        self._tdnet = tdnet

    async def get_filings(self, ticker: str) -> list[Filing]:
        if ticker.endswith(".T"):
            sec_code = ticker.removesuffix(".T")
            import asyncio
            edinet_task = asyncio.create_task(self._edinet.get_filings(sec_code))
            tdnet_task = asyncio.create_task(self._tdnet.get_filings(sec_code))
            edinet_filings, tdnet_filings = await asyncio.gather(edinet_task, tdnet_task)
            return sorted(
                edinet_filings + tdnet_filings,
                key=lambda x: x.date,
                reverse=True,
            )
        else:
            return await self._sec.get_filings(ticker)
