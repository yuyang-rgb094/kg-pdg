"""Phase 3: Complete.

Creates new entities (or extends existing ones) following the ontology depth
standard, closes citation-path gaps by adding relations, annotates evidence
levels and limitations, and checks whether entities need splitting.
"""
from __future__ import annotations

from datetime import datetime, timezone

from kg_pdg.core.ontology import Ontology
from kg_pdg.models.entity import Entity
from kg_pdg.models.evidence import EvidenceLevel, KnowledgeType
from kg_pdg.models.relation import Relation, RelationType


class Complete:
    """Phase 3 engine: create / extend / connect / annotate entities."""

    def __init__(self, ontology: Ontology | None = None, adapter=None) -> None:
        self.ontology = ontology or Ontology()
        self.adapter = adapter

    def assign_tier(self, entity_desc: str, graph: dict) -> str:
        """Assign a tier (Tier1 / Tier2a / Tier2b / Tier3) to a description.

        - Tier1: the description matches an existing entity title (direct hit).
        - Tier2a: the description matches a tag or alias.
        - Tier2b: the description appears inside entity content.
        - Tier3: no match anywhere (truly new entity).
        """
        entities = graph.get("entities", {})
        desc = entity_desc.lower()

        if any(desc in e.title.lower() for e in entities.values()):
            return "Tier1"
        for e in entities.values():
            aliases_tags = [t.lower() for t in e.tags + e.aliases]
            if desc in aliases_tags:
                return "Tier2a"
        if any(desc in e.content.lower() for e in entities.values()):
            return "Tier2b"
        return "Tier3"

    def create_entity(self, template: dict, tier: str) -> Entity:
        """Create a new entity following the ontology depth standard."""
        now = datetime.now(timezone.utc).isoformat()

        knowledge_type = template.get("knowledge_type", KnowledgeType.A_CONCEPT)
        if isinstance(knowledge_type, str):
            knowledge_type = KnowledgeType(knowledge_type)
        evidence_level = template.get("evidence_level", EvidenceLevel.L6_SINGLE_CENTER_COHORT)
        if isinstance(evidence_level, str):
            evidence_level = EvidenceLevel(evidence_level)

        standard = self.ontology.get_depth_standard(knowledge_type)
        content = template.get("content", "")

        # Ensure the content exposes the sections required by the depth standard.
        required = standard.get("required_fields", [])
        if required:
            missing_sections = [
                f for f in required if f not in content.lower()
            ]
            if missing_sections:
                content = content + "\n\n" + "\n".join(
                    f"## {f}" for f in missing_sections
                )

        return Entity(
            entity_id=template.get("entity_id", f"ent-{tier}-{now}"),
            title=template.get("title", "Untitled"),
            category=template.get("category", "unknown"),
            knowledge_type=knowledge_type,
            evidence_level=evidence_level,
            tags=list(template.get("tags", [])),
            aliases=list(template.get("aliases", [])),
            content=content,
            sources=list(template.get("sources", [])),
            created_at=now,
            updated_at=now,
            evolution_chain=list(template.get("evolution_chain", [])),
        )

    def extend_entity(self, existing_entity: Entity, new_content: str) -> Entity:
        """Extend an existing entity with additional content."""
        existing_entity.content = existing_entity.content + "\n\n" + new_content
        existing_entity.updated_at = datetime.now(timezone.utc).isoformat()
        existing_entity.evolution_chain = existing_entity.evolution_chain + [
            {"action": "extend", "content_preview": new_content[:200]}
        ]
        return existing_entity

    def close_citation_path(self, entity: Entity, graph: dict) -> list[Relation]:
        """Create relations that close citation gaps for ``entity``."""
        relations = graph.get("relations", [])
        entities = graph.get("entities", {})
        existing = {(r.source_id, r.target_id, r.relation_type) for r in relations}
        now = datetime.now(timezone.utc).isoformat()
        new_relations: list[Relation] = []

        # Link the entity to the sources it derives from.
        for src in entity.sources:
            if src in entities:
                key = (entity.entity_id, src, RelationType.DERIVES_FROM)
                if key not in existing:
                    new_relations.append(
                        Relation(
                            entity.entity_id,
                            src,
                            RelationType.DERIVES_FROM,
                            0.8,
                            [src],
                            now,
                        )
                    )

        # If the entity is a concept, link it to validating RCT evidence.
        for eid, ent in entities.items():
            if eid == entity.entity_id:
                continue
            if ent.evidence_level in (
                EvidenceLevel.L2_MULTICENTER_RCT,
                EvidenceLevel.L3_SINGLE_CENTER_RCT,
            ):
                key = (entity.entity_id, eid, RelationType.VALIDATED_BY)
                if key not in existing:
                    new_relations.append(
                        Relation(
                            entity.entity_id,
                            eid,
                            RelationType.VALIDATED_BY,
                            0.7,
                            [],
                            now,
                        )
                    )

        return new_relations

    def annotate_evidence(self, entity: Entity) -> Entity:
        """Annotate an entity with its evidence grade and limitations."""
        level = entity.evidence_level
        if level in (
            EvidenceLevel.L8_TEXTBOOK,
            EvidenceLevel.L1_SYSTEMATIC_REVIEW,
        ):
            annotation = {"action": "annotate", "grade": "L1", "limitations": []}
        elif level in (
            EvidenceLevel.L2_MULTICENTER_RCT,
            EvidenceLevel.L3_SINGLE_CENTER_RCT,
        ):
            annotation = {
                "action": "annotate",
                "grade": "L2",
                "limitations": ["single-center bias"] if level ==
                    EvidenceLevel.L3_SINGLE_CENTER_RCT else [],
            }
        elif level in (
            EvidenceLevel.L4_GUIDELINE,
            EvidenceLevel.L7_CONSENSUS,
        ):
            annotation = {
                "action": "annotate",
                "grade": "L4",
                "limitations": ["expert opinion"],
            }
        else:
            annotation = {
                "action": "annotate",
                "grade": "L5",
                "limitations": ["observational bias"],
            }
        entity.evolution_chain = entity.evolution_chain + [annotation]
        entity.updated_at = datetime.now(timezone.utc).isoformat()
        return entity

    def check_granularity(self, entity: Entity) -> bool:
        """Return True if an entity needs splitting per granularity rules."""
        return self.ontology.should_trigger_split(entity)
