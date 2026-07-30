"""Opportunity Core models — Jobs-first; other types schema-ready."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class OpportunityType(str, Enum):
    JOB = "JOB"
    CLIENT = "CLIENT"
    PRODUCT = "PRODUCT"
    NETWORK = "NETWORK"
    OTHER = "OTHER"


class OpportunityStatus(str, Enum):
    NEW = "new"
    REVIEW = "review"
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    HIRED = "hired"
    ARCHIVED = "archived"
    SKIPPED = "skipped"


class FeedbackAction(str, Enum):
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"
    SAVE = "SAVE"
    APPLY = "APPLY"
    SKIP = "SKIP"
    NOT_RELEVANT = "NOT_RELEVANT"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    HIRED = "HIRED"


class NextAction(str, Enum):
    APPLY = "APPLY"
    REVIEW = "REVIEW"
    WRITE_TO_CONTACT = "WRITE_TO_CONTACT"
    FOLLOW_UP = "FOLLOW_UP"
    RESEARCH_COMPANY = "RESEARCH_COMPANY"
    PREPARE_INTERVIEW = "PREPARE_INTERVIEW"
    EVALUATE_OFFER = "EVALUATE_OFFER"
    WAIT = "WAIT"
    ARCHIVE = "ARCHIVE"
    CONSIDER_SWITCH = "CONSIDER_SWITCH"


class ActionPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


SCORE_KEYS = (
    "fit",
    "income",
    "growth",
    "probability",
    "strategic",
    "urgency",
)


@dataclass
class ScoreComponent:
    score: int
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"score": int(self.score), "reasons": list(self.reasons)}


@dataclass
class ScoreBundle:
    fit: ScoreComponent
    income: ScoreComponent
    growth: ScoreComponent
    probability: ScoreComponent
    strategic: ScoreComponent
    urgency: ScoreComponent
    overall: int
    weights: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "fit": self.fit.to_dict(),
            "income": self.income.to_dict(),
            "growth": self.growth.to_dict(),
            "probability": self.probability.to_dict(),
            "strategic": self.strategic.to_dict(),
            "urgency": self.urgency.to_dict(),
            "overall_score": int(self.overall),
            "weights": dict(self.weights),
        }


@dataclass
class Opportunity:
    id: int | None
    type: OpportunityType
    title: str
    company_or_entity: str
    source: str
    source_url: str
    status: OpportunityStatus
    created_at: str
    updated_at: str
    raw_payload: dict[str, Any] = field(default_factory=dict)
    normalized_payload: dict[str, Any] = field(default_factory=dict)
    scores: dict[str, Any] = field(default_factory=dict)
    analysis: dict[str, Any] = field(default_factory=dict)
    next_action: str = NextAction.REVIEW.value
    next_action_priority: str = ActionPriority.MEDIUM.value
    feedback: list[dict[str, Any]] = field(default_factory=list)
    job_lead_id: int | None = None
    overall_score: int = 0

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["type"] = self.type.value if isinstance(self.type, OpportunityType) else self.type
        d["status"] = (
            self.status.value if isinstance(self.status, OpportunityStatus) else self.status
        )
        return d


# Map legacy job_hunt feedback / status → Opportunity
LEGACY_FEEDBACK_TO_OPP = {
    "like": FeedbackAction.LIKE,
    "dislike": FeedbackAction.DISLIKE,
    "applied": FeedbackAction.APPLY,
    "interview": FeedbackAction.INTERVIEW,
}

LEGACY_STATUS_TO_OPP = {
    "new": OpportunityStatus.NEW,
    "liked": OpportunityStatus.SAVED,
    "rejected": OpportunityStatus.REJECTED,
    "applied": OpportunityStatus.APPLIED,
    "interview": OpportunityStatus.INTERVIEW,
}

FEEDBACK_TO_STATUS = {
    FeedbackAction.LIKE: OpportunityStatus.SAVED,
    FeedbackAction.SAVE: OpportunityStatus.SAVED,
    FeedbackAction.DISLIKE: OpportunityStatus.SKIPPED,
    FeedbackAction.SKIP: OpportunityStatus.SKIPPED,
    FeedbackAction.NOT_RELEVANT: OpportunityStatus.ARCHIVED,
    FeedbackAction.APPLY: OpportunityStatus.APPLIED,
    FeedbackAction.INTERVIEW: OpportunityStatus.INTERVIEW,
    FeedbackAction.OFFER: OpportunityStatus.OFFER,
    FeedbackAction.REJECTED: OpportunityStatus.REJECTED,
    FeedbackAction.HIRED: OpportunityStatus.HIRED,
}

# Reasons that must NOT punish source relevance (actionability / paywall)
NON_SOURCE_PUNISH_REASONS = frozenset(
    {
        "paywall",
        "hirify_plus",
        "no_contacts",
        "subscription",
        "подписк",
        "контакт",
        "not_actionable",
        "невозможно откликнуться",
        "duplicate",
        "дубл",
        "cross-channel",
    }
)
