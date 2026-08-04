"""Evidence and knowledge type enumerations for the KG-PDG framework.

This module defines the foundational enums used to classify knowledge along
the *depth* dimension (KnowledgeType) and the *evidence* dimension
(EvidenceLevel), as well as the Evidence dataclass that captures a single
supporting reference for a knowledge claim.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class KnowledgeType(str, Enum):
    """Classification of knowledge types along the depth dimension.

    The ordering A -> E reflects increasing operational specificity:
    A_CONCEPT is the most foundational (definitions / thresholds), while
    E_COMPLICATION is the most applied (complications and their management).
    """

    A_CONCEPT = "A_CONCEPT"
    B_DIAGNOSIS = "B_DIAGNOSIS"
    C_OPERATION = "C_OPERATION"
    D_DECISION = "D_DECISION"
    E_COMPLICATION = "E_COMPLICATION"


class EvidenceLevel(str, Enum):
    """Hierarchy of evidence levels.

    T0_TEXTBOOK is the most general/foundational, P2_REGISTRY the most
    applied/specific. The codes mirror the literature provenance taxonomy
    used throughout the framework.
    """

    T0_TEXTBOOK = "T0_TEXTBOOK"
    P1_CONSENSUS = "P1_CONSENSUS"
    P0_RCT = "P0_RCT"
    P2_REGISTRY = "P2_REGISTRY"


@dataclass
class Evidence:
    """A single piece of evidence supporting a knowledge claim.

    Attributes:
        claim: The factual statement being supported.
        source_id: Identifier (DOI / PMID / URL) of the originating source.
        evidence_level: Level in the evidence hierarchy.
        grade_quality: Optional grading label (e.g. GRADE "High"/"Moderate").
        recommendation_class: Optional recommendation class (e.g. "Class I").
        confidence_interval: Optional confidence interval as a free-form string.
        limitations: List of acknowledged limitations of the evidence.
    """

    claim: str
    source_id: str
    evidence_level: EvidenceLevel
    grade_quality: str | None = None
    recommendation_class: str | None = None
    confidence_interval: str | None = None
    limitations: list[str] = field(default_factory=list)
