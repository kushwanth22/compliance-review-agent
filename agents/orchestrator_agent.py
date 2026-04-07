"""
Orchestrator Agent - coordinates all domain compliance agents.
Uses asyncio.gather() to run all domain agents in parallel (async).
Aggregates results into a single ComplianceReport.
"""
from __future__ import annotations
import asyncio
import time
from typing import Any
from config.settings import get_settings
from config.logging_config import get_logger
from models.review_result import (
    ComplianceReport,
    DomainReviewResult,
    Severity,
    ComplianceDomain,
)
from agents.brand_agent import BrandAgent
from agents.legal_agent import LegalAgent
from agents.accessibility_agent import AccessibilityAgent
from agents.global_readiness_agent import GlobalReadinessAgent
from agents.product_marketing_agent import ProductMarketingAgent
from rag.retriever import ComplianceRetriever
from evaluation.escalation_rules import EscalationEvaluator
from evaluation.scorer import ComplianceScorer

logger = get_logger(__name__)

# Severity priority for aggregation (highest wins)
SEVERITY_ORDER = [
      Severity.PASS,
      Severity.LOW,
      Severity.MEDIUM,
      Severity.HIGH,
      Severity.CRITICAL,
]


class OrchestratorAgent:
      """
          Central orchestrator for the Compliance Review Agent.

              Workflow:
                  1. Retrieve compliance guidance for the asset from vector store (RAG)
                      2. Fan out to all domain agents in parallel (asyncio.gather)
                          3. Collect DomainReviewResult from each agent
                              4. Evaluate escalation triggers
                                  5. Aggregate into ComplianceReport
                                      """

    def __init__(self) -> None:
              self.settings = get_settings()
              self.retriever = ComplianceRetriever()
              self.scorer = ComplianceScorer()
              self.escalation_evaluator = EscalationEvaluator()

        # Initialize all domain agents
              self._all_agents = {
                  ComplianceDomain.BRAND: BrandAgent(),
                  ComplianceDomain.LEGAL: LegalAgent(),
                  ComplianceDomain.ACCESSIBILITY: AccessibilityAgent(),
                  ComplianceDomain.GLOBAL_READINESS: GlobalReadinessAgent(),
                  ComplianceDomain.PRODUCT_MARKETING: ProductMarketingAgent(),
              }

    def _get_active_agents(self) -> dict[ComplianceDomain, Any]:
              """Return only agents for configured domains."""
              active_domains = self.settings.review_domain_list
              return {
                  domain: agent
                  for domain, agent in self._all_agents.items()
                  if domain.value in active_domains
              }

    async def run_review(
              self,
              asset_id: str,
              asset_filename: str,
              asset_content: str,
              asset_metadata: dict[str, Any] | None = None,
    ) -> ComplianceReport:
              """
                      Run full multi-domain compliance review.

                              All domain agents run concurrently via asyncio.gather().
                                      Total review time = slowest single agent (not sum of all agents).
                                              """
              start_time = time.monotonic()
              metadata = asset_metadata or {}
              active_agents = self._get_active_agents()

        logger.info(
                      "orchestrator_review_started",
                      asset_id=asset_id,
                      filename=asset_filename,
                      domains=[d.value for d in active_agents.keys()],
        )

        # Step 1: Retrieve compliance guidance from vector store (RAG)
        retrieved_context = await self.retriever.retrieve_for_asset(
                      asset_content=asset_content,
                      asset_metadata=metadata,
        )

        # Step 2: Fan out to all domain agents in parallel
        review_tasks = [
                      agent.review(
                                        asset_id=asset_id,
                                        asset_content=asset_content,
                                        retrieved_context=retrieved_context,
                                        asset_metadata=metadata,
                      )
                      for agent in active_agents.values()
        ]

        domain_results: list[DomainReviewResult] = await asyncio.gather(*review_tasks)

        # Step 3: Score and aggregate
        overall_severity = self.scorer.compute_overall_severity(domain_results)
        overall_passed = overall_severity in (Severity.PASS, Severity.LOW)

        # Step 4: Evaluate escalation
        escalation_triggers = self.escalation_evaluator.evaluate(
                      domain_results=domain_results,
                      threshold=self.settings.escalation_threshold,
        )

        duration_ms = int((time.monotonic() - start_time) * 1000)

        # Step 5: Build final report
        report = ComplianceReport(
                      asset_id=asset_id,
                      asset_filename=asset_filename,
                      overall_passed=overall_passed,
                      overall_severity=overall_severity,
                      domain_results=domain_results,
                      executive_summary=self._build_executive_summary(
                                        domain_results, overall_passed, overall_severity
                      ),
                      review_duration_ms=duration_ms,
        )

        logger.info(
                      "orchestrator_review_complete",
                      asset_id=asset_id,
                      overall_passed=overall_passed,
                      overall_severity=overall_severity.value,
                      requires_human_review=report.requires_human_review,
                      total_findings=report.total_findings,
                      duration_ms=duration_ms,
        )

        return report

    def _build_executive_summary(
              self,
              domain_results: list[DomainReviewResult],
              overall_passed: bool,
              overall_severity: Severity,
    ) -> str:
              passed_domains = [r.domain.value for r in domain_results if r.passed]
              failed_domains = [r.domain.value for r in domain_results if not r.passed]
              escalation_domains = [r.domain.value for r in domain_results if r.requires_human_review]

        status = "PASSED" if overall_passed else "FAILED"
        summary = f"Compliance review {status} with overall severity: {overall_severity.value.upper()}. "

        if passed_domains:
                      summary += f"Passed domains: {', '.join(passed_domains)}. "
                  if failed_domains:
                                summary += f"Failed domains: {', '.join(failed_domains)}. "
                            if escalation_domains:
                                          summary += f"Human review required for: {', '.join(escalation_domains)}."

        return summary
