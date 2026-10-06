"""Contract-facing tests for the curriculum tool."""

from app.modules.tools import (
    get_course_detail,
    get_courses,
    get_curriculum_overview,
    get_total_credits,
)
from app.modules.tools.curriculum.loader import load_curriculum
from app.schemas.contract import CardsData, CourseTableData


def test_every_available_term_returns_verified_total() -> None:
    terms = {(course.year, course.semester) for course in load_curriculum()}
    for year, semester in terms:
        result = get_courses(year, semester)
        assert isinstance(result, CourseTableData)
        assert result.total_credits == sum(course.credits for course in result.courses)
        assert [course.code for course in result.courses] == sorted(course.code for course in result.courses)
    assert get_courses(5, 1) is None


def test_course_detail_accepts_code_and_near_name() -> None:
    assert get_course_detail("04-622-201").name_en == "Data Structure and Algorithms"
    assert get_course_detail("04622201").code == "04-622-201"
    assert get_course_detail("Computer Programing").code == "04-621-101"
    assert get_course_detail("not a course") is None


def test_course_detail_matches_short_names_and_case() -> None:
    assert get_course_detail("Data Structure").code == "04-622-201"
    assert get_course_detail("data structure").code == "04-622-201"
    assert get_course_detail("โครงสร้างข้อมูล").code == "04-622-201"
    assert get_course_detail("Database").code == "04-622-202"


def test_credits_and_overview_use_data_file() -> None:
    assert get_total_credits() == 141
    assert get_total_credits(year=1, semester=1) == 19
    assert get_total_credits(year=1) == 40
    overview = get_curriculum_overview()
    assert isinstance(overview, CardsData)
    assert len(overview.cards) == 4
    assert "40 หน่วยกิต" in overview.cards[0].body
