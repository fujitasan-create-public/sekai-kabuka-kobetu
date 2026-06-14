from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy.orm import Session


class IItemRepository(ABC):
    @abstractmethod
    def get_all(self, db: Session) -> list[Any]: ...

    @abstractmethod
    def create(self, db: Session, name: str) -> Any: ...
