import asyncio
import logging
from datetime import date, timedelta
from time import monotonic

import httpx

from app.domain.entities.filing import Filing

logger = logging.getLogger(__name__)

_EDINET_DOC_TYPES = {
    "120": "有価証券報告書",
    "140": "四半期報告書",
    "160": "半期報告書",
    "130": "訂正有価証券報告書",
    "150": "訂正四半期報告書",
}
_CACHE_TTL = 3600.0


class EDINETFilingService:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key
        self._cache: dict[str, tuple[float, list[Filing]]] = {}

    async def get_filings(self, sec_code: str) -> list[Filing]:
        if not self._api_key:
            return []

        cached = self._cache.get(sec_code)
        if cached and monotonic() - cached[0] < _CACHE_TTL:
            return cached[1]

        edinet_sec_code = sec_code + "0"
        today = date.today()
        # 過去13ヶ月（約395日）を検索して四半期ごとの提出を漏らさず捕捉する
        dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(395)]

        sem = asyncio.Semaphore(30)
        async with httpx.AsyncClient() as client:
            tasks = [self._fetch_day(client, sem, d) for d in dates]
            day_results = await asyncio.gather(*tasks)

        filings: list[Filing] = []
        seen: set[str] = set()
        for docs in day_results:
            for doc in docs:
                if doc.get("secCode") != edinet_sec_code:
                    continue
                doc_type = doc.get("docTypeCode", "")
                if doc_type not in _EDINET_DOC_TYPES:
                    continue
                doc_id = doc.get("docID", "")
                if not doc_id or doc_id in seen:
                    continue
                seen.add(doc_id)
                filings.append(
                    Filing(
                        form=_EDINET_DOC_TYPES[doc_type],
                        date=(doc.get("submitDateTime") or "")[:10],
                        description=doc.get("docDescription") or _EDINET_DOC_TYPES[doc_type],
                        url=f"https://disclosure2.edinet-fsa.go.jp/WZEK0040.aspx?{doc_id},,",
                        source="edinet",
                    )
                )

        result = sorted(filings, key=lambda x: x.date, reverse=True)[:12]
        self._cache[sec_code] = (monotonic(), result)
        return result

    async def _fetch_day(
        self,
        client: httpx.AsyncClient,
        sem: asyncio.Semaphore,
        date_str: str,
    ) -> list[dict]:
        async with sem:
            try:
                resp = await client.get(
                    "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json",
                    params={"date": date_str, "type": 2, "Subscription-Key": self._api_key},
                    timeout=10.0,
                )
                if resp.status_code != 200:
                    return []
                return resp.json().get("results", []) or []
            except Exception:
                return []
