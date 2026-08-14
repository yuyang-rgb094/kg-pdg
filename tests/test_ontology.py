"""Tests for the ontology framework."""

from __future__ import annotations

import pytest

from kg_pdg.core.ontology import Ontology
from kg_pdg.models.entity import Entity
from kg_pdg.models.evidence import EvidenceLevel, KnowledgeType


@pytest.fixture
def ontology() -> Ontology:
    return Ontology()


@pytest.fixture
def sample_entity() -> Entity:
    return Entity(
        entity_id="PT001",
        title="TCFA",
        category="plaque_type",
        knowledge_type=KnowledgeType.A_CONCEPT,
        evidence_level=EvidenceLevel.L8_TEXTBOOK,
        tags=["KG/plaque_type"],
        aliases=["thin-cap fibroatheroma"],
        content="TCFA is a plaque with FCT <65um.\nKey evidence: PROSPECT trial.",
        sources=["10.1056/NEJMoa1100547", "31504405"],
        created_at="2026-01-15T00:00:00",
        updated_at="2026-01-15T00:00:00",
    )


@pytest.fixture
def oversized_entity() -> Entity:
    """An entity with >300 lines of content."""
    return Entity(
        entity_id="BIG001",
        title="Oversized Entity",
        category="operation",
        knowledge_type=KnowledgeType.C_OPERATION,
        evidence_level=EvidenceLevel.L7_CONSENSUS,
        content="\n".join(f"Line {i}" for i in range(350)),
        sources=["src1"],
        created_at="2026-01-15T00:00:00",
        updated_at="2026-01-15T00:00:00",
    )


class TestKnowledgeTypes:
    """Tests for the knowledge type dimension."""

    def test_five_types_defined(self, ontology: Ontology):
        assert len(ontology.KNOWLEDGE_TYPES) == 5
        assert KnowledgeType.A_CONCEPT in ontology.KNOWLEDGE_TYPES
        assert KnowledgeType.E_COMPLICATION in ontology.KNOWLEDGE_TYPES

    def test_each_type_has_depth_standard(self, ontology: Ontology):
        for kt, info in ontology.KNOWLEDGE_TYPES.items():
            assert "depth_standard" in info
            assert "min_sources" in info["depth_standard"]
            assert "required_fields" in info["depth_standard"]

    def test_operation_requires_most_sources(self, ontology: Ontology):
        """C_OPERATION should require >=3 sources (most demanding type)."""
        standard = ontology.get_depth_standard(KnowledgeType.C_OPERATION)
        assert standard["min_sources"] >= 3


class TestEvidenceHierarchy:
    """Tests for the evidence hierarchy dimension."""

    def test_eleven_levels(self, ontology: Ontology):
        assert len(ontology.EVIDENCE_HIERARCHY) == 11
        assert EvidenceLevel.L1_SYSTEMATIC_REVIEW in ontology.EVIDENCE_HIERARCHY
        assert EvidenceLevel.L11_CASE_REPORT in ontology.EVIDENCE_HIERARCHY


class TestMetaPath:
    """Tests for the meta-path dimension."""

    def test_five_node_template(self, ontology: Ontology):
        assert len(ontology.META_PATH_TEMPLATE) == 5
        assert ontology.META_PATH_TEMPLATE[0] == "modality"
        assert ontology.META_PATH_TEMPLATE[-1] == "outcome"


class TestRelationTypes:
    """Tests for the citation network dimension."""

    def test_eight_relation_types(self, ontology: Ontology):
        assert len(ontology.RELATION_TYPES) == 8
        assert "SOURCE_OF_THRESHOLD" in ontology.RELATION_TYPES
        assert "CONTRADICTS" in ontology.RELATION_TYPES


class TestEntityValidation:
    """Tests for entity validation against ontology standards."""

    def test_valid_entity_passes(self, ontology: Ontology, sample_entity: Entity):
        errors = ontology.validate_entity(sample_entity)
        assert errors == []

    def test_empty_content_fails(self, ontology: Ontology):
        entity = Entity(
            entity_id="X001",
            title="Empty",
            category="test",
            knowledge_type=KnowledgeType.A_CONCEPT,
            evidence_level=EvidenceLevel.L8_TEXTBOOK,
            content="",
            sources=["src1", "src2"],
        )
        errors = ontology.validate_entity(entity)
        assert any("content" in e.lower() for e in errors)

    def test_insufficient_sources_fails(self, ontology: Ontology):
        """A_CONCEPT requires >=2 sources; providing 1 should fail."""
        entity = Entity(
            entity_id="X002",
            title="Under-sourced",
            category="test",
            knowledge_type=KnowledgeType.A_CONCEPT,
            evidence_level=EvidenceLevel.L8_TEXTBOOK,
            content="Some content here.",
            sources=["only_one"],
        )
        errors = ontology.validate_entity(entity)
        assert any("source" in e.lower() for e in errors)


class TestGranularityTriggers:
    """Tests for granularity adaptation rules."""

    def test_normal_entity_no_split(self, ontology: Ontology, sample_entity: Entity):
        assert ontology.should_trigger_split(sample_entity) is False

    def test_oversized_entity_triggers_split(self, ontology: Ontology, oversized_entity: Entity):
        assert ontology.should_trigger_split(oversized_entity) is True

    def test_single_source_dominance_triggers_split(self, ontology: Ontology):
        """Entity with a single source contributing >60% should trigger split."""
        entity = Entity(
            entity_id="X003",
            title="Single Source",
            category="test",
            knowledge_type=KnowledgeType.A_CONCEPT,
            evidence_level=EvidenceLevel.L8_TEXTBOOK,
            content="Some content.",
            sources=["only_source"],
        )
        assert ontology.should_trigger_split(entity) is True


class TestCoverageAndRestructuring:
    """Tests for coverage audit and reverse restructuring."""

    def test_coverage_ratio(self, ontology: Ontology, sample_entity: Entity):
        ratio = ontology.check_coverage(sample_entity, source_content_length=1000)
        assert 0.0 < ratio <= 1.0

    def test_zero_source_length(self, ontology: Ontology, sample_entity: Entity):
        assert ontology.check_coverage(sample_entity, source_content_length=0) == 0.0

    def test_reverse_restruct_trigger(self, ontology: Ontology):
        """Source > 3x max_lines threshold should trigger reverse restructuring."""
        assert ontology.should_trigger_reverse_restruct(source_length=1200) is True

    def test_reverse_restruct_no_trigger(self, ontology: Ontology):
        assert ontology.should_trigger_reverse_restruct(source_length=500) is False
