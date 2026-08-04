"""Entity dataclass representing a knowledge graph node."""
from __future__ import annotations

from dataclasses import dataclass, field

from kg_pdg.models.evidence import EvidenceLevel, KnowledgeType

# Granularity thresholds used by Entity.needs_split().
_MAX_LINES = 300
_SINGLE_SOURCE_RATIO = 0.6


@dataclass
class Entity:
    """A knowledge graph node.

    Attributes:
        entity_id: Unique identifier of the node.
        title: Human-readable title.
        category: Coarse category, e.g. "plaque_type", "imaging_feature",
            "clinical_trial".
        knowledge_type: Depth-dimension classification (A_CONCEPT ... E_COMPLICATION).
        evidence_level: Evidence-dimension classification (T0_TEXTBOOK ... P2_REGISTRY).
        tags: Free-form tags for retrieval.
        aliases: Alternative names / synonyms.
        content: The actual knowledge content (free text).
        sources: Citation identifiers (DOIs / PMIDs) backing the content.
        created_at: ISO-8601 creation timestamp.
        updated_at: ISO-8601 last-update timestamp.
        evolution_chain: Ordered records tracking how the concept evolved.
    """

    entity_id: str
    title: str
    category: str
    knowledge_type: KnowledgeType
    evidence_level: EvidenceLevel
    tags: list[str] = field(default_factory=list)
    aliases: list[str] = field(default_factory=list)
    content: str = ""
    sources: list[str] = field(default_factory=list)
    created_at: str = ""
    updated_at: str = ""
    evolution_chain: list[dict] = field(default_factory=list)

    def line_count(self) -> int:
        """Return the number of lines in the entity content."""
        return len(self.content.splitlines()) if self.content else 0

    def coverage_ratio(self, source_id: str) -> float:
        """Return the approximate fraction of content attributed to ``source_id``.

        Without per-source content attribution we approximate the ratio as a
        uniform split across the entity's sources. A source that is not listed
        contributes zero.
        """
        if not self.sources or source_id not in self.sources:
            return 0.0
        return 1.0 / len(self.sources)

    def needs_split(self) -> bool:
        """Return True if the entity should be split.

        Triggers when the content exceeds the line threshold or when a single
        source contributes more than the allowed ratio (i.e. the entity is
        dominated by one source).
        """
        if self.line_count() > _MAX_LINES:
            return True
        if self.sources:
            dominant_ratio = max(self.coverage_ratio(src) for src in self.sources)
            if dominant_ratio > _SINGLE_SOURCE_RATIO:
                return True
        return False
