"""Structured bounty finding models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class BountyFinding:
    title: str
    severity: str
    weakness_type: str
    asset: str
    report_markdown: str
    reproduction_steps: str
    impact: str
    program_name: str
    platform: str
    team_handle: str
    program_url: str
    confidence: str = "high"
    quality_score: int | None = None
    evidence_commands: list[str] | None = None

    def to_meta(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_meta(cls, meta: dict[str, Any]) -> BountyFinding | None:
        required = (
            "title",
            "severity",
            "weakness_type",
            "asset",
            "report_markdown",
            "reproduction_steps",
            "impact",
            "program_name",
            "platform",
            "team_handle",
            "program_url",
        )
        if not all(meta.get(k) for k in required):
            return None
        return cls(
            title=str(meta["title"]),
            severity=str(meta["severity"]).lower(),
            weakness_type=str(meta["weakness_type"]),
            asset=str(meta["asset"]),
            report_markdown=str(meta["report_markdown"]),
            reproduction_steps=str(meta["reproduction_steps"]),
            impact=str(meta["impact"]),
            program_name=str(meta["program_name"]),
            platform=str(meta["platform"]),
            team_handle=str(meta["team_handle"]),
            program_url=str(meta["program_url"]),
            confidence=str(meta.get("confidence", "high")).lower(),
        )


@dataclass
class BountyScanResult:
    draft_ids: list[int] = field(default_factory=list)
    researched_program: str = ""
    programs_tried: list[str] = field(default_factory=list)
    finding_found: bool = False
    skipped_reason: str = ""
    message: str = ""
    purged_ids: list[int] = field(default_factory=list)
    research_log: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
