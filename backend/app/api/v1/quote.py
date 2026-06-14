from dataclasses import asdict

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import get_quote_use_case
from app.application.use_cases.get_quote import GetQuoteUseCase

router = APIRouter(prefix="/api", tags=["quote"])


@router.get("/quote")
async def get_quote(
    ticker: str = Query(...),
    use_case: GetQuoteUseCase = Depends(get_quote_use_case),
) -> dict:
    quote = await use_case.execute(ticker)
    return {
        "ticker": quote.ticker,
        "longName": quote.long_name,
        "shortName": quote.short_name,
        "currency": quote.currency,
        "exchange": quote.exchange,
        "trailingPE": quote.trailing_pe,
        "forwardPE": quote.forward_pe,
        "priceToBook": quote.price_to_book,
        "marketCap": quote.market_cap,
        "dividendYield": quote.dividend_yield,
        "trailingEps": quote.trailing_eps,
        "fiftyTwoWeekHigh": quote.fifty_two_week_high,
        "fiftyTwoWeekLow": quote.fifty_two_week_low,
        "volume": quote.volume,
        "averageVolume": quote.average_volume,
        "beta": quote.beta,
        "sector": quote.sector,
        "industry": quote.industry,
    }
