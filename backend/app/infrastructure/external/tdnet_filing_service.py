import asyncio
import logging
import re
from datetime import date, timedelta
from time import monotonic

import httpx
from bs4 import BeautifulSoup

from app.domain.entities.filing import Filing

logger = logging.getLogger(__name__)

_TDNET_BASE = "https://www.release.tdnet.info/inbs"
_TDNET_UA = {"User-Agent": "Mozilla/5.0 (compatible; sekai-kabuka-kobetu)"}
_CACHE_TTL = 3600.0


class TDNetFilingService:
    def __init__(self) -> None:
        self._cache: dict[str, tuple[float, list[Filing]]] = {}

    async def get_filings(self, sec_code: str) -> list[Filing]:
        cached = self._cache.get(sec_code)
        if cached and monotonic() - cached[0] < _CACHE_TTL:
            return cached[1]

        code5 = sec_code + "0"
        today = date.today()
        target_dates = _target_dates(today)

        sem = asyncio.Semaphore(25)
        async with httpx.AsyncClient(headers=_TDNET_UA) as client:
            all_results = await asyncio.gather(*[
                self._fetch_date(client, sem, d, code5) for d in target_dates
            ])

        filings: list[Filing] = []
        seen: set[str] = set()
        for day_filings in all_results:
            for f in day_filings:
                if f.description not in seen:
                    seen.add(f.description)
                    filings.append(f)

        result = sorted(filings, key=lambda x: x.date, reverse=True)[:8]
        self._cache[sec_code] = (monotonic(), result)
        return result

    async def _fetch_date(
        self,
        client: httpx.AsyncClient,
        sem: asyncio.Semaphore,
        date_str: str,
        code5: str,
    ) -> list[Filing]:
        url1 = f"{_TDNET_BASE}/I_list_001_{date_str}.html"
        filings, total = await _parse_page(client, sem, url1, code5)

        if total > 100:
            max_page = min((total + 99) // 100, 8)
            extra = await asyncio.gather(*[
                _parse_page(client, sem, f"{_TDNET_BASE}/I_list_{p:03d}_{date_str}.html", code5)
                for p in range(2, max_page + 1)
            ])
            for extra_filings, _ in extra:
                filings.extend(extra_filings)

        formatted = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        return [
            Filing(
                form=f.form,
                date=formatted,
                description=f.description,
                url=f.url,
                source="tdnet",
            )
            for f in filings
        ]


async def _parse_page(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    url: str,
    code5: str,
) -> tuple[list[Filing], int]:
    async with sem:
        try:
            resp = await client.get(url, timeout=10.0)
            if resp.status_code != 200:
                return [], 0
        except Exception:
            return [], 0

    soup = BeautifulSoup(resp.text, "html.parser")

    total = 0
    sum_div = soup.find(class_="kaijiSum")
    if sum_div:
        m = re.search(r"全(\d+)件", sum_div.get_text())
        if m:
            total = int(m.group(1))

    table = soup.find("table", id="main-list-table")
    if not table:
        return [], total

    results: list[Filing] = []
    for row in table.find_all("tr"):
        code_td = row.find(lambda t: t.name == "td" and "kjCode" in (t.get("class") or []))
        title_td = row.find(lambda t: t.name == "td" and "kjTitle" in (t.get("class") or []))
        if not code_td or not title_td:
            continue
        if code_td.get_text(strip=True) != code5:
            continue
        link = title_td.find("a")
        if not link:
            continue
        title_text = link.get_text(strip=True)
        if "決算短信" not in title_text:
            continue
        href = link.get("href", "")
        results.append(
            Filing(
                form="決算短信",
                date="",
                description=title_text,
                url=f"{_TDNET_BASE}/{href}" if href else "",
                source="tdnet",
            )
        )

    return results, total


def _target_dates(today: date) -> list[str]:
    """四半期提出ウィンドウ（各QE+25〜55日）の平日を生成。過去2年分。"""
    dates: set[str] = set()
    quarter_ends = [(3, 31), (6, 30), (9, 30), (12, 31)]
    for yr in range(today.year - 1, today.year + 1):
        for mo, dy in quarter_ends:
            try:
                qe = date(yr, mo, dy)
            except ValueError:
                continue
            for delta in range(25, 56):
                d = qe + timedelta(days=delta)
                if d > today:
                    break
                if d.weekday() < 5:
                    dates.add(d.strftime("%Y%m%d"))
    for i in range(30):
        d = today - timedelta(days=i)
        if d.weekday() < 5:
            dates.add(d.strftime("%Y%m%d"))
    return sorted(dates, reverse=True)
