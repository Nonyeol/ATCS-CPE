"""Validate the curriculum data against the published study-plan totals."""

import json
from collections import Counter
from pathlib import Path

from app.schemas.contract import Course


DATA_FILE = Path(__file__).resolve().parents[5] / "data" / "curriculum" / "curriculum.json"


def validate_curriculum(data: dict) -> dict[tuple[int, int], int]:
    if not isinstance(data.get("total_credits"), int) or data["total_credits"] <= 0:
        raise ValueError("total_credits must be a positive integer")

    term_credits: Counter[tuple[int, int]] = Counter()
    concrete_codes: set[str] = set()
    for row in data["courses"]:
        course = Course.model_validate(row)
        if course.year not in range(1, 5) or course.semester not in (1, 2):
            raise ValueError(f"Invalid year or semester: {course.code}")
        if course.credits <= 0:
            raise ValueError(f"Invalid credits: {course.code}")
        if "x" not in course.code.lower():
            if course.code in concrete_codes:
                raise ValueError(f"Duplicate course code: {course.code}")
            concrete_codes.add(course.code)
        term_credits[(course.year, course.semester)] += course.credits

    if set(term_credits) != {(year, term) for year in range(1, 5) for term in (1, 2)}:
        raise ValueError("The study plan must include all eight year/semester pairs")
    if sum(term_credits.values()) != data["total_credits"]:
        raise ValueError("Course credits do not match the program total")
    return dict(term_credits)


def main() -> None:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    totals = validate_curriculum(data)
    print(f"Curriculum {data['curriculum_year']}: {data['total_credits']} credits")
    for (year, semester), credits in sorted(totals.items()):
        print(f"Year {year}, semester {semester}: {credits} credits")
    print("Compare these term totals with the official study plan before each data PR.")


if __name__ == "__main__":
    main()
