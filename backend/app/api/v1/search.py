from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_search_use_case
from app.application.use_cases.search_tickers import SearchTickersUseCase

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
def search(
    q: str = Query(default="", description="部分一致検索ワード"),
    use_case: SearchTickersUseCase = Depends(get_search_use_case),
) -> list[dict]:
    results = use_case.execute(q)
    return [{"ticker": r.ticker, "name": r.name, "market": r.market} for r in results]
