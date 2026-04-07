"""
Global Readiness Compliance Agent.
Reviews creative assets for localization readiness, cultural sensitivity, and regional compliance.
Checks: cultural symbols, dates/numbers/currency formats, text expansion space, regional restrictions.
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

GLOBAL_READINESS_SYSTEM_PROMPT = """You are a Microsoft Global Readiness Compliance Reviewer.
Your role is to evaluate creative assets for international readiness and cultural appropriateness.

You review for:
- Cultural sensitivity (symbols, colors, gestures with different meanings globally)
- Text expansion space (translated text can be 30-50% longer than English)
- Date, time, number, and currency format flexibility
- Region-specific legal restrictions (content banned in certain markets)
- Right-to-left language layout support
- Local imagery appropriateness
- Metric vs imperial units
- Local trademark and IP considerations

Respond in JSON format with the same structure as other agents."""


class GlobalReadinessAgent(BaseComplianceAgent):
      """Global Readiness compliance domain agent."""

    @property
    def domain(self) -> ComplianceDomain:
              return ComplianceDomain.GLOBAL_READINESS

    @property
    def system_prompt(self) -> str:
              return GLOBAL_READINESS_SYSTEM_PROMPT

    def build_review_prompt(
              self,
              asset_content: str,
              retrieved_context: str,
              asset_metadata: dict[str, Any],
    ) -> str:
              filename = asset_metadata.get("filename", "unknown")
              target_markets = asset_metadata.get("target_markets", "Global")
              return f"""Review this creative asset for Microsoft Global Readiness compliance.

      ASSET: {filename} | TARGET MARKETS: {target_markets}
      METADATA: {json.dumps(asset_metadata, indent=2)}

      CONTENT:
      {asset_content[:3000]}

      GLOBAL READINESS GUIDANCE (cite ONLY these sources):
      {retrieved_context}

      Identify any content that could be culturally insensitive or problematic in target markets.
      Flag hardcoded locale-specific formats as MEDIUM severity."""

    def parse_llm_response(self, response_text: str, asset_id: str) -> DomainReviewResult:
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
                                                    severity=Severity(f.get("severity", "low")),
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
                              overall_severity=Severity(data.get("overall_severity", "low")),
                              findings=findings,
                              summary=data.get("summary", "Global readiness review completed."),
                              agent_model=self.settings.llm_model,
            )
except (json.JSONDecodeError, KeyError, ValueError) as exc:
            self.logger.warning("global_readiness_agent_parse_error", error=str(exc))
            return DomainReviewResult(
                              domain=self.domain,
                              asset_id=asset_id,
                              passed=False,
                              overall_severity=Severity.MEDIUM,
                              findings=[],
                              summary=f"Global readiness review parse failed: {str(exc)}",
                              requires_human_review=True,
                              escalation_reason="Global readiness agent parse error",
                              agent_model=self.settings.llm_model,
            )
