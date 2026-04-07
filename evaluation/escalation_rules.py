"""
Escalation rules - determines when human review is required.
Clear escalation triggers preserve trust in AI automation.
"""
from __future__ import annotations
from models.review_result import DomainReviewResult, Severity

# Severity levels that trigger human review by threshold
SEVERITY_RANK: dict[Severity, int] = {
      Severity.PASS: 0,
      Severity.LOW: 1,
      Severity.MEDIUM: 2,
      Severity.HIGH: 3,
      Severity.CRITICAL: 4,
}

ESCALATION_THRESHOLD_RANK: dict[str, int] = {
      "low": 1,
      "medium": 2,
      "high": 3,
}


class EscalationEvaluator:
      """
          Evaluates domain review results and determines escalation triggers.
              Responsible AI: preserves human oversight for high-risk decisions.
                  """

    def evaluate(
              self,
              domain_results: list[DomainReviewResult],
              threshold: str = "high",
    ) -> list[str]:
              """
                      Evaluate all domain results and return list of escalation trigger reasons.
                              Mutates each DomainReviewResult's requires_human_review flag.
                                      """
              threshold_rank = ESCALATION_THRESHOLD_RANK.get(threshold, 3)
              triggers = []

        for result in domain_results:
                      domain_triggers = self._evaluate_domain(result, threshold_rank)
                      if domain_triggers:
                                        result.requires_human_review = True
                                        result.escalation_reason = "; ".join(domain_triggers)
                                        triggers.extend(domain_triggers)

                  return triggers

    def _evaluate_domain(
              self,
              result: DomainReviewResult,
              threshold_rank: int,
    ) -> list[str]:
              """Check a single domain result for escalation triggers."""
              triggers = []

        # Rule 1: Severity meets or exceeds threshold
              if SEVERITY_RANK.get(result.overall_severity, 0) >= threshold_rank:
                            triggers.append(
                                              f"{result.domain.value}: severity {result.overall_severity.value} "
                                              f"meets escalation threshold"
                            )

              # Rule 2: Any CRITICAL finding regardless of threshold
              critical_findings = [
                  f for f in result.findings
                  if f.severity == Severity.CRITICAL
              ]
              if critical_findings:
                            triggers.append(
                                              f"{result.domain.value}: {len(critical_findings)} CRITICAL finding(s) - "
                                              f"always escalated"
                            )

              # Rule 3: Legal/CELA domain failures always require human review
              if result.domain.value == "legal" and not result.passed:
                            triggers.append(
                                              f"{result.domain.value}: legal/CELA failures require human review by policy"
                            )

              # Rule 4: Accessibility failures with HIGH+ severity
              if result.domain.value == "accessibility" and SEVERITY_RANK.get(result.overall_severity, 0) >= 3:
                            triggers.append(
                                              f"{result.domain.value}: high-severity accessibility failure - legal risk"
                            )

              # Rule 5: Agent errors always escalate
              error_findings = [f for f in result.findings if f.rule == "agent_error"]
              if error_findings:
                            triggers.append(
                                              f"{result.domain.value}: review agent error - manual review required"
                            )

              return triggers
