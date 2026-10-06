"""Load and validate curriculum rows once for the tools module."""

import json
from functools import lru_cache
from pathlib import Path

from app.schemas.contract import Course


DATA_FILE = Path(__file__).resolve().parents[5] / "data" / "curriculum" / "curriculum.json"


@lru_cache(maxsize=1)
def _load_data() -> dict:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def load_curriculum() -> list[Course]:
    return [Course.model_validate(row) for row in _load_data()["courses"]]


def load_program_total_credits() -> int:
    return int(_load_data()["total_credits"])
