"""DI wiring: singleton factories exposed as FastAPI Depends()-compatible callables."""
from __future__ import annotations

from functools import lru_cache

from app.application.interfaces.broadcaster import IBroadcaster
from app.application.interfaces.cache_service import ICacheService
from app.application.interfaces.filing_service import IFilingService
from app.application.interfaces.indicator_service import IIndicatorService
from app.application.interfaces.stock_service import IStockDataService
from app.application.use_cases.get_filings import GetFilingsUseCase
from app.application.use_cases.get_history import GetHistoryUseCase
from app.application.use_cases.get_indicators import GetIndicatorsUseCase
from app.application.use_cases.get_quote import GetQuoteUseCase
from app.application.use_cases.search_tickers import SearchTickersUseCase
from app.core.config import get_settings
from app.domain.repositories.item_repository import IItemRepository
from app.domain.repositories.master_repository import IMasterRepository
from app.infrastructure.cache.in_memory_cache import InMemoryCache
from app.infrastructure.database.item_repository import SQLiteItemRepository
from app.infrastructure.external.composite_filing_service import CompositeFilingService
from app.infrastructure.external.edinet_filing_service import EDINETFilingService
from app.infrastructure.external.sec_filing_service import SECFilingService
from app.infrastructure.external.ta_indicator_service import TALibIndicatorService
from app.infrastructure.external.tdnet_filing_service import TDNetFilingService
from app.infrastructure.external.yfinance_stock_service import YFinanceStockService
from app.infrastructure.master.csv_master_repository import CSVMasterRepository
from app.infrastructure.streaming.in_memory_broadcaster import InMemoryBroadcaster


# ── Singletons ─────────────────────────────────────────────────────────────

@lru_cache
def get_broadcaster() -> IBroadcaster:
    return InMemoryBroadcaster()


@lru_cache
def get_cache_service() -> ICacheService:
    return InMemoryCache()


@lru_cache
def get_master_repository() -> IMasterRepository:
    return CSVMasterRepository(csv_path=get_settings().csv_path)


@lru_cache
def get_stock_data_service() -> IStockDataService:
    return YFinanceStockService()


@lru_cache
def get_indicator_service() -> IIndicatorService:
    return TALibIndicatorService()


@lru_cache
def get_filing_service() -> IFilingService:
    settings = get_settings()
    return CompositeFilingService(
        sec=SECFilingService(),
        edinet=EDINETFilingService(api_key=settings.edinet_api_key),
        tdnet=TDNetFilingService(),
    )


@lru_cache
def get_item_repository() -> IItemRepository:
    return SQLiteItemRepository()


# ── Use case factories (not cached — lightweight, stateless) ───────────────

def get_search_use_case() -> SearchTickersUseCase:
    return SearchTickersUseCase(master_repo=get_master_repository())


def get_quote_use_case() -> GetQuoteUseCase:
    return GetQuoteUseCase(stock_service=get_stock_data_service())


def get_history_use_case() -> GetHistoryUseCase:
    return GetHistoryUseCase(stock_service=get_stock_data_service())


def get_indicators_use_case() -> GetIndicatorsUseCase:
    return GetIndicatorsUseCase(indicator_service=get_indicator_service())


def get_filings_use_case() -> GetFilingsUseCase:
    return GetFilingsUseCase(filing_service=get_filing_service())
