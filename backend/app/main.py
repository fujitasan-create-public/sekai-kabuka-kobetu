import asyncio
import logging

from dotenv import load_dotenv
load_dotenv()  # load backend/.env before any os.environ reads

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.dependencies import (
    get_broadcaster,
    get_cache_service,
    get_master_repository,
)
from app.core.config import get_settings
from app.api.v1.filings import router as filings_router
from app.api.v1.health import router as health_router
from app.api.v1.history import router as history_router
from app.api.v1.indicators import router as indicators_router
from app.api.v1.items import router as items_router
from app.api.v1.quote import router as quote_router
from app.api.v1.search import router as search_router
from app.api.v1.stream import router as stream_router
from app.infrastructure.streaming.poller import Poller

logging.basicConfig(level=logging.INFO)

app = FastAPI(title="Sekai Kabuka Kobetu API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(filings_router)
app.include_router(health_router)
app.include_router(search_router)
app.include_router(history_router)
app.include_router(quote_router)
app.include_router(indicators_router)
app.include_router(stream_router)
app.include_router(items_router)


@app.on_event("startup")
async def on_startup() -> None:
    get_master_repository().warm_up()

    settings = get_settings()
    broadcaster = get_broadcaster()
    cache = get_cache_service()

    poller = Poller(
        broadcaster=broadcaster,
        cache=cache,
        poll_interval=settings.poll_interval,
    )
    asyncio.create_task(poller.run())
