"""Structural-signal probe discovery engine.

This is the first step of the KG Loop probe-discovery engine. It scans a
knowledge graph using pure graph algorithms and simple heuristics (no LLM)
to surface structural signals that warrant a probe. Each detected signal
maps to a templated probe question that can feed the KG-PDG four-phase loop.
"""

from __future__ import annotations

import re

from kg_pdg.models.entity import Entity
from kg_pdg.models.relation import Relation
from kg_pdg.models.signal import DiscoveryReport, StructuralSignal
from kg_pdg.utils.graph import GraphUtils

# Heuristic pattern for a "numeric fact": a threshold, statistic, or ratio.
# Matches things like "<65", "<=0.80", "HR=42.73", "ratio", "%", "threshold".
_NUMERIC_FACT_PATTERN = re.compile(
    r"(<|>|≤|≥|<=|>=)\s*\d|HR\s*=|ratio|%|threshold",
    re.IGNORECASE,
)


class StructuralProbeDiscovery:
    """Detect structural signals in a knowledge graph that warrant probes."""

    def __init__(self, graph: dict) -> None:
        self.graph = graph
        self.entities: dict[str, Entity] = graph.get("entities", {})
        self.relations: list[Relation] = graph.get("relations", [])

    def _degree(self) -> dict[str, int]:
        """Return the total degree (in + out) of every entity."""
        in_degree, out_degree = self._in_out_degree()
        return {eid: in_degree[eid] + out_degree[eid] for eid in self.entities}

    def find_isolated_nodes(self) -> list[str]:
        """Return entity ids that participate in no relation (degree zero)."""
        degree = self._degree()
        return sorted(eid for eid, d in degree.items() if d == 0)

    def _in_out_degree(self) -> tuple[dict[str, int], dict[str, int]]:
        """Return (in-degree, out-degree) maps for every entity."""
        in_degree: dict[str, int] = {eid: 0 for eid in self.entities}
        out_degree: dict[str, int] = {eid: 0 for eid in self.entities}
        for r in self.relations:
            if r.source_id in out_degree:
                out_degree[r.source_id] += 1
            if r.target_id in in_degree:
                in_degree[r.target_id] += 1
        return in_degree, out_degree

    def find_dead_ends(self) -> list[str]:
        """Return entity ids with inbound but no outbound edges.

        A dead end terminates a reasoning chain: something points to it, but
        it points to nothing downstream, breaking a meta-path.
        """
        in_degree, out_degree = self._in_out_degree()
        return sorted(
            eid
            for eid in self.entities
            if in_degree[eid] > 0 and out_degree[eid] == 0
        )

    def find_unsourced_facts(self) -> list[str]:
        """Return entity ids holding a numeric fact with no source citation.

        A numeric fact (threshold, statistic, ratio) without any source is a
        strong probe signal: the value cannot be traced to evidence.
        """
        unsourced: list[str] = []
        for eid, ent in self.entities.items():
            if ent.sources:
                continue
            haystack = f"{ent.title} {ent.content}"
            if _NUMERIC_FACT_PATTERN.search(haystack):
                unsourced.append(eid)
        return sorted(unsourced)

    def find_unclosed_citations(
        self, consensus_ids: list[str], max_hops: int = 3
    ) -> list[tuple[str, int]]:
        """Return (entity_id, distance) for entities too far from consensus.

        Distance is the shortest hop count to any consensus node. Entities
        whose distance exceeds ``max_hops`` or that are unreachable (-1) are
        flagged as having an unclosed citation path to consensus.
        """
        if not consensus_ids:
            return []
        unclosed: list[tuple[str, int]] = []
        for eid in self.entities:
            if eid in consensus_ids:
                continue
            distance = min(
                GraphUtils.shortest_path(self.graph, eid, cid)
                for cid in consensus_ids
            )
            if distance > max_hops or distance == -1:
                unclosed.append((eid, distance))
        return sorted(unclosed)

    def discover(
        self,
        consensus_ids: list[str] | None = None,
        max_hops: int = 3,
    ) -> DiscoveryReport:
        """Run all structural detectors and aggregate signals into a report.

        Each detected gap is wrapped in a StructuralSignal with a templated
        probe question, ready to feed the KG-PDG growth loop.
        """
        consensus_ids = consensus_ids or []
        signals: list[StructuralSignal] = []

        for eid in self.find_isolated_nodes():
            title = self.entities[eid].title
            signals.append(
                StructuralSignal(
                    signal_type="ISOLATED_NODE",
                    entity_id=eid,
                    detail=f"Entity '{title}' participates in no relation.",
                    severity="P3_LOW",
                    suggested_probe=(
                        f"What are the relationships of '{title}' to other "
                        "concepts in the graph?"
                    ),
                )
            )

        for eid in self.find_dead_ends():
            title = self.entities[eid].title
            signals.append(
                StructuralSignal(
                    signal_type="DEAD_END",
                    entity_id=eid,
                    detail=f"Reasoning chain terminates at '{title}'.",
                    severity="P2_MODERATE",
                    suggested_probe=(
                        f"What downstream knowledge follows from '{title}' "
                        "and what outcome does it predict?"
                    ),
                )
            )

        for eid in self.find_unsourced_facts():
            title = self.entities[eid].title
            signals.append(
                StructuralSignal(
                    signal_type="UNSOURCED_FACT",
                    entity_id=eid,
                    detail=f"Numeric fact '{title}' has no source citation.",
                    severity="P1_HIGH",
                    suggested_probe=(
                        f"What is the evidence source for the numeric fact "
                        f"'{title}' and its prognostic value?"
                    ),
                )
            )

        for eid, distance in self.find_unclosed_citations(
            consensus_ids, max_hops=max_hops
        ):
            title = self.entities[eid].title
            severity = "P1_HIGH" if distance == -1 else "P2_MODERATE"
            signals.append(
                StructuralSignal(
                    signal_type="UNCLOSED_CITATION",
                    entity_id=eid,
                    detail=(
                        f"Entity '{title}' is {distance} hops from consensus."
                    ),
                    severity=severity,
                    suggested_probe=(
                        f"How does '{title}' connect to consensus within "
                        f"{distance} hops, and what is its outcome?"
                    ),
                )
            )

        return DiscoveryReport(signals=signals)
