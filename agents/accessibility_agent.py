"""
Accessibility Compliance Agent.
Reviews creative assets against WCAG 2.1 AA and Microsoft Accessibility Standards.
Checks: alt text, color contrast, captions, keyboard navigation, screen reader compatibility.
NOTE: High-severity accessibility failures trigger human escalation (legal risk).
"""
from __future__ import annotations
import json
from typing import Any
from agents.base_agent import BaseComplianceAgent
from models.review_result import (
    ComplianceDomain,
    DomainReviewResult,
    ComplianceFinding,
    Severity,
)

ACCESSIBILITY_SYSTEM_PROMPT = """You are a Microsoft Accessibility Compliance Reviewer.
Your role is to evaluate creative assets against WCAG 2.1 AA and Microsoft Accessibility Standards.

You review for:
- Alt text for images (descriptive and meaningful)
- Color contrast ratios (minimum 4.5:1 for normal text, 3:1 for large text)
- Video captions and audio descriptions
- Readable font sizes (minimum 12px / 9pt)
- Keyboard navigation compatibility indicators
- Screen reader compatibility signals
- Accessible color combinations (not relying on color alone)
- Flashing content (max 3 flashes per second)

You ONLY make judgments grounded in the provided compliance guidance.
Respond in JSON format with the same structure as other agents."""


class AccessibilityAgent(BaseComplianceAgent):
      """Accessibility compliance domain agent (WCAG 2.1 AA + Microsoft standards)."""

    @property
    def domain(self) -> ComplianceDomain:
              return ComplianceDomain.ACCESSIBILITY

    @property
    def system_prompt(self) -> str:
              return ACCESSIBILITY_SYSTEM_PROMPT

    def build_review_prompt(
              self,
              asset_content: str,
              retrieved_context: str,
              asset_metadata: dict[str, Any],
    ) -> str:
              filename = asset_metadata.get("filename", "unknown")
              file_type = asset_metadata.get("file_type", "unknown")
              return f"""Review this creative asset for Microsoft Accessibility compliance (WCAG 2.1 AA).

      ASSET: {filename} ({file_type})
      METADATA: {json.dumps(asset_metadata, indent=2)}

      CONTENT:
      {asset_content[:3000]}

      ACCESSIBILITY GUIDANCE (cite ONLY these sources):
      {retrieved_context}

      Check all accessibility criteria. Flag missing alt text as HIGH severity.
      Flag contrast failures as MEDIUM-HIGH severity. Flag flashing content as CRITICAL."""

    def parse_llm_response(
              self,
              response_text: str,
              asset_id: str,
    ) -> DomainReviewResult:
              try:
                            text = response_text.strip()
                            if "```json" in text:
                                              text = text.split("```json")[1].split("```")[0].strip()
elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            data = json.loads(text)
            findings = [
                              ComplianceFinding(
                                                    rule=f.get("rule", "unknown"),
                                                    description=f.get("description", ""),
                                                    severity=Severity(f.get("severity", "medium")),
                                                    passed=f.get("passed", False),
                                                    rationale=f.get("rationale", ""),
                                                    suggested_fix=f.get("suggested_fix"),
                              )
                              for f in data.get("findings", [])
            ]

            return DomainReviewResult(
                              domain=self.domain,
                              asset_id=asset_id,
                              passed=data.get("passed", False),
                              overall_severity=Severity(data.get("overall_severity", "medium")),
                              findings=findings,
                              summary=data.get("summary", "Accessibility review completed."),
                              agent_model=self.settings.llm_model,
            )
except (json.JSONDecodeError, KeyError, ValueError) as exc:
            self.logger.warning("accessibility_agent_parse_error", error=str(exc))
            return DomainReviewResult(
                              domain=self.domain,
                              asset_id=asset_id,
                              passed=False,
                              overall_severity=Severity.MEDIUM,
                              findings=[],
                              summary=f"Accessibility review parse failed: {str(exc)}",
                              requires_human_review=True,
                              escalation_reason="Accessibility agent parse error - manual review required",
                              agent_model=self.settings.llm_model,
            )
