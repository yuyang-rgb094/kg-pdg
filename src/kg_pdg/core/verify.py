"""Phase 4: Verify.

Audits the knowledge graph for bidirectional-link completeness, computes
source coverage ratios, runs a backtest with probe questions, validates
ontology compliance, and generates a completion report.
"""
from __future__ import annotations

import random

from kg_pdg.core.ontology import Ontology
from kg_pdg.utils.graph import GraphUtils


class Verify:
    """Phase 4 engine: audit, backtest, and report."""

    def __init__(self, ontology: Ontology | None = None) -> None:
        self.ontology = ontology or Ontology()

    def check_bidirectional_links(self, graph: dict) -> list[str]:
        """Find unidirectional links and return them as 'src->tgt' strings."""
        broken = GraphUtils.detect_broken_links(graph)
        return [f"{src}->{tgt}" for src, tgt in broken]

    def audit_coverage(self, graph: dict, sources: dict[str, int]) -> dict:
        """Compute coverage ratios for every (entity, source) pair.

        ``sources`` maps a source id to the length of its original content.
        The returned dict includes an ``__average__`` entry.
        """
        entities = graph.get("entities", {})
        report: dict[str, float] = {}
        total_ratio = 0.0
        count = 0
        for eid, ent in entities.items():
            for src in ent.sources:
                src_len = sources.get(src, 0)
                if src_len > 0:
                    ratio = self.ontology.check_coverage(ent, src_len)
                    report[f"{eid}:{src}"] = ratio
                    total_ratio += ratio
                    count += 1
        report["__average__"] = total_ratio / count if count else 0.0
        return report

    def probe_backtest(self, graph: dict, questions: list[str]) -> dict:
        """Test up to 3 random probe questions against the graph."""
        # Local import to avoid an import cycle at module load time.
        from kg_pdg.core.probe import Probe

        results: dict[str, dict] = {}
        if not questions:
            return results
        sample = random.sample(questions, min(3, len(questions)))
        for q in sample:
            probe = Probe(q, graph)
            meta_path = probe.parse_question()
            query_result = probe.query_graph(meta_path, graph)
            gap = probe.assess_coverage(query_result)
            results[q] = {
                "matched_count": len(query_result["matched_entities"]),
                "missing_count": len(gap.missing_entities),
                "severity": gap.severity,
            }
        return results

    def generate_report(self, results: dict) -> str:
        """Generate a human-readable completion report."""
        lines = ["# KG-PDG Verification Report", ""]

        bidir = results.get("bidirectional_issues", [])
        coverage = results.get("coverage", {})
        backtest = results.get("backtest", {})
        compliance = results.get("compliance", [])

        lines.append(f"Bidirectional link issues: {len(bidir)}")
        for issue in bidir:
            lines.append(f"  - {issue}")
        lines.append("")

        avg = coverage.get("__average__", 0.0) if isinstance(coverage, dict) else 0.0
        lines.append(f"Average coverage: {avg:.2f}")
        lines.append("")

        lines.append(f"Backtest questions: {len(backtest)}")
        for q, r in backtest.items():
            lines.append(
                f"  - '{q}': matched={r['matched_count']}, "
                f"missing={r['missing_count']}, severity={r['severity']}"
            )
        lines.append("")

        lines.append(f"Ontology compliance issues: {len(compliance)}")
        for issue in compliance:
            lines.append(f"  - {issue}")

        return "\n".join(lines)

    def validate_ontology_compliance(self, graph: dict) -> list[str]:
        """Check that all entities meet the ontology standards."""
        entities = graph.get("entities", {})
        issues: list[str] = []
        for eid, ent in entities.items():
            for err in self.ontology.validate_entity(ent):
                issues.append(f"{eid}: {err}")
        return issues
