import asyncio
import logging

import httpx

from app.domain.entities.filing import Filing

logger = logging.getLogger(__name__)

_SEC_HEADERS = {"User-Agent": "sekai-kabuka-kobetu contact@example.com"}
_EDGAR_FORMS = {"10-K", "10-Q", "20-F", "6-K"}


class SECFilingService:
    def __init__(self) -> None:
        self._ticker_map: dict[str, int] = {}
        self._lock = asyncio.Lock()

    async def _load_ticker_map(self) -> dict[str, int]:
        if self._ticker_map:
            return self._ticker_map
        async with self._lock:
            if self._ticker_map:
                return self._ticker_map
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(
                        "https://www.sec.gov/files/company_tickers.json",
                        headers=_SEC_HEADERS,
                        timeout=20.0,
                    )
                    resp.raise_for_status()
                    data = resp.json()
                    self._ticker_map = {
                        v["ticker"].upper(): v["cik_str"] for v in data.values()
                    }
            except Exception as e:
                logger.error("Failed to load SEC ticker map: %s", e)
        return self._ticker_map

    async def get_filings(self, ticker: str) -> list[Filing]:
        mapping = await self._load_ticker_map()
        cik = mapping.get(ticker.upper())
        if cik is None:
            return []

        cik_padded = f"{cik:010d}"
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"https://data.sec.gov/submissions/CIK{cik_padded}.json",
                    headers=_SEC_HEADERS,
                    timeout=15.0,
                )
                resp.raise_for_status()
                data = resp.json()
        except Exception as e:
            logger.error("SEC submissions fetch failed for %s: %s", ticker, e)
            return []

        recent = data.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        accessions = recent.get("accessionNumber", [])
        primary_docs = recent.get("primaryDocument", [])
        descriptions = recent.get("primaryDocDescription", [])

        results: list[Filing] = []
        for form, dt, acc, doc, desc in zip(forms, dates, accessions, primary_docs, descriptions):
            if form not in _EDGAR_FORMS:
                continue
            acc_clean = acc.replace("-", "")
            url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_clean}/{doc}"
            results.append(
                Filing(form=form, date=dt, description=desc or form, url=url, source="sec_edgar")
            )
            if len(results) >= 12:
                break

        return results
