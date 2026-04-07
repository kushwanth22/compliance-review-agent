"""
Brand Compliance Agent.
Reviews creative assets against Microsoft Brand Guidelines.
Checks: logo usage, color palette, typography, visual identity, tone of voice.
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

BRAND_SYSTEM_PROMPT = """You are a Microsoft Brand Compliance Reviewer.
Your role is to evaluate creative assets against Microsoft Brand Guidelines.

You review for:
- Microsoft logo usage (placement, size, clearspace, color)
- Brand color palette compliance (Microsoft Blue #0078D4, etc.)
- Typography standards (Segoe UI font family)
- Visual identity consistency
- Tone of voice alignment
- Co-branding rules

You ONLY make judgments grounded in the provided compliance guidance.
You do NOT use general knowledge - cite specific rules from the provided context.

Respond in JSON format:
{
  "passed": true/false,
    "overall_severity": "pass|low|medium|high|critical",
      "summary": "brief summary",
        "findings": [
            {
                  "rule": "rule name",
                        "description": "what was checked",
                              "severity": "pass|low|medium|high|critical",
                                    "passed": true/false,
                                          "rationale": "why pass/fail with citation",
                                                "suggested_fix": "how to fix (if failed)"
    }
      ]
      }"""


class BrandAgent(BaseComplianceAgent):
      """Brand compliance domain agent."""

    @property
    def domain(self) -> ComplianceDomain:
              return ComplianceDomain.BRAND

    @property
    def system_prompt(self) -> str:
              return BRAND_SYSTEM_PROMPT

    def build_review_prompt(
              self,
              asset_content: str,
              retrieved_context: str,
              asset_metadata: dict[str, Any],
    ) -> str:
              filename = asset_metadata.get("filename", "unknown")
              file_type = asset_metadata.get("file_type", "unknown")
              return f"""Review the following creative asset for Microsoft Brand compliance.

      ASSET INFORMATION:
      - Filename: {filename}
      - File Type: {file_type}
      - Metadata: {json.dumps(asset_metadata, indent=2)}

      ASSET CONTENT:
      {asset_content[:3000]}

      APPROVED BRAND GUIDANCE (use ONLY these sources for citations):
      {retrieved_context}

      Evaluate this asset against the brand guidance above.
      Be specific about which rules pass or fail.
      Every finding must cite its source from the guidance provided."""

    def parse_llm_response(
              self,
              response_text: str,
              asset_id: str,
    ) -> DomainReviewResult:
              """Parse JSON response from LLM into DomainReviewResult."""
              try:
                            # Extract JSON from response (handle markdown code blocks)
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
                              overall_severity=Severity(data.get("overall_severity", "medium")),
                              findings=findings,
                              summary=data.get("summary", "Brand review completed."),
                              agent_model=self.settings.llm_model,
            )

except (json.JSONDecodeError, KeyError, ValueError) as exc:
            self.logger.warning(
                              "brand_agent_parse_error",
                              error=str(exc),
                              response_preview=response_text[:200],
            )
            # Fallback: return a failed result requiring human review
            return DomainReviewResult(
                              domain=self.domain,
                              asset_id=asset_id,
                              passed=False,
                              overall_severity=Severity.MEDIUM,
                              findings=[],
                              summary=f"Brand review completed but response parsing failed: {str(exc)}",
                              requires_human_review=True,
                              escalation_reason="LLM response could not be parsed - manual review needed",
                              agent_model=self.settings.llm_model,
            )
