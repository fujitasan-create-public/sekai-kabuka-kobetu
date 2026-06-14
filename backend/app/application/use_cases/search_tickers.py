from app.domain.entities.ticker import TickerInfo
from app.domain.repositories.master_repository import IMasterRepository


class SearchTickersUseCase:
    def __init__(self, master_repo: IMasterRepository) -> None:
        self._repo = master_repo

    def execute(self, query: str, limit: int = 30) -> list[TickerInfo]:
        if not query:
            return []
        return self._repo.search(query, limit)
