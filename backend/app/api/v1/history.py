from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_history_use_case
from app.application.use_cases.get_history import VALID_INTERVALS, VALID_RANGES, GetHistoryUseCase

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history")
async def get_history(
    ticker: str = Query(...),
    interval: str = Query(default="1d"),
    range: str = Query(default="6mo"),
    use_case: GetHistoryUseCase = Depends(get_history_use_case),
) -> dict:
    if interval not in VALID_INTERVALS:
        raise HTTPException(400, f"interval must be one of {VALID_INTERVALS}")
    if range not in VALID_RANGES:
        raise HTTPException(400, f"range must be one of {VALID_RANGES}")

    bars = await use_case.execute(ticker=ticker, period=range, interval=interval)
    data = [
        {"t": b.t, "o": b.o, "h": b.h, "l": b.l, "c": b.c, "v": b.v} for b in bars
    ]
    return {"ticker": ticker, "interval": interval, "range": range, "data": data}
