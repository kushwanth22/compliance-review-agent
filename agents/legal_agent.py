"""
Legal / CELA Compliance Agent.
Reviews creative assets against Microsoft Legal and Corporate External & Legal Affairs (CELA) guidelines.
Checks: disclaimers, claims, IP, regulatory compliance, privacy statements.
NOTE: Legal failures always trigger human escalation (see escalation_rules.py).
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

LEGAL_SYSTEM_PROMPT = """You are a Microsoft Legal/CELA Compliance Reviewer.
Your role is to evaluate creative assets against Microsoft Legal and CELA guidelines.

You review for:
- Required legal disclaimers and disclosures
- Accuracy of product/feature claims
- Intellectual property compliance (trademarks, copyrights)
- Privacy and data protection statements
- Regulatory compliance by region
- Comparative advertising rules
- Promotional offer terms and conditions

You ONLY make judgments grounded in the provided compliance guidance.
You do NOT use general legal knowledge - cite specific rules from the provided context.
All legal failures MUST be flagged as high or critical severity.

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
                                          "rationale": "why pass/fail with specific citation",
                                                "suggested_fix": "exact text change required (if failed)"
    }
      ]
      }"""


class LegalAgent(BaseComplianceAgent):
      """Legal/CELA compliance domain agent."""

    @property
    def domain(self) -> ComplianceDomain:
              return ComplianceDomain.LEGAL

    @property
    def system_prompt(self) -> str:
              return LEGAL_SYSTEM_PROMPT

    def build_review_prompt(
              self,
              asset_content: str,
              retrieved_context: str,
              asset_metadata: dict[str, Any],
    ) -> str:
              filename = asset_metadata.get("filename", "unknown")
              target_markets = asset_metadata.get("target_markets", "Global")
              return f"""Review the following creative asset for Microsoft Legal/CELA compliance.

      ASSET INFORMATION:
      - Filename: {filename}
      - Target Markets: {target_markets}
      - Metadata: {json.dumps(asset_metadata, indent=2)}

      ASSET CONTENT:
      {asset_content[:3000]}

      APPROVED LEGAL GUIDANCE (use ONLY these sources for citations):
      {retrieved_context}

      Evaluate ALL claims, disclaimers, and legal statements in this asset.
      Flag any missing required disclaimers as HIGH severity.
      Flag any inaccurate claims as CRITICAL severity.
      Every finding must cite its source from the guidance provided."""

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
                                                    severity=Severity(f.get("severity", "high")),
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
                              overall_severity=Severity(data.get("overall_severity", "high")),
                              findings=findings,
                              summary=data.get("summary", "Legal review completed."),
                              agent_model=self.settings.llm_model,
            )

except (json.JSONDecodeError, KeyError, ValueError) as exc:
            self.logger.warning("legal_agent_parse_error", error=str(exc))
            return DomainReviewResult(
                              domain=self.domain,
                              asset_id=asset_id,
                              passed=False,
                              overall_severity=Severity.HIGH,
                              findings=[],
                              summary=f"Legal review parse failed: {str(exc)}",
                              requires_human_review=True,
                              escalation_reason="Legal agent parse error - mandatory human review",
                              agent_model=self.settings.llm_model,
            )
