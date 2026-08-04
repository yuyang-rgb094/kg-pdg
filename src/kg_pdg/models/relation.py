"""Relation dataclass and relation type enumeration."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class RelationType(str, Enum):
    """Types of edges between knowledge graph nodes.

    Each type has a natural bidirectional counterpart (see ``REVERSE_MAP``);
    ``Relation.reverse`` returns that counterpart.
    """

    SOURCE_OF_THRESHOLD = "SOURCE_OF_THRESHOLD"
    PRECURSOR_OF = "PRECURSOR_OF"
    VALIDATED_BY = "VALIDATED_BY"
    COMPLEMENTARY_TO = "COMPLEMENTARY_TO"
    EXTENDS = "EXTENDS"
    CITES = "CITES"
    DERIVES_FROM = "DERIVES_FROM"
    CONTRADICTS = "CONTRADICTS"


# Mapping of a relation type to its bidirectional counterpart.
REVERSE_MAP: dict[RelationType, RelationType] = {
    RelationType.SOURCE_OF_THRESHOLD: RelationType.DERIVES_FROM,
    RelationType.DERIVES_FROM: RelationType.SOURCE_OF_THRESHOLD,
    RelationType.PRECURSOR_OF: RelationType.EXTENDS,
    RelationType.EXTENDS: RelationType.PRECURSOR_OF,
    RelationType.VALIDATED_BY: RelationType.CITES,
    RelationType.CITES: RelationType.VALIDATED_BY,
    RelationType.COMPLEMENTARY_TO: RelationType.COMPLEMENTARY_TO,
    RelationType.CONTRADICTS: RelationType.CONTRADICTS,
}


@dataclass
class Relation:
    """A directed edge between two knowledge graph nodes.

    Attributes:
        source_id: Identifier of the source node.
        target_id: Identifier of the target node.
        relation_type: Type of the edge.
        confidence: Confidence score in the range [0, 1].
        evidence: List of citation identifiers supporting the relation.
        created_at: ISO-8601 creation timestamp.
    """

    source_id: str
    target_id: str
    relation_type: RelationType
    confidence: float = 1.0
    evidence: list[str] = field(default_factory=list)
    created_at: str = ""

    def reverse(self) -> "Relation":
        """Return the bidirectional counterpart of this relation.

        The source and target are swapped and the relation type is mapped to
        its counterpart via ``REVERSE_MAP``.
        """
        return Relation(
            source_id=self.target_id,
            target_id=self.source_id,
            relation_type=REVERSE_MAP.get(self.relation_type, self.relation_type),
            confidence=self.confidence,
            evidence=list(self.evidence),
            created_at=self.created_at,
        )
