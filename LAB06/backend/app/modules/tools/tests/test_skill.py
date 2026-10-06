"""Checks for the twelve-question skill assessment and scoring formula."""

import pytest
from pydantic import ValidationError

from app.modules.tools import calculate_skill, get_assessment, top_skills
from app.schemas.contract import AssessmentAnswer, AssessmentFormData, SKILL_KEYS, SkillScores


def _answers(value: int) -> list[AssessmentAnswer]:
    return [AssessmentAnswer(question_id=f"q{number}", value=value) for number in range(1, 13)]


def test_form_matches_contract_without_exposing_weights() -> None:
    form = get_assessment()
    assert isinstance(form, AssessmentFormData)
    assert form.assessment_id == "skill_v1"
    assert len(form.questions) == 12
    assert [option.value for option in form.questions[0].options] == list(range(5))
    assert all("weights" not in question.model_dump() for question in form.questions)


def test_zero_and_full_answers_bound_every_skill() -> None:
    assert calculate_skill(_answers(0)).model_dump() == dict.fromkeys(SKILL_KEYS, 0)
    assert calculate_skill(_answers(4)).model_dump() == dict.fromkeys(SKILL_KEYS, 100)


def test_mixed_and_missing_answers_match_hand_calculation() -> None:
    answers = [
        AssessmentAnswer(question_id="q1", value=1),
        AssessmentAnswer(question_id="q2", value=3),
        AssessmentAnswer(question_id="q3", value=4),
        AssessmentAnswer(question_id="q4", value=2),
    ]
    scores = calculate_skill(answers)
    assert isinstance(scores, SkillScores)
    assert scores.frontend == round((1 + 3) / 8 * 100) == 50
    assert scores.backend == round((4 + 2) / 8 * 100) == 75
    assert all(getattr(scores, skill) == 0 for skill in SKILL_KEYS[2:])
    assert calculate_skill(answers) == scores


def test_top_skills_break_ties_by_contract_order() -> None:
    assert top_skills(calculate_skill(_answers(4))) == SKILL_KEYS[:2]
    assert top_skills(calculate_skill(_answers(0)), n=3) == SKILL_KEYS[:3]


def test_invalid_answers_do_not_produce_scores() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        calculate_skill([AssessmentAnswer(question_id="q1", value=1)] * 2)
    with pytest.raises(ValueError, match="Unknown"):
        calculate_skill([AssessmentAnswer(question_id="q13", value=1)])
    with pytest.raises(ValidationError):
        AssessmentAnswer(question_id="q1", value=5)
