# LOCKED: change only via a contract/* PR approved by P1 + P3.
# Keep in sync with frontend/src/types/contract.ts
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field

UserType = Literal["prospective", "current_student", "near_graduate"]
AgeRange = Literal["under_18", "18_20", "21_23", "24_plus"]
SkillKey = Literal["frontend", "backend", "network", "embedded", "ai_data", "cybersecurity"]
Intent = Literal["department_info", "curriculum", "course_detail", "skill_analysis", "general", "clarify"]
FeedbackReason = Literal["incorrect", "off_topic", "hard_to_read", "incomplete", "other"]
SKILL_KEYS: list[str] = ["frontend", "backend", "network", "embedded", "ai_data", "cybersecurity"]


# ---------- User ----------
class User(BaseModel):
    id: str
    email: str
    name: str
    picture_url: Optional[str] = None
    display_name: Optional[str] = None
    age_range: Optional[AgeRange] = None
    user_type: Optional[UserType] = None
    study_year: Optional[int] = Field(default=None, ge=1, le=4)
    onboarded: bool = False


class AuthResponse(BaseModel):
    access_token: str
    user: User
    is_new_user: bool


class ProfileUpdate(BaseModel):
    display_name: str = Field(min_length=1, max_length=50)
    age_range: AgeRange
    user_type: UserType
    study_year: Optional[int] = Field(default=None, ge=1, le=4)


# ---------- Skill ----------
class SkillScores(BaseModel):
    frontend: int = Field(ge=0, le=100)
    backend: int = Field(ge=0, le=100)
    network: int = Field(ge=0, le=100)
    embedded: int = Field(ge=0, le=100)
    ai_data: int = Field(ge=0, le=100)
    cybersecurity: int = Field(ge=0, le=100)


class SkillDimension(BaseModel):
    key: str
    label: str
    short_label: Optional[str] = None
    score: int = Field(ge=0, le=100)
    description: Optional[str] = None


class SkillProfile(BaseModel):
    scores: SkillScores
    top_skills: list[SkillKey]
    taken_at: str
    topic: Optional[str] = None
    score: Optional[int] = None
    title: Optional[str] = None
    dimensions: Optional[list[SkillDimension]] = None
    custom_top_skills: Optional[list[str]] = None


# ---------- Curriculum ----------
class Course(BaseModel):
    code: str
    name_th: str
    name_en: str
    credits: int
    credit_detail: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    year: int
    semester: int


class CourseTableData(BaseModel):
    year: int
    semester: int
    courses: list[Course]
    total_credits: int


class InfoCard(BaseModel):
    title: str
    body: str
    icon: Optional[str] = None
    tags: list[str] = []


class CardsData(BaseModel):
    cards: list[InfoCard]


class AssessmentOption(BaseModel):
    value: int = Field(ge=0, le=4)
    label: str


class AssessmentQuestion(BaseModel):
    id: str
    text: str
    options: list[AssessmentOption]


class AssessmentFormData(BaseModel):
    assessment_id: str
    title: str
    questions: list[AssessmentQuestion]


class SkillRadarData(BaseModel):
    scores: SkillScores
    top_skills: list[SkillKey]
    summary: str
    taken_at: str
    topic: Optional[str] = None
    title: Optional[str] = None
    dimensions: Optional[list[SkillDimension]] = None
    custom_top_skills: Optional[list[str]] = None


class ErrorData(BaseModel):
    code: Literal["llm_unavailable", "tool_failed", "unknown"]


# ---------- Agent response ----------
class Source(BaseModel):
    doc_id: str
    title: str
    section: Optional[str] = None
    url: Optional[str] = None
    snippet: str
    score: float


class ActionPayload(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None


class Action(BaseModel):
    type: Literal["ask", "open_url"]
    label: str
    payload: ActionPayload


# Persona/theme chosen in the chat UI. Changes the tone of the answer only, never facts, scores or sources.
InteractionMode = Literal["normal", "devil", "developer"]


class ResponseMeta(BaseModel):
    intent: Intent
    tool: Optional[str] = None
    latency_ms: int = 0
    interaction_mode: InteractionMode = "normal"  # history saved before this field reads as "normal"


ResponseType = Literal["text", "course_table", "cards", "assessment_form", "skill_radar", "error"]


class AgentResponse(BaseModel):
    conversation_id: str
    message_id: str
    message: str
    response_type: ResponseType
    data: Union[CourseTableData, CardsData, AssessmentFormData, SkillRadarData, ErrorData, None] = None
    sources: list[Source] = []
    actions: list[Action] = []
    meta: ResponseMeta


# ---------- Requests ----------
class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str = Field(min_length=1, max_length=1000)
    interaction_mode: InteractionMode = "normal"


class AssessmentAnswer(BaseModel):
    question_id: str
    value: int = Field(ge=0, le=4)


class AssessmentSubmit(BaseModel):
    conversation_id: str
    assessment_id: str
    answers: list[AssessmentAnswer]
    interaction_mode: InteractionMode = "normal"


class FeedbackRequest(BaseModel):
    message_id: str
    rating: Literal["up", "down"]
    reason: Optional[FeedbackReason] = None
    comment: Optional[str] = Field(default=None, max_length=500)


# ---------- History ----------
class ConversationSummary(BaseModel):
    id: str
    title: str
    updated_at: str
    project_id: Optional[str] = None  # None = not in a project


class ConversationUpdate(BaseModel):
    """PATCH body: send only the fields to change. `project_id: null` removes the chat from its project."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=80)
    project_id: Optional[str] = None


class Project(BaseModel):
    """A user's folder that groups related conversations."""

    id: str
    name: str
    created_at: str
    updated_at: str
    conversation_count: int = 0


class ProjectInput(BaseModel):
    name: str = Field(min_length=1, max_length=60)


class ChatMessage(BaseModel):
    id: str
    role: Literal["user", "assistant"]
    content: Optional[str] = None           # role == "user"
    response: Optional[AgentResponse] = None  # role == "assistant"
    feedback: Optional[Literal["up", "down"]] = None
    created_at: str


class ConversationDetail(BaseModel):
    id: str
    title: str
    messages: list[ChatMessage]


# ---------- Internal tool contract (P3 <-> P4) ----------
class RetrievedChunk(BaseModel):
    text: str
    source: Source
