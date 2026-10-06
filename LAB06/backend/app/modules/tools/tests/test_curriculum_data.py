"""Checks for the published eight-term curriculum plan."""

import json
from collections import Counter
from copy import deepcopy
from pathlib import Path

import pytest

from app.schemas.contract import Course
from app.modules.tools.curriculum.validate import validate_curriculum


DATA_FILE = Path(__file__).resolve().parents[5] / "data" / "curriculum" / "curriculum.json"


def test_curriculum_matches_study_plan() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    courses = [Course.model_validate(row) for row in data["courses"]]

    assert data["curriculum_year"] == "2568"
    assert data["total_credits"] == 141
    assert len(courses) == 51
    assert {(course.year, course.semester) for course in courses} == {
        (year, semester) for year in range(1, 5) for semester in (1, 2)
    }

    totals = Counter()
    for course in courses:
        totals[(course.year, course.semester)] += course.credits
    assert dict(totals) == {
        (1, 1): 19, (1, 2): 21, (2, 1): 20, (2, 2): 21,
        (3, 1): 20, (3, 2): 19, (4, 1): 6, (4, 2): 15,
    }
    assert validate_curriculum(data) == dict(totals)

    concrete_codes = [course.code for course in courses if "x" not in course.code]
    assert len(concrete_codes) == len(set(concrete_codes))


def test_validator_rejects_duplicate_concrete_code() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    duplicate = deepcopy(next(row for row in data["courses"] if row["code"] == "04-622-201"))
    data["courses"].append(duplicate)
    with pytest.raises(ValueError, match="Duplicate course code"):
        validate_curriculum(data)


def test_validator_rejects_wrong_program_total() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    data["total_credits"] -= 1
    with pytest.raises(ValueError, match="program total"):
        validate_curriculum(data)
