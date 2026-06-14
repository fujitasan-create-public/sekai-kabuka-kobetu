from dataclasses import dataclass, field


@dataclass(frozen=True)
class Filing:
    form: str
    date: str
    description: str
    url: str
    source: str = field(default="unknown")
