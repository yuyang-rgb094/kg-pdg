"""Pipeline orchestrating the four KG-PDG phases.

The pipeline runs Probe -> Recall -> Complete -> Verify in sequence, logging
the progress and output of each phase, and returns a summary containing the
updated graph and the reports produced by each phase.
"""
from __future__ import annotations

import logging

from kg_pdg.adapters.base import BaseAdapter
from kg_pdg.core.complete import Complete
from kg_pdg.core.discovery import StructuralProbeDiscovery
from kg_pdg.core.ontology import Ontology
from kg_pdg.core.probe import Probe
from kg_pdg.core.recall import Recall
from kg_pdg.core.verify import Verify

logger = logging.getLogger(__name__)


class Pipeline:
    """Orchestrator for the four-phase KG-PDG growth loop."""

    def __init__(self, adapter: BaseAdapter) -> None:
        self.adapter = adapter
        self.ontology = Ontology()

    def run(self, question: str, graph: dict) -> dict:
        """Execute the full 4-phase loop and return a summary dict."""
        logger.info("KG-PDG pipeline started for question: %s", question)

        # ------------------------------------------------------------------
        # Phase 1: Probe
        # ------------------------------------------------------------------
        logger.info("Phase 1 - Probe: parsing question and assessing coverage.")
        probe = Probe(question, graph)
        meta_path = probe.parse_question()
        query_result = probe.query_graph(meta_path, graph)
        gap_report = probe.assess_coverage(query_result)
        probe.classify_tiers(gap_report)
        logger.info(
            "Phase 1 complete. severity=%s, missing=%d, broken=%d, gaps=%d",
            gap_report.severity,
            len(gap_report.missing_entities),
            len(gap_report.broken_links),
            len(gap_report.coverage_gaps),
        )

        # ------------------------------------------------------------------
        # Phase 2: Recall
        # ------------------------------------------------------------------
        logger.info("Phase 2 - Recall: predicting missing entities and searching.")
        recall = Recall(self.adapter)
        predictions = recall.predict_missing_entities(gap_report)
        queries = recall.search_strategy(predictions)
        ranked = recall.rank_results(queries, gap_report)
        recall_report = recall.generate_recall_report(ranked)
        logger.info(
            "Phase 2 complete. predictions=%d, queries=%d, hit_rate=%.2f",
            len(predictions),
            len(queries),
            recall_report["hit_rate"],
        )

        # ------------------------------------------------------------------
        # Phase 3: Complete
        # ------------------------------------------------------------------
        logger.info("Phase 3 - Complete: creating entities and closing paths.")
        complete = Complete(self.ontology, self.adapter)
        entities = graph.setdefault("entities", {})
        relations = graph.setdefault("relations", [])
        for pred in predictions:
            tier = complete.assign_tier(pred.get("description", ""), graph)
            template = {
                "title": pred.get("description", "New entity"),
                "category": pred.get("predicted_entity_type", "unknown"),
                "knowledge_type": "A_CONCEPT",
                "evidence_level": "L6_SINGLE_CENTER_COHORT",
                "content": pred.get("description", ""),
                "sources": [],
                "tags": [pred.get("slot", "")],
            }
            new_entity = complete.create_entity(template, tier)
            new_entity = complete.annotate_evidence(new_entity)
            entities[new_entity.entity_id] = new_entity
            relations.extend(complete.close_citation_path(new_entity, graph))
        logger.info(
            "Phase 3 complete. entities=%d, relations=%d",
            len(entities),
            len(relations),
        )

        # ------------------------------------------------------------------
        # Phase 4: Verify
        # ------------------------------------------------------------------
        logger.info("Phase 4 - Verify: auditing graph.")
        verify = Verify(self.ontology)
        bidirectional_issues = verify.check_bidirectional_links(graph)
        coverage = verify.audit_coverage(graph, {})
        backtest = verify.probe_backtest(graph, [question])
        compliance = verify.validate_ontology_compliance(graph)

        verification_report = {
            "bidirectional_issues": bidirectional_issues,
            "coverage": coverage,
            "backtest": backtest,
            "compliance": compliance,
        }
        completion_report = verify.generate_report(verification_report)
        logger.info(
            "Phase 4 complete. compliance_issues=%d, bidirectional_issues=%d",
            len(compliance),
            len(bidirectional_issues),
        )

        return {
            "updated_graph": graph,
            "gap_report": gap_report,
            "recall_report": recall_report,
            "completion_report": completion_report,
            "verification_report": verification_report,
        }

    def run_discovery(
        self,
        graph: dict,
        consensus_ids: list[str] | None = None,
        max_hops: int = 3,
    ) -> dict:
        """Auto-discover structural signals and grow the graph via the loop.

        Scans the graph for structural gaps (isolated nodes, dead ends,
        unsourced facts, unclosed citations), then runs the full 4-phase loop
        once per detected signal. Each probe operates on the graph as updated
        by the previous probe, so the graph grows incrementally. This is the
        self-driving entry point of the KG Loop: no external input required.
        """
        discovery = StructuralProbeDiscovery(graph)
        report = discovery.discover(
            consensus_ids=consensus_ids, max_hops=max_hops
        )
        logger.info(
            "Discovery found %d structural signals; running one loop each.",
            report.count(),
        )

        probe_results: list[dict] = []
        for sig in report.signals:
            logger.info(
                "Auto-probe [%s] %s: %s",
                sig.signal_type,
                sig.entity_id,
                sig.suggested_probe,
            )
            result = self.run(sig.suggested_probe, graph)
            probe_results.append(
                {
                    "signal_type": sig.signal_type,
                    "entity_id": sig.entity_id,
                    "severity": sig.severity,
                    "suggested_probe": sig.suggested_probe,
                    "result": result,
                }
            )

        return {
            "discovery_report": report,
            "probe_results": probe_results,
            "updated_graph": graph,
        }
