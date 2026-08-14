"""Tests for the structural-signal probe discovery engine.

The discovery engine is the first step of the KG Loop probe-discovery
engine: it scans a knowledge graph using pure graph algorithms and simple
heuristics (no LLM) to surface structural signals that warrant a probe.
"""

from __future__ import annotations

import pytest

from kg_pdg.core.discovery import StructuralProbeDiscovery
from kg_pdg.models.entity import Entity
from kg_pdg.models.evidence import EvidenceLevel, KnowledgeType
from kg_pdg.models.relation import Relation, RelationType


@pytest.fixture
def graph() -> dict:
    """A small graph with one connected pair and one isolated entity."""
    entities: dict[str, Entity] = {
        "PT001": Entity(
            entity_id="PT001",
            title="TCFA",
            category="plaque_type",
            knowledge_type=KnowledgeType.A_CONCEPT,
            evidence_level=EvidenceLevel.L8_TEXTBOOK,
            content="TCFA is a plaque with FCT <65um.",
            sources=["10.1056/NEJMoa1100547"],
        ),
        "CT001": Entity(
            entity_id="CT001",
            title="PROSPECT Trial",
            category="clinical_trial",
            knowledge_type=KnowledgeType.B_DIAGNOSIS,
            evidence_level=EvidenceLevel.L2_MULTICENTER_RCT,
            content="PROSPECT: TCFA predicts MACE.",
            sources=["10.1056/NEJMoa1100547"],
        ),
        "IS001": Entity(
            entity_id="IS001",
            title="Orphan Concept",
            category="concept",
            knowledge_type=KnowledgeType.A_CONCEPT,
            evidence_level=EvidenceLevel.L6_SINGLE_CENTER_COHORT,
            content="This entity is not connected to anything.",
            sources=["10.9999/example"],
        ),
    }
    relations: list[Relation] = [
        Relation(
            source_id="CT001",
            target_id="PT001",
            relation_type=RelationType.VALIDATED_BY,
        ),
    ]
    return {"entities": entities, "relations": relations}


class TestIsolatedNodes:
    """Structural signal 1: entities with degree zero."""

    def test_returns_entity_with_no_relations(self, graph: dict):
        discovery = StructuralProbeDiscovery(graph)
        assert discovery.find_isolated_nodes() == ["IS001"]

    def test_returns_empty_when_all_entities_connected(self, graph: dict):
        graph["relations"].append(
            Relation(
                source_id="PT001",
                target_id="IS001",
                relation_type=RelationType.EXTENDS,
            )
        )
        discovery = StructuralProbeDiscovery(graph)
        assert discovery.find_isolated_nodes() == []


class TestDeadEnds:
    """Structural signal 2: entities with in-degree but no out-degree.

    A dead end is a node where a reasoning chain terminates: something points
    to it, but it points to nothing downstream. This breaks a meta-path.
    """

    def test_returns_entity_with_inbound_but_no_outbound(self, graph: dict):
        discovery = StructuralProbeDiscovery(graph)
        # PT001 has an inbound edge (CT001->PT001) but no outbound edge.
        assert discovery.find_dead_ends() == ["PT001"]

    def test_returns_empty_when_entity_has_outbound_edge(self, graph: dict):
        graph["relations"].append(
            Relation(
                source_id="PT001",
                target_id="IS001",
                relation_type=RelationType.EXTENDS,
            )
        )
        discovery = StructuralProbeDiscovery(graph)
        # PT001 now has an outbound edge, so it is no longer a dead end.
        # IS001 now has an inbound edge but no outbound edge, so it becomes one.
        assert discovery.find_dead_ends() == ["IS001"]


@pytest.fixture
def fact_graph() -> dict:
    """Graph exercising the unsourced-fact detector."""
    entities: dict[str, Entity] = {
        "F001": Entity(
            entity_id="F001",
            title="FFR threshold",
            category="metric",
            knowledge_type=KnowledgeType.E_COMPLICATION,
            evidence_level=EvidenceLevel.L7_CONSENSUS,
            content="Ischemia is defined as FFR <=0.80.",
            sources=[],
        ),
        "F002": Entity(
            entity_id="F002",
            title="FFR threshold (sourced)",
            category="metric",
            knowledge_type=KnowledgeType.E_COMPLICATION,
            evidence_level=EvidenceLevel.L2_MULTICENTER_RCT,
            content="Ischemia is defined as FFR <=0.80.",
            sources=["10.1056/NEJMoa1201123"],
        ),
        "F003": Entity(
            entity_id="F003",
            title="TCFA",
            category="plaque_type",
            knowledge_type=KnowledgeType.A_CONCEPT,
            evidence_level=EvidenceLevel.L8_TEXTBOOK,
            content="TCFA is a thin-cap fibroatheroma.",
            sources=[],
        ),
    }
    return {"entities": entities, "relations": []}


class TestUnsourcedFacts:
    """Structural signal 3: numeric facts without any source citation."""

    def test_returns_entity_with_numeric_content_and_no_sources(
        self, fact_graph: dict
    ):
        discovery = StructuralProbeDiscovery(fact_graph)
        assert discovery.find_unsourced_facts() == ["F001"]

    def test_ignores_numeric_content_with_sources(self, fact_graph: dict):
        discovery = StructuralProbeDiscovery(fact_graph)
        assert "F002" not in discovery.find_unsourced_facts()

    def test_ignores_content_without_numeric_fact(self, fact_graph: dict):
        discovery = StructuralProbeDiscovery(fact_graph)
        assert "F003" not in discovery.find_unsourced_facts()


@pytest.fixture
def chain_graph() -> dict:
    """A linear chain CT001 -> A -> B -> C -> D for hop-distance checks."""
    def _ent(eid: str, title: str) -> Entity:
        return Entity(
            entity_id=eid,
            title=title,
            category="concept",
            knowledge_type=KnowledgeType.A_CONCEPT,
            evidence_level=EvidenceLevel.L6_SINGLE_CENTER_COHORT,
            content=title,
            sources=["10.9999/example"],
        )

    entities = {
        "CT001": _ent("CT001", "Consensus Trial"),
        "A": _ent("A", "Concept A"),
        "B": _ent("B", "Concept B"),
        "C": _ent("C", "Concept C"),
        "D": _ent("D", "Concept D"),
    }
    relations = [
        Relation(source_id="CT001", target_id="A", relation_type=RelationType.EXTENDS),
        Relation(source_id="A", target_id="B", relation_type=RelationType.EXTENDS),
        Relation(source_id="B", target_id="C", relation_type=RelationType.EXTENDS),
        Relation(source_id="C", target_id="D", relation_type=RelationType.EXTENDS),
    ]
    return {"entities": entities, "relations": relations}


class TestUnclosedCitations:
    """Structural signal 4: entities too far from a consensus node."""

    def test_returns_entities_beyond_max_hops(self, chain_graph: dict):
        discovery = StructuralProbeDiscovery(chain_graph)
        # Consensus = CT001. D is 4 hops away; with max_hops=3 it is unclosed.
        result = discovery.find_unclosed_citations(["CT001"], max_hops=3)
        assert ("D", 4) in result
        assert all(eid != "C" for eid, _ in result)

    def test_returns_unreachable_entities(self, graph: dict):
        discovery = StructuralProbeDiscovery(graph)
        # IS001 is not connected to consensus CT001 -> distance -1.
        result = discovery.find_unclosed_citations(["CT001"], max_hops=3)
        assert ("IS001", -1) in result


class TestDiscover:
    """The discover() entry point aggregates signals into a report."""

    def test_aggregates_all_detected_signals(self, graph: dict):
        discovery = StructuralProbeDiscovery(graph)
        report = discovery.discover(consensus_ids=["CT001"])
        # IS001 is isolated; PT001 is a dead end. Both should surface.
        assert report.count() >= 2

    def test_every_signal_has_probe_and_severity(self, graph: dict):
        discovery = StructuralProbeDiscovery(graph)
        report = discovery.discover(consensus_ids=["CT001"])
        for sig in report.signals:
            assert sig.suggested_probe
            assert sig.severity

    def test_by_type_filters_signals(self, graph: dict):
        discovery = StructuralProbeDiscovery(graph)
        report = discovery.discover(consensus_ids=["CT001"])
        isolated = report.by_type("ISOLATED_NODE")
        assert [s.entity_id for s in isolated] == ["IS001"]
