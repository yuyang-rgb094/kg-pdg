"""Phase 1: Probe.

Maps a natural-language question onto a 5-node meta-path, queries the
knowledge graph for matching entities, and produces a GapReport describing
missing entities, broken links, and coverage gaps. Gaps are then classified
into tiers (Tier1 / Tier2a / Tier2b / Tier3) based on graph distance and
evidence strength.
"""
from __future__ import annotations

from kg_pdg.models.entity import Entity
from kg_pdg.models.gap import GapReport, MetaPath
from kg_pdg.utils.graph import GraphUtils

# Generic keyword heuristics for mapping questions to meta-path slots.
_SLOT_KEYWORDS: dict[str, list[str]] = {
    "modality": [
        "modality", "imaging", "oct", "ivus", "ct", "mri", "ultrasound",
        "angiography", "method", "technique", "scan",
    ],
    "feature": [
        "feature", "plaque", "calcification", "stenosis", "morphology",
        "characteristic", "sign", "finding",
    ],
    "risk_stratification": [
        "risk", "stratification", "score", "classification", "stratify",
        "high-risk", "vulnerable",
    ],
    "intervention": [
        "intervention", "stent", "pci", "procedure", "treatment", "therapy",
        "surgery", "operation",
    ],
    "outcome": [
        "outcome", "prognosis", "mace", "survival", "mortality", "result",
        "endpoint", "follow-up",
    ],
}

# Required coverage ratio for a source to be considered adequately extracted.
_REQUIRED_COVERAGE = 0.6


class Probe:
    """Phase 1 engine: question -> meta-path -> gap report."""

    def __init__(self, question: str, graph: dict) -> None:
        self.question = question
        self.graph = graph

    def parse_question(self, question: str | None = None) -> MetaPath:
        """Map a natural-language question to a 5-node MetaPath instance."""
        q = (question or self.question).lower()
        slots: dict[str, str] = {}
        for slot, keywords in _SLOT_KEYWORDS.items():
            for kw in keywords:
                if kw in q:
                    slots[slot] = kw
                    break
        return MetaPath(
            modality=slots.get("modality", ""),
            feature=slots.get("feature", ""),
            risk_stratification=slots.get("risk_stratification", ""),
            intervention=slots.get("intervention", ""),
            outcome=slots.get("outcome", ""),
        )

    def query_graph(self, meta_path: MetaPath, graph: dict | None = None) -> dict:
        """Query the graph for entities matching the meta-path slots."""
        g = graph or self.graph
        entities: dict[str, Entity] = g.get("entities", {})
        relations = g.get("relations", [])

        slot_values = [
            meta_path.modality,
            meta_path.feature,
            meta_path.risk_stratification,
            meta_path.intervention,
            meta_path.outcome,
        ]
        active_values = [v for v in slot_values if v]

        matched_entities: dict[str, Entity] = {}
        for eid, ent in entities.items():
            haystack = " ".join(
                [ent.title, ent.content, " ".join(ent.tags), " ".join(ent.aliases)]
            ).lower()
            if any(v in haystack for v in active_values):
                matched_entities[eid] = ent

        matched_ids = set(matched_entities)
        matched_relations = [
            r for r in relations
            if r.source_id in matched_ids or r.target_id in matched_ids
        ]

        return {
            "meta_path": meta_path,
            "matched_entities": matched_entities,
            "matched_relations": matched_relations,
            "all_entities": entities,
            "all_relations": relations,
        }

    def assess_coverage(self, query_result: dict) -> GapReport:
        """Identify missing entities, broken links, and coverage gaps."""
        meta_path: MetaPath = query_result["meta_path"]
        matched: dict[str, Entity] = query_result["matched_entities"]
        all_entities: dict[str, Entity] = query_result["all_entities"]
        all_relations = query_result["all_relations"]

        slot_values = {
            "modality": meta_path.modality,
            "feature": meta_path.feature,
            "risk_stratification": meta_path.risk_stratification,
            "intervention": meta_path.intervention,
            "outcome": meta_path.outcome,
        }

        missing_entities: list[str] = []
        for slot, value in slot_values.items():
            if not value:
                continue
            has_match = any(
                value in " ".join(
                    [e.title, e.content, " ".join(e.tags), " ".join(e.aliases)]
                ).lower()
                for e in matched.values()
            )
            if not has_match:
                missing_entities.append(f"{slot}:{value}")

        broken_links = GraphUtils.detect_broken_links(
            {"entities": all_entities, "relations": all_relations}
        )

        coverage_gaps: list[dict] = []
        for eid, ent in all_entities.items():
            for src in ent.sources:
                ratio = ent.coverage_ratio(src)
                if ratio < _REQUIRED_COVERAGE:
                    coverage_gaps.append(
                        {
                            "entity_id": eid,
                            "source_id": src,
                            "current_coverage": ratio,
                            "required_coverage": _REQUIRED_COVERAGE,
                        }
                    )

        severity = self._severity(missing_entities, broken_links, coverage_gaps)

        return GapReport(
            probe_question=self.question,
            meta_path=meta_path,
            missing_entities=missing_entities,
            broken_links=broken_links,
            coverage_gaps=coverage_gaps,
            tier_classification={},
            severity=severity,
        )

    @staticmethod
    def _severity(
        missing: list[str],
        broken: list[tuple[str, str]],
        gaps: list[dict],
    ) -> str:
        score = len(missing) * 2 + len(broken) + len(gaps)
        if score >= 8:
            return "P0_CRITICAL"
        if score >= 5:
            return "P1_HIGH"
        if score >= 2:
            return "P2_MODERATE"
        return "P3_LOW"

    def classify_tiers(self, gap_report: GapReport) -> dict[str, list[str]]:
        """Classify gaps into Tier1 / Tier2a / Tier2b / Tier3.

        - Tier1: missing entities directly on the meta-path.
        - Tier2a: broken (unidirectional) links.
        - Tier2b: entities with insufficient source coverage.
        - Tier3: peripheral / unresolved gaps.
        """
        tiers: dict[str, list[str]] = {
            "Tier1": [],
            "Tier2a": [],
            "Tier2b": [],
            "Tier3": [],
        }
        for desc in gap_report.missing_entities:
            tiers["Tier1"].append(desc)
        for src, tgt in gap_report.broken_links:
            tiers["Tier2a"].append(f"broken_link:{src}->{tgt}")
        for gap in gap_report.coverage_gaps:
            tiers["Tier2b"].append(
                f"coverage:{gap['entity_id']}:{gap['source_id']}"
            )

        gap_report.tier_classification = tiers
        return tiers
