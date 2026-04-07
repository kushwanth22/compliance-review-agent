"""
Pydantic models for compliance review results.
All outputs are typed, validated, and serializable for audit trails.
"""
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field
import uuid


class ComplianceDomain(str, Enum):
    BRAND = "brand"
    LEGAL = "legal"
    ACCESSIBILITY = "accessibility"
    GLOBAL_READINESS = "global_readiness"
    PRODUCT_MARKETING = "product_marketing"


class Severity(str, Enum):
    PASS = "pass"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CitationSource(BaseModel):
    """Grounded citation - every finding must trace back to an approved source."""
    document_name: str
    section: str | None = None
    chunk_id: str | None = None
    relevance_score: float = Field(ge=0.0, le=1.0)
    excerpt: str | None = Field(None, max_length=500)


class ComplianceFinding(BaseModel):
    """A single compliance finding within a domain review."""
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule: str
    description: str
    severity: Severity
    passed: bool
    rationale: str
    citations: list[CitationSource] = Field(default_factory=list)
    suggested_fix: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class DomainReviewResult(BaseModel):
    """Result from a single domain compliance agent."""
    domain: ComplianceDomain
    asset_id: str
    passed: bool
    overall_severity: Severity
    findings: list[ComplianceFinding] = Field(default_factory=list)
    summary: str
    requires_human_review: bool = False
    escalation_reason: str | None = None
    agent_model: str
    review_duration_ms: int | None = None
    reviewed_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def critical_findings(self) -> list[ComplianceFinding]:
        return [f for f in self.findings if f.severity in (Severity.CRITICAL, Severity.HIGH)]

                    @property
                    def finding_count(self) -> int:
                        return len(self.findings)


                class ComplianceReport(BaseModel):
                    """Aggregated compliance report across all domains - final output."""
                    report_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
                    asset_id: str
                    asset_filename: str
                    overall_passed: bool
                    overall_severity: Severity
                    domain_results: list[DomainReviewResult] = Field(default_factory=list)
                    requires_human_review: bool = False
                    escalation_triggers: list[str] = Field(default_factory=list)
                    executive_summary: str = ""
                    total_findings: int = 0
                    domains_passed: int = 0
                    domains_failed: int = 0
                    reviewed_at: datetime = Field(default_factory=datetime.utcnow)
                    review_duration_ms: int | None = None

                    def model_post_init(self, __context: Any) -> None:
                        self.total_findings = sum(r.finding_count for r in self.domain_results)
                                                          self.domains_passed = sum(1 for r in self.domain_results if r.passed)
                                                                    self.domains_failed = sum(1 for r in self.domain_results if not r.passed)
                                                                              self.requires_human_review = any(r.requires_human_review for r in self.domain_results)
                                                                                                                       self.escalation_triggers = [
                                                                                                                                     r.escalation_reason for r in self.domain_results
                                                                                                                                     if r.escalation_reason is not None
                                                                                                                                 ]
