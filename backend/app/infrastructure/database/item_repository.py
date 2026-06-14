from sqlalchemy.orm import Session

from app.domain.repositories.item_repository import IItemRepository
from app.infrastructure.database.models import Item


class SQLiteItemRepository(IItemRepository):
    def get_all(self, db: Session) -> list[Item]:
        return db.query(Item).order_by(Item.id).all()

    def create(self, db: Session, name: str) -> Item:
        item = Item(name=name)
        db.add(item)
        db.commit()
        db.refresh(item)
        return item
