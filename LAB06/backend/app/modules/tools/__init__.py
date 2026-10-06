"""Public API of the tools module (P5).

Other modules import only from `app.modules.tools`, never from its internal files.
"""

from .curriculum.service import (
    get_course_detail,
    get_courses,
    get_curriculum_overview,
    get_total_credits,
)
from .skill.service import calculate_skill, get_assessment, top_skills

__all__ = [
    "get_courses",
    "get_course_detail",
    "get_total_credits",
    "get_curriculum_overview",
    "get_assessment",
    "calculate_skill",
    "top_skills",
]
