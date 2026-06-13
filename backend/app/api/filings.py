import asyncio
import logging
import os
from datetime import date, timedelta
from time import monotonic

import httpx
from fastapi import APIRouter, Query

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["filings"])

SEC_HEADERS = {"User-Agent": "sekai-kabuka-kobetu contact@example.com"}
EDGAR_FORMS = {"10-K", "10-Q", "20-F", "6-K"}

EDINET_DOC_TYPES = {
    "120": "有価証券報告書",
    "140": "四半期報告書",
    "160": "半期報告書",
    "130": "訂正有価証券報告書",
    "150": "訂正四半期報告書",
}

# ── SEC EDGAR ──────────────────────────────────────────────────────────────

_sec_ticker_map: dict[str, int] = {}
_sec_map_lock = asyncio.Lock()


async def _load_sec_ticker_map() -> dict[str, int]:
    global _sec_ticker_map
    if _sec_ticker_map:
        return _sec_ticker_map
    async with _sec_map_lock:
        if _sec_ticker_map:
            return _sec_ticker_map
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    "https://www.sec.gov/files/company_tickers.json",
                    headers=SEC_HEADERS,
                    timeout=20.0,
                )
                resp.raise_for_status()
                data = resp.json()
                _sec_ticker_map = {v["ticker"].upper(): v["cik_str"] for v in data.values()}
        except Exception as e:
            logger.error("Failed to load SEC ticker map: %s", e)
    return _sec_ticker_map


async def _fetch_sec_filings(ticker: str) -> list[dict]:
    mapping = await _load_sec_ticker_map()
    cik = mapping.get(ticker.upper())
    if cik is None:
        return []

    cik_padded = f"{cik:010d}"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://data.sec.gov/submissions/CIK{cik_padded}.json",
                headers=SEC_HEADERS,
                timeout=15.0,
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.error("SEC submissions fetch failed for %s: %s", ticker, e)
        return []

    recent = data.get("filings", {}).get("recent", {})
    forms         = recent.get("form", [])
    dates         = recent.get("filingDate", [])
    accessions    = recent.get("accessionNumber", [])
    primary_docs  = recent.get("primaryDocument", [])
    descriptions  = recent.get("primaryDocDescription", [])

    results = []
    for form, dt, acc, doc, desc in zip(forms, dates, accessions, primary_docs, descriptions):
        if form not in EDGAR_FORMS:
            continue
        acc_clean = acc.replace("-", "")
        url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_clean}/{doc}"
        results.append({"form": form, "date": dt, "description": desc or form, "url": url})
        if len(results) >= 12:
            break

    return results


# ── EDINET ─────────────────────────────────────────────────────────────────

def _edinet_key() -> str:
    return os.environ.get("EDINET_API_KEY", "")


# (sec_code → (fetched_at, filings)) — 1時間キャッシュ
_edinet_cache: dict[str, tuple[float, list[dict]]] = {}
_EDINET_CACHE_TTL = 3600.0


async def _fetch_edinet_day(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    date_str: str,
    api_key: str,
) -> list[dict]:
    async with sem:
        try:
            resp = await client.get(
                "https://disclosure.edinet-fsa.go.jp/api/v2/documents.json",
                params={"date": date_str, "type": 2, "Subscription-Key": api_key},
                timeout=10.0,
            )
            if resp.status_code != 200:
                return []
            return resp.json().get("results", []) or []
        except Exception:
            return []


async def _fetch_edinet_filings(sec_code: str) -> list[dict]:
    api_key = _edinet_key()
    if not api_key:
        return []

    # キャッシュヒット確認
    cached = _edinet_cache.get(sec_code)
    if cached and monotonic() - cached[0] < _EDINET_CACHE_TTL:
        return cached[1]

    # EDINET secCode は TSE 4桁 + 末尾 "0" の 5桁
    edinet_sec_code = sec_code + "0"

    today = date.today()
    # 過去13ヶ月の全日付 ≈ 395件。四半期ごとの提出日（8月・11月・2月・5〜7月）を漏らさず捕捉する。
    dates = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(395)]

    sem = asyncio.Semaphore(30)
    async with httpx.AsyncClient() as client:
        tasks = [_fetch_edinet_day(client, sem, d, api_key) for d in dates]
        day_results = await asyncio.gather(*tasks)

    filings: list[dict] = []
    seen: set[str] = set()
    for docs in day_results:
        for doc in docs:
            if doc.get("secCode") != edinet_sec_code:
                continue
            doc_type = doc.get("docTypeCode", "")
            if doc_type not in EDINET_DOC_TYPES:
                continue
            doc_id = doc.get("docID", "")
            if not doc_id or doc_id in seen:
                continue
            seen.add(doc_id)
            filings.append({
                "form": EDINET_DOC_TYPES[doc_type],
                "date": (doc.get("submitDateTime") or "")[:10],
                "description": doc.get("docDescription") or EDINET_DOC_TYPES[doc_type],
                "url": f"https://disclosure2.edinet-fsa.go.jp/WZEK0040.aspx?{doc_id},,",
            })

    result = sorted(filings, key=lambda x: x["date"], reverse=True)[:12]
    _edinet_cache[sec_code] = (monotonic(), result)
    return result


# ── Router ─────────────────────────────────────────────────────────────────

@router.get("/filings")
async def get_filings(ticker: str = Query(...)) -> dict:
    is_japan = ticker.endswith(".T")

    if is_japan:
        sec_code = ticker.replace(".T", "")
        filings = await _fetch_edinet_filings(sec_code)
        return {
            "ticker": ticker,
            "source": "edinet",
            "has_key": bool(_edinet_key()),
            "search_url": "https://disclosure2.edinet-fsa.go.jp/",
            "filings": filings,
        }
    else:
        filings = await _fetch_sec_filings(ticker)
        return {
            "ticker": ticker,
            "source": "sec_edgar",
            "has_key": True,
            "search_url": (
                f"https://www.sec.gov/cgi-bin/browse-edgar"
                f"?action=getcompany&CIK={ticker}&type=10-K&dateb=&owner=include&count=10"
            ),
            "filings": filings,
        }
