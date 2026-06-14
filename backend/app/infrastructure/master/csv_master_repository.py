import csv
import logging

from app.domain.entities.ticker import TickerInfo
from app.domain.repositories.master_repository import IMasterRepository

logger = logging.getLogger(__name__)


class CSVMasterRepository(IMasterRepository):
    def __init__(self, csv_path: str) -> None:
        self._csv_path = csv_path
        self._records: list[TickerInfo] | None = None

    def warm_up(self) -> None:
        self._load()

    def search(self, query: str, limit: int = 30) -> list[TickerInfo]:
        q = query.lower()
        results: list[TickerInfo] = []
        for rec in self._load():
            if q in rec.ticker.lower() or q in rec.name.lower():
                results.append(rec)
            if len(results) >= limit:
                break
        return results

    def get_all(self) -> list[TickerInfo]:
        return list(self._load())

    def _load(self) -> list[TickerInfo]:
        if self._records is None:
            self._records = self._parse_csv()
        return self._records

    def _parse_csv(self) -> list[TickerInfo]:
        records: list[TickerInfo] = []
        try:
            with open(self._csv_path, encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row.get("銘柄名", "").strip()
                    ticker = row.get("銘柄コード", "").strip()
                    market = row.get("市場", "").strip()
                    if ticker:
                        records.append(TickerInfo(name=name, ticker=ticker, market=market))
        except Exception as e:
            logger.error("Failed to load master CSV from %s: %s", self._csv_path, e)
        return records
