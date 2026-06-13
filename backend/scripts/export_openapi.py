from pathlib import Path
import sys

import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app.main import app  # noqa: E402


def main() -> None:
    output_path = ROOT_DIR / "api.yml"
    with output_path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(app.openapi(), f, allow_unicode=True, sort_keys=False)
    print(f"OpenAPI schema generated: {output_path}")


if __name__ == "__main__":
    main()
