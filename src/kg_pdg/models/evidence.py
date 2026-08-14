"""Evidence and knowledge type enumerations for the KG-PDG framework.

This module defines the foundational enums used to classify knowledge along
the *depth* dimension (KnowledgeType) and the *provenance* dimension
(EvidenceLevel), as well as the Evidence dataclass that captures a single
supporting reference for a knowledge claim.

EvidenceLevel is a pure provenance taxonomy: it classifies WHAT KIND of source
the evidence is (systematic review, multicenter RCT, guideline, consensus,
textbook, ...). It is NOT a quality score. Quality and integrity are scored
separately by TrustScorer (``kg_pdg.core.trust``), which combines the
EvidenceLevel base score with integrity modifiers (conflicts, retraction,
blinding, sponsor-run, spin, self-citation, citation cartel, age decay).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from kg_pdg.models.source import SourceMetadata


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
    """Provenance taxonomy: what kind of source the evidence is.

    This is a pure classification of study design / source type, ordered from
    the most rigorous synthesis (L1) to the weakest evidence (L11). The same
    EvidenceLevel can carry very different trust scores: a conflicted
    open-label multicenter RCT and a clean double-blind one are both
    L2_MULTICENTER_RCT, but TrustScorer scores them very differently.
    """

    L1_SYSTEMATIC_REVIEW = "L1_SYSTEMATIC_REVIEW"
    L2_MULTICENTER_RCT = "L2_MULTICENTER_RCT"
    L3_SINGLE_CENTER_RCT = "L3_SINGLE_CENTER_RCT"
    L4_GUIDELINE = "L4_GUIDELINE"
    L5_MULTICENTER_COHORT = "L5_MULTICENTER_COHORT"
    L6_SINGLE_CENTER_COHORT = "L6_SINGLE_CENTER_COHORT"
    L7_CONSENSUS = "L7_CONSENSUS"
    L8_TEXTBOOK = "L8_TEXTBOOK"
    L9_NARRATIVE_REVIEW = "L9_NARRATIVE_REVIEW"
    L10_CASE_SERIES = "L10_CASE_SERIES"
    L11_CASE_REPORT = "L11_CASE_REPORT"


@dataclass
class Evidence:
    """A single piece of evidence supporting a knowledge claim.

    Attributes:
        claim: The factual statement being supported.
        source_id: Identifier (DOI / PMID / URL) of the originating source.
        evidence_level: Provenance level in the evidence taxonomy.
        source_metadata: Optional integrity metadata for trust scoring.
        trust_score: Optional 0-100 trust score computed by TrustScorer.
        grade_quality: Optional grading label (e.g. GRADE "High"/"Moderate").
        recommendation_class: Optional recommendation class (e.g. "Class I").
        confidence_interval: Optional confidence interval as a free-form string.
        limitations: List of acknowledged limitations of the evidence.
    """

    claim: str
    source_id: str
    evidence_level: EvidenceLevel
    source_metadata: SourceMetadata | None = None
    trust_score: float | None = None
    grade_quality: str | None = None
    recommendation_class: str | None = None
    confidence_interval: str | None = None
    limitations: list[str] = field(default_factory=list)
