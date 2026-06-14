import os
from dataclasses import dataclass, field

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclass
class Settings:
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./app.db")
    )
    edinet_api_key: str = field(
        default_factory=lambda: os.getenv("EDINET_API_KEY", "")
    )
    poll_interval: int = field(
        default_factory=lambda: int(os.getenv("POLL_INTERVAL", "30"))
    )
    csv_path: str = field(
        default_factory=lambda: os.path.join(_BASE_DIR, "../../codes.csv")
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
