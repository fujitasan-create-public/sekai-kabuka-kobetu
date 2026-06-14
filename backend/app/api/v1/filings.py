from dataclasses import asdict

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_filing_service, get_filings_use_case
from app.application.interfaces.filing_service import IFilingService
from app.application.use_cases.get_filings import GetFilingsUseCase
from app.core.config import get_settings

router = APIRouter(prefix="/api", tags=["filings"])


@router.get("/filings")
async def get_filings(
    ticker: str = Query(...),
    use_case: GetFilingsUseCase = Depends(get_filings_use_case),
) -> dict:
    filings = await use_case.execute(ticker)
    filings_data = [
        {"form": f.form, "date": f.date, "description": f.description, "url": f.url}
        for f in filings
    ]

    is_japan = ticker.endswith(".T")
    if is_japan:
        return {
            "ticker": ticker,
            "source": "edinet",
            "has_key": bool(get_settings().edinet_api_key),
            "search_url": "https://disclosure2.edinet-fsa.go.jp/",
            "tdnet_url": "https://www.release.tdnet.info/",
            "filings": filings_data,
        }
    else:
        return {
            "ticker": ticker,
            "source": "sec_edgar",
            "has_key": True,
            "search_url": (
                f"https://www.sec.gov/cgi-bin/browse-edgar"
                f"?action=getcompany&CIK={ticker}&type=10-K&dateb=&owner=include&count=10"
            ),
            "filings": filings_data,
        }
