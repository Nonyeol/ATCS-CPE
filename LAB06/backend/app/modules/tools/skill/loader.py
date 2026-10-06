"""Load and check the versioned skill questionnaire once."""

import json
from collections import Counter
from functools import lru_cache
from pathlib import Path

from app.schemas.contract import AssessmentOption, SKILL_KEYS


DATA_FILE = Path(__file__).resolve().parents[5] / "data" / "assessment" / "skill_v1.json"


@lru_cache(maxsize=1)
def load_assessment() -> dict:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    if data["assessment_id"] != "skill_v1" or len(data["questions"]) != 12:
        raise ValueError("Expected skill_v1 with 12 questions")
    if sorted(option["value"] for option in data["scale"]) != list(range(5)):
        raise ValueError("Scale must contain values 0 through 4")
    for option in data["scale"]:
        AssessmentOption.model_validate(option)

    primary_skills: Counter[str] = Counter()
    question_ids = set()
    for question in data["questions"]:
        if not question["text"].strip() or question["id"] in question_ids:
            raise ValueError("Question text must exist and IDs must be unique")
        question_ids.add(question["id"])
        weights = question["weights"]
        primary = [skill for skill, weight in weights.items() if weight == 1.0]
        if len(primary) != 1:
            raise ValueError("Each question needs one primary skill")
        primary_skills[primary[0]] += 1
        for skill, weight in weights.items():
            if skill not in SKILL_KEYS or weight <= 0:
                raise ValueError("Invalid skill weight")
            if skill != primary[0] and weight > 0.3:
                raise ValueError("Cross-skill weight must be at most 0.3")
    if set(question_ids) != {f"q{number}" for number in range(1, 13)}:
        raise ValueError("Question IDs must be q1 through q12")
    if any(primary_skills[skill] != 2 for skill in SKILL_KEYS):
        raise ValueError("Each skill needs two primary questions")
    return data
