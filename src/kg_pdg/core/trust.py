"""Multi-dimensional trust scoring for literature sources.

TrustScorer combines a provenance base score (derived from EvidenceLevel and
VenueType) with integrity modifiers (conflicts, retraction, blinding,
sponsor-run, spin, self-citation, citation cartel, age decay) into a single
0-100 trust score.

This is the anti-fraud / anti-"academic cliquishness" layer that the coarse
EvidenceLevel taxonomy cannot express. Two sources with the same
EvidenceLevel (e.g. L2_MULTICENTER_RCT) can receive very different trust
scores: a clean double-blind trial with disclosed conflicts scores high,
while a conflicted open-label trial with a negative objective endpoint and a
hidden corrigendum scores low.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from kg_pdg.models.evidence import EvidenceLevel
from kg_pdg.models.source import RetractionStatus, SourceMetadata, VenueType


@dataclass
class TrustResult:
    """Output of a trust-scoring run.

    Attributes:
        score: Final 0-100 trust score.
        base: Base score before modifiers.
        modifiers: List of (name, delta) tuples applied.
        flags: List of advisory flags (e.g. "sponsor_run",
            "needs_independent_verification").
    """

    score: float
    base: int
    modifiers: list[tuple[str, int]] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)


class TrustScorer:
    """Compute a 0-100 trust score from EvidenceLevel + SourceMetadata."""

    # Base score by (EvidenceLevel, VenueType). Missing combinations fall
    # back to the REGULAR_JOURNAL entry, then to a conservative default of 40.
    BASE_SCORES: dict[tuple[EvidenceLevel, VenueType], int] = {
        (EvidenceLevel.L1_SYSTEMATIC_REVIEW, VenueType.TOP_JOURNAL): 90,
        (EvidenceLevel.L1_SYSTEMATIC_REVIEW, VenueType.REGULAR_JOURNAL): 85,
        (EvidenceLevel.L2_MULTICENTER_RCT, VenueType.TOP_JOURNAL): 95,
        (EvidenceLevel.L2_MULTICENTER_RCT, VenueType.REGULAR_JOURNAL): 90,
        (EvidenceLevel.L3_SINGLE_CENTER_RCT, VenueType.TOP_JOURNAL): 85,
        (EvidenceLevel.L3_SINGLE_CENTER_RCT, VenueType.REGULAR_JOURNAL): 82,
        (EvidenceLevel.L4_GUIDELINE, VenueType.TOP_JOURNAL): 90,
        (EvidenceLevel.L4_GUIDELINE, VenueType.REGULAR_JOURNAL): 88,
        (EvidenceLevel.L5_MULTICENTER_COHORT, VenueType.TOP_JOURNAL): 82,
        (EvidenceLevel.L5_MULTICENTER_COHORT, VenueType.REGULAR_JOURNAL): 80,
        (EvidenceLevel.L6_SINGLE_CENTER_COHORT, VenueType.TOP_JOURNAL): 68,
        (EvidenceLevel.L6_SINGLE_CENTER_COHORT, VenueType.REGULAR_JOURNAL): 65,
        (EvidenceLevel.L7_CONSENSUS, VenueType.REGULAR_JOURNAL): 50,
        (EvidenceLevel.L8_TEXTBOOK, VenueType.REGULAR_JOURNAL): 60,
        (EvidenceLevel.L9_NARRATIVE_REVIEW, VenueType.REGULAR_JOURNAL): 45,
        (EvidenceLevel.L10_CASE_SERIES, VenueType.REGULAR_JOURNAL): 55,
        (EvidenceLevel.L11_CASE_REPORT, VenueType.REGULAR_JOURNAL): 30,
    }

    def score(
        self,
        evidence_level: EvidenceLevel,
        metadata: SourceMetadata | None = None,
    ) -> TrustResult:
        """Compute the trust score for an evidence level + metadata."""
        m = metadata or SourceMetadata()
        modifiers: list[tuple[str, int]] = []
        flags: list[str] = []

        # 1. Retraction -> hard zero (irreversible).
        if m.retraction_status == RetractionStatus.RETRACTED:
            return TrustResult(
                score=0.0,
                base=0,
                modifiers=[("RETRACTED", -100)],
                flags=["retracted"],
            )

        # 2. Base score from provenance.
        base = self.BASE_SCORES.get(
            (evidence_level, m.venue_type),
            self.BASE_SCORES.get((evidence_level, VenueType.REGULAR_JOURNAL), 40),
        )
        score = base

        # 3. Journal warning list.
        if m.journal_warning == "HIGH_ALERT":
            return TrustResult(
                score=0.0,
                base=base,
                modifiers=[("HIGH_ALERT", -100)],
                flags=["high_alert"],
            )
        if m.journal_warning == "LOW_ALERT":
            score -= 50
            modifiers.append(("LOW_ALERT", -50))

        # 4. Undisclosed conflict of interest.
        if not m.conflicts_disclosed:
            score -= 20
            modifiers.append(("UNDISCLOSED_COI", -20))

        # 5. Expression of concern.
        if m.has_expression_of_concern:
            score -= 30
            modifiers.append(("EXPRESSION_OF_CONCERN", -30))

        # 6. Corrigendum for governance issues.
        if m.has_corrigendum:
            score -= 10
            modifiers.append(("CORRIGENDUM", -10))

        # 7. Open-label design (subjective endpoints at risk).
        if not m.blinded:
            score -= 15
            modifiers.append(("OPEN_LABEL", -15))

        # 8. Negative objective endpoint (spin risk).
        if m.objective_endpoint_positive is False:
            score -= 10
            modifiers.append(("NEGATIVE_OBJECTIVE_ENDPOINT", -10))

        # 9. Sponsor-run governance correction: disclosed industry-run study.
        if m.sponsor_run:
            score -= 5
            modifiers.append(("SPONSOR_RUN", -5))
            flags.append("sponsor_run")
            flags.append("needs_independent_verification")

        # 10. Self-citation ratio.
        if m.self_citation_ratio and m.self_citation_ratio > 0.3:
            score -= 10
            modifiers.append(("HIGH_SELF_CITATION", -10))

        # 11. Citation cartel.
        if m.citation_clusters_detected:
            score -= 15
            modifiers.append(("CITATION_CARTEL", -15))

        # 12. Age decay.
        if m.publication_year:
            age = datetime.now().year - m.publication_year
            if evidence_level == EvidenceLevel.L8_TEXTBOOK and age > 5:
                d = 5 * (age // 5)
                score -= d
                modifiers.append(("AGE_DECAY", -d))
            elif evidence_level in (
                EvidenceLevel.L4_GUIDELINE,
                EvidenceLevel.L7_CONSENSUS,
            ) and age > 3:
                d = 10 * (age // 3)
                score -= d
                modifiers.append(("AGE_DECAY", -d))
            elif age > 5:
                d = 5 * (age // 5)
                score -= d
                modifiers.append(("AGE_DECAY", -d))

        return TrustResult(
            score=round(max(0.0, min(100.0, score)), 1),
            base=base,
            modifiers=modifiers,
            flags=flags,
        )
