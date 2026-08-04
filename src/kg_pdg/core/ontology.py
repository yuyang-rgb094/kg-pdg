"""Ontology: four-dimensional ontology framework for KG-PDG.

The four dimensions are:

1. Knowledge type (depth): A_CONCEPT -> B_DIAGNOSIS -> C_OPERATION ->
   D_DECISION -> E_COMPLICATION.
2. Evidence level: T0_TEXTBOOK, P0_RCT, P1_CONSENSUS, P2_REGISTRY.
3. Meta-path (reasoning chain): modality -> feature -> risk_stratification
   -> intervention -> outcome.
4. Relation type: how entities connect to each other.

The Ontology class is the generic, domain-agnostic reference implementation.
Domain-specific behaviour is provided by adapters (see ``kg_pdg.adapters``).
"""
from __future__ import annotations

from kg_pdg.models.entity import Entity
from kg_pdg.models.evidence import EvidenceLevel, KnowledgeType


class Ontology:
    """Generic four-dimensional ontology reference."""

    # Dimension 1: knowledge types with descriptions and depth standards.
    KNOWLEDGE_TYPES: dict[KnowledgeType, dict] = {
        KnowledgeType.A_CONCEPT: {
            "code": "A_CONCEPT",
            "description": "Foundational concept, definition, or threshold value",
            "depth_standard": {
                "min_sources": 2,
                "required_fields": ["definition", "threshold_value", "origin_reference"],
            },
        },
        KnowledgeType.B_DIAGNOSIS: {
            "code": "B_DIAGNOSIS",
            "description": "Diagnostic criteria and imaging feature identification",
            "depth_standard": {
                "min_sources": 2,
                "required_fields": ["criteria", "sensitivity", "specificity"],
            },
        },
        KnowledgeType.C_OPERATION: {
            "code": "C_OPERATION",
            "description": "Operational procedure and intervention technique",
            "depth_standard": {
                "min_sources": 3,
                "required_fields": ["procedure", "indications", "contraindications"],
            },
        },
        KnowledgeType.D_DECISION: {
            "code": "D_DECISION",
            "description": "Clinical decision and risk stratification logic",
            "depth_standard": {
                "min_sources": 3,
                "required_fields": ["decision_rule", "risk_factors", "outcome_measure"],
            },
        },
        KnowledgeType.E_COMPLICATION: {
            "code": "E_COMPLICATION",
            "description": "Complication, adverse event, and management",
            "depth_standard": {
                "min_sources": 2,
                "required_fields": ["complication", "incidence", "management"],
            },
        },
    }

    # Dimension 2: evidence hierarchy ordered from most to least foundational.
    EVIDENCE_HIERARCHY: list[EvidenceLevel] = [
        EvidenceLevel.T0_TEXTBOOK,
        EvidenceLevel.P0_RCT,
        EvidenceLevel.P1_CONSENSUS,
        EvidenceLevel.P2_REGISTRY,
    ]

    # Dimension 3: the 5-node meta-path template (slot names).
    META_PATH_TEMPLATE: list[str] = [
        "modality",
        "feature",
        "risk_stratification",
        "intervention",
        "outcome",
    ]

    # Dimension 4: relation types and their descriptions.
    RELATION_TYPES: dict[str, str] = {
        "SOURCE_OF_THRESHOLD": "source is the origin of a threshold/standard",
        "PRECURSOR_OF": "source is a technical precursor of the target",
        "VALIDATED_BY": "source is validated by the target evidence",
        "COMPLEMENTARY_TO": "source and target complement each other",
        "EXTENDS": "source extends the target concept",
        "CITES": "source cites the target",
        "DERIVES_FROM": "source derives from the target",
        "CONTRADICTS": "source contradicts the target",
    }

    # Granularity triggers shared with adapters.
    GRANULARITY_TRIGGERS: dict[str, int | float] = {
        "max_lines": 300,
        "single_source_ratio": 0.6,
    }

    def get_depth_standard(self, knowledge_type: KnowledgeType) -> dict:
        """Return the depth standard for a knowledge type.

        The depth standard specifies the minimum number of sources and the
        required content sections an entity of this type must contain.
        """
        entry = self.KNOWLEDGE_TYPES.get(knowledge_type)
        if entry is None:
            return {}
        return entry.get("depth_standard", {})

    def validate_entity(self, entity: Entity) -> list[str]:
        """Validate an entity against the ontology.

        Returns a list of human-readable validation error strings; an empty
        list means the entity is compliant.
        """
        errors: list[str] = []

        if not entity.entity_id:
            errors.append("Entity must have a non-empty entity_id.")
        if not entity.title:
            errors.append("Entity must have a non-empty title.")
        if not isinstance(entity.knowledge_type, KnowledgeType):
            errors.append("Entity knowledge_type must be a KnowledgeType enum member.")
        if not isinstance(entity.evidence_level, EvidenceLevel):
            errors.append("Entity evidence_level must be an EvidenceLevel enum member.")
        if not entity.content:
            errors.append("Entity content must not be empty.")

        standard = self.get_depth_standard(entity.knowledge_type)
        min_sources = standard.get("min_sources", 0)
        if len(entity.sources) < min_sources:
            errors.append(
                f"Entity {entity.entity_id} has {len(entity.sources)} source(s); "
                f"{entity.knowledge_type.value} requires at least {min_sources}."
            )
        return errors

    def check_coverage(self, entity: Entity, source_content_length: int) -> float:
        """Return the coverage ratio of an entity relative to a source.

        Coverage is the fraction of the source's content length that the
        entity's content represents, clamped to [0, 1].
        """
        if source_content_length <= 0:
            return 0.0
        return min(len(entity.content) / source_content_length, 1.0)

    def should_trigger_split(self, entity: Entity) -> bool:
        """Return True if an entity should be split per granularity rules."""
        return entity.needs_split()

    def should_trigger_reverse_restruct(self, source_length: int) -> bool:
        """Return True if reverse restructuring should be triggered.

        Reverse restructuring re-reads a source when it is much larger than
        what has been extracted, indicating sparse coverage of a big source.
        """
        threshold = self.GRANULARITY_TRIGGERS["max_lines"]
        return source_length > threshold * 3
