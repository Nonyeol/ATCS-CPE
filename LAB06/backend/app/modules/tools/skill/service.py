"""Deterministic skill assessment and scoring functions."""

from app.schemas.contract import (
    AssessmentAnswer,
    AssessmentFormData,
    AssessmentOption,
    AssessmentQuestion,
    SKILL_KEYS,
    SkillScores,
)

from .loader import load_assessment



def get_assessment() -> AssessmentFormData:
    data = load_assessment()
    options = [AssessmentOption.model_validate(row) for row in data["scale"]]
    return AssessmentFormData(
        assessment_id=data["assessment_id"],
        title=data["title"],
        questions=[
            AssessmentQuestion(id=row["id"], text=row["text"], options=options)
            for row in data["questions"]
        ],
    )


def calculate_skill(answers: list[AssessmentAnswer]) -> SkillScores:
    questions = load_assessment()["questions"]
    valid_ids = {question["id"] for question in questions}
    values = {}
    for answer in answers:
        if answer.question_id not in valid_ids or answer.question_id in values:
            raise ValueError(f"Unknown or duplicate question ID: {answer.question_id}")
        values[answer.question_id] = answer.value

    scores = {}
    for skill in SKILL_KEYS:
        weights = [(values.get(question["id"], 0), question["weights"].get(skill, 0)) for question in questions]
        denominator = sum(4 * weight for _, weight in weights)
        scores[skill] = round(sum(value * weight for value, weight in weights) / denominator * 100)
    return SkillScores(**scores)


def top_skills(scores: SkillScores, n: int = 2) -> list[str]:
    values = scores.model_dump()
    return sorted(SKILL_KEYS, key=lambda skill: (-values[skill], SKILL_KEYS.index(skill)))[:max(n, 0)]
