from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_item_repository
from app.domain.repositories.item_repository import IItemRepository
from app.infrastructure.database.db import get_db
from app.schemas import ItemCreate, ItemRead

router = APIRouter(prefix="/items", tags=["items"])


@router.get("", response_model=list[ItemRead])
def list_items(
    db: Session = Depends(get_db),
    repo: IItemRepository = Depends(get_item_repository),
):
    return repo.get_all(db)


@router.post("", response_model=ItemRead, status_code=status.HTTP_201_CREATED)
def create_item(
    payload: ItemCreate,
    db: Session = Depends(get_db),
    repo: IItemRepository = Depends(get_item_repository),
):
    return repo.create(db, payload.name)
