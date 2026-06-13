from fastapi import APIRouter, Query

from app.data.master import get_master

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
def search(q: str = Query(default="", description="部分一致検索ワード")) -> list[dict]:
    if not q:
        return []
    q_lower = q.lower()
    results = []
    for rec in get_master():
        if q_lower in rec.ticker.lower() or q_lower in rec.name.lower():
            results.append({"ticker": rec.ticker, "name": rec.name, "market": rec.market})
        if len(results) >= 30:
            break
    return results
