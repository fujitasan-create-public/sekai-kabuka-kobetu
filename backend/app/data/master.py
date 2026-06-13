import csv
import os
from dataclasses import dataclass

_CSV_PATH = os.path.join(os.path.dirname(__file__), "../../codes.csv")


@dataclass
class TickerRecord:
    name: str
    ticker: str
    market: str


_master: list[TickerRecord] | None = None


def get_master() -> list[TickerRecord]:
    global _master
    if _master is None:
        _master = _load()
    return _master


def _load() -> list[TickerRecord]:
    records = []
    with open(_CSV_PATH, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("銘柄名", "").strip()
            ticker = row.get("銘柄コード", "").strip()
            market = row.get("市場", "").strip()
            if ticker:
                records.append(TickerRecord(name=name, ticker=ticker, market=market))
    return records
