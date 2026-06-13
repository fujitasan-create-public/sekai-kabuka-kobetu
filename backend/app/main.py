import asyncio
import logging

from dotenv import load_dotenv
load_dotenv()  # load backend/.env before any os.environ reads

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.filings import router as filings_router
from app.api.health import router as health_router
from app.api.history import router as history_router
from app.api.indicators import router as indicators_router
from app.api.quote import router as quote_router
from app.api.search import router as search_router
from app.api.stream import router as stream_router
from app.data.master import get_master
from app.data.poller import run_poller

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


@app.on_event("startup")
async def on_startup() -> None:
    get_master()  # warm up CSV cache
    asyncio.create_task(run_poller())
