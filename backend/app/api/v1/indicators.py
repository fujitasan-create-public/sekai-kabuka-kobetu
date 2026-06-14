from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_indicators_use_case
from app.application.use_cases.get_indicators import GetIndicatorsUseCase
from app.infrastructure.external.ta_indicator_service import VALID_TYPES

router = APIRouter(prefix="/api", tags=["indicators"])


@router.get("/indicators")
async def get_indicators(
    ticker: str = Query(...),
    type: str = Query(..., description="macd|rsi|sma|ema|bb"),
    interval: str = Query(default="1d"),
    range: str = Query(default="6mo"),
    period: int = Query(default=14),
    fast: int = Query(default=12),
    slow: int = Query(default=26),
    signal: int = Query(default=9),
    use_case: GetIndicatorsUseCase = Depends(get_indicators_use_case),
) -> dict:
    if type not in VALID_TYPES:
        raise HTTPException(400, f"type must be one of {VALID_TYPES}")

    result = await use_case.execute(
        ticker=ticker,
        indicator_type=type,
        interval=interval,
        period_range=range,
        period=period,
        fast=fast,
        slow=slow,
        signal=signal,
    )
    return {"ticker": result.ticker, "type": result.type, "data": result.data}
