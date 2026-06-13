from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.items import router as items_router
from app.db import Base, engine

app = FastAPI(title="Template FastAPI", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(health_router)
app.include_router(items_router)
