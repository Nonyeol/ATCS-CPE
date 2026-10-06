"""Public curriculum queries backed by the verified JSON study plan."""

from rapidfuzz import fuzz, utils

from app.schemas.contract import CardsData, Course, CourseTableData, InfoCard

from .loader import load_curriculum, load_program_total_credits


def get_courses(year: int, semester: int) -> CourseTableData | None:
    if year not in range(1, 5) or semester not in (1, 2):
        return None
    courses = sorted(
        (course for course in load_curriculum() if (course.year, course.semester) == (year, semester)),
        key=lambda course: (course.code, course.name_th),
    )
    if not courses:
        return None
    return CourseTableData(
        year=year,
        semester=semester,
        courses=courses,
        total_credits=sum(course.credits for course in courses),
    )


def _normalized_code(value: str) -> str:
    return "".join(character for character in value.casefold() if character.isalnum())


def get_course_detail(query: str) -> Course | None:
    query = query.strip()
    if not query:
        return None
    concrete_courses = [course for course in load_curriculum() if "x" not in course.code]
    code = _normalized_code(query)
    for course in concrete_courses:
        if code == _normalized_code(course.code):
            return course

    best_course = None
    best_score = 0.0
    for course in concrete_courses:
        for name in (course.name_th, course.name_en):
            if not name:
                continue
            score = fuzz.WRatio(query, name, processor=utils.default_process)
            if score > best_score:
                best_course, best_score = course, score
    return best_course if best_score >= 80 else None


def get_total_credits(year: int | None = None, semester: int | None = None) -> int:
    if year is None and semester is None:
        return load_program_total_credits()
    return sum(
        course.credits
        for course in load_curriculum()
        if (year is None or course.year == year)
        and (semester is None or course.semester == semester)
    )


def get_curriculum_overview() -> CardsData:
    cards = []
    for year in range(1, 5):
        courses = [course for course in load_curriculum() if course.year == year]
        if courses:
            featured = [course.name_th for course in courses if "x" not in course.code][:4]
            body = f"รวม {sum(course.credits for course in courses)} หน่วยกิต"
            if featured:
                body += "\n\nวิชาเด่น: " + ", ".join(featured)
            tags = sorted({course.category for course in courses if course.category})
        else:
            body, tags = "ยังไม่มีข้อมูลรายวิชา", []
        cards.append(InfoCard(title=f"ปี {year}", body=body, tags=tags))
    return CardsData(cards=cards)
