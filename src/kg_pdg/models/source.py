"""Source metadata and integrity dimensions for trust scoring.

This module defines the data structures that capture a literature source's
publication channel (VenueType), retraction state (RetractionStatus), and its
integrity signals (conflict of interest, blinding, sponsor-run, self-citation,
citation cartel, etc.). These feed the TrustScorer in ``kg_pdg.core.trust``
to produce a 0-100 trust score that complements the coarse EvidenceLevel
provenance taxonomy.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class VenueType(str, Enum):
    """Publication channel of a source.

    TOP_JOURNAL: high-impact, highly selective venues (NEJM, Lancet, JAMA...).
    REGULAR_JOURNAL: standard peer-reviewed journals.
    PREDATORY: predatory / junk journals (paper mills, pay-to-publish).
    """

    TOP_JOURNAL = "TOP_JOURNAL"
    REGULAR_JOURNAL = "REGULAR_JOURNAL"
    PREDATORY = "PREDATORY"


class RetractionStatus(str, Enum):
    """Retraction state of a source."""

    NOT_RETRACTED = "NOT_RETRACTED"
    RETRACTED = "RETRACTED"
    PARTIAL_RETRACTION = "PARTIAL_RETRACTION"


@dataclass
class SourceMetadata:
    """Integrity metadata for a literature source.

    Attributes:
        venue_type: Publication channel (top / regular / predatory).
        conflicts_disclosed: Whether conflicts of interest are disclosed.
        retraction_status: Retraction state.
        has_expression_of_concern: Whether the journal issued an EoC.
        has_corrigendum: Whether a corrigendum / erratum was issued.
        sponsor_run: Whether the study was run entirely by the sponsor
            (e.g. all authors are sponsor employees) and conflicts are
            disclosed. Triggers a small governance correction and an
            "independent verification" flag.
        blinded: Whether the study was blinded (True) or open-label (False).
        objective_endpoint_positive: Whether the objective endpoint was
            positive. False flags a spin risk (subjective endpoints positive
            while objective endpoints are negative).
        self_citation_ratio: Author self-citation ratio in [0, 1].
        citation_clusters_detected: Whether citation-cartel clusters were found.
        publication_year: Year of publication (for age decay).
        journal_warning: Warning-list level, e.g. "HIGH_ALERT" / "LOW_ALERT".
    """

    venue_type: VenueType = VenueType.REGULAR_JOURNAL
    conflicts_disclosed: bool = False
    retraction_status: RetractionStatus = RetractionStatus.NOT_RETRACTED
    has_expression_of_concern: bool = False
    has_corrigendum: bool = False
    sponsor_run: bool = False
    blinded: bool = True
    objective_endpoint_positive: bool | None = None
    self_citation_ratio: float | None = None
    citation_clusters_detected: bool = False
    publication_year: int | None = None
    journal_warning: str | None = None
