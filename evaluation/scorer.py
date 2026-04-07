"""
Compliance scoring logic.
Computes overall severity from domain review results.
"""
from __future__ import annotations
from models.review_result import DomainReviewResult, Severity

# Severity ordering from lowest to highest risk
SEVERITY_RANK: dict[Severity, int] = {
      Severity.PASS: 0,
      Severity.LOW: 1,
      Severity.MEDIUM: 2,
      Severity.HIGH: 3,
      Severity.CRITICAL: 4,
}


class ComplianceScorer:
      """
          Computes the overall compliance severity across all domain results.
              Uses the highest severity finding across all domains (worst-case wins).
                  """

    def compute_overall_severity(
              self,
              domain_results: list[DomainReviewResult],
    ) -> Severity:
              """
                      Return the highest severity across all domain results.
                              If all domains pass, return PASS. Otherwise return worst severity.
                                      """
              if not domain_results:
                            return Severity.PASS

              max_severity = Severity.PASS

        for result in domain_results:
                      if SEVERITY_RANK[result.overall_severity] > SEVERITY_RANK[max_severity]:
                                        max_severity = result.overall_severity

                  return max_severity

    def compute_pass_rate(
              self,
              domain_results: list[DomainReviewResult],
    ) -> float:
              """Compute the percentage of domains that passed."""
              if not domain_results:
                            return 0.0
                        passed = sum(1 for r in domain_results if r.passed)
        return round(passed / len(domain_results), 2)

    def severity_to_score(self, severity: Severity) -> int:
              """Convert severity to a numeric score (0=pass, 4=critical)."""
        return SEVERITY_RANK.get(severity, 0)
