"""Tests for the multi-dimensional trust scoring engine.

TrustScorer combines a provenance base score (EvidenceLevel + VenueType) with
integrity modifiers into a 0-100 trust score. These tests cover the base
scores, every modifier, the hard-zero rules, and the two real-world validation
cases (Lianhuaqingwen vs EPIC-HR) that motivated the design.
"""
from __future__ import annotations

import pytest

from kg_pdg.core.trust import TrustScorer
from kg_pdg.models.evidence import EvidenceLevel
from kg_pdg.models.source import RetractionStatus, SourceMetadata, VenueType


@pytest.fixture
def scorer() -> TrustScorer:
    return TrustScorer()


class TestBaseScores:
    """Base score by provenance (EvidenceLevel + VenueType)."""

    def test_multicenter_rct_top_journal(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(
                venue_type=VenueType.TOP_JOURNAL,
                conflicts_disclosed=True,
            ),
        )
        assert result.base == 95
        assert result.score == 95

    def test_multicenter_rct_regular_journal(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(venue_type=VenueType.REGULAR_JOURNAL),
        )
        assert result.base == 90

    def test_consensus_below_guideline(self, scorer: TrustScorer):
        """Consensus must score clearly below guideline (the 江湖 correction)."""
        consensus = scorer.score(
            EvidenceLevel.L7_CONSENSUS,
            SourceMetadata(venue_type=VenueType.REGULAR_JOURNAL),
        )
        guideline = scorer.score(
            EvidenceLevel.L4_GUIDELINE,
            SourceMetadata(venue_type=VenueType.REGULAR_JOURNAL),
        )
        assert consensus.score < guideline.score
        assert consensus.base == 50
        assert guideline.base == 88

    def test_case_report_lowest(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L11_CASE_REPORT,
            SourceMetadata(venue_type=VenueType.REGULAR_JOURNAL),
        )
        assert result.base == 30

    def test_unknown_combination_falls_back(self, scorer: TrustScorer):
        """Missing (level, venue) combos fall back to a conservative default."""
        result = scorer.score(
            EvidenceLevel.L7_CONSENSUS,
            SourceMetadata(venue_type=VenueType.TOP_JOURNAL),
        )
        assert result.base == 50  # falls back to REGULAR_JOURNAL entry


class TestHardZero:
    """Irreversible disqualification rules."""

    def test_retracted_scores_zero(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(
                venue_type=VenueType.TOP_JOURNAL,
                retraction_status=RetractionStatus.RETRACTED,
            ),
        )
        assert result.score == 0.0
        assert "retracted" in result.flags

    def test_high_alert_journal_scores_zero(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(journal_warning="HIGH_ALERT"),
        )
        assert result.score == 0.0
        assert "high_alert" in result.flags


class TestIntegrityModifiers:
    """Each integrity red flag applies its penalty."""

    def test_undisclosed_coi(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(conflicts_disclosed=False),
        )
        assert ("UNDISCLOSED_COI", -20) in result.modifiers

    def test_expression_of_concern(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(has_expression_of_concern=True),
        )
        assert ("EXPRESSION_OF_CONCERN", -30) in result.modifiers

    def test_corrigendum(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(has_corrigendum=True),
        )
        assert ("CORRIGENDUM", -10) in result.modifiers

    def test_open_label(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(blinded=False),
        )
        assert ("OPEN_LABEL", -15) in result.modifiers

    def test_negative_objective_endpoint(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(objective_endpoint_positive=False),
        )
        assert ("NEGATIVE_OBJECTIVE_ENDPOINT", -10) in result.modifiers

    def test_high_self_citation(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(self_citation_ratio=0.4),
        )
        assert ("HIGH_SELF_CITATION", -10) in result.modifiers

    def test_citation_cartel(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(citation_clusters_detected=True),
        )
        assert ("CITATION_CARTEL", -15) in result.modifiers

    def test_low_alert_journal(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(journal_warning="LOW_ALERT"),
        )
        assert ("LOW_ALERT", -50) in result.modifiers


class TestSponsorRun:
    """Sponsor-run governance correction: -5 + verification flag."""

    def test_sponsor_run_penalty_and_flags(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(
                venue_type=VenueType.TOP_JOURNAL,
                conflicts_disclosed=True,
                sponsor_run=True,
            ),
        )
        assert ("SPONSOR_RUN", -5) in result.modifiers
        assert "sponsor_run" in result.flags
        assert "needs_independent_verification" in result.flags

    def test_sponsor_run_disclosed_no_coi_penalty(self, scorer: TrustScorer):
        """Disclosed sponsor-run must NOT also trigger the COI penalty."""
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(conflicts_disclosed=True, sponsor_run=True),
        )
        assert ("UNDISCLOSED_COI", -20) not in result.modifiers


class TestAgeDecay:
    """Recency decay differs by source type."""

    def test_textbook_decays_after_5_years(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L8_TEXTBOOK,
            SourceMetadata(publication_year=2015),
        )
        assert any(name == "AGE_DECAY" for name, _ in result.modifiers)

    def test_guideline_decays_after_3_years(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L4_GUIDELINE,
            SourceMetadata(publication_year=2020),
        )
        assert any(name == "AGE_DECAY" for name, _ in result.modifiers)

    def test_recent_rct_no_decay(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(publication_year=2024),
        )
        assert not any(name == "AGE_DECAY" for name, _ in result.modifiers)


class TestBounds:
    """Score is clamped to [0, 100]."""

    def test_floor_at_zero(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(
                conflicts_disclosed=False,
                has_expression_of_concern=True,
                has_corrigendum=True,
                blinded=False,
                objective_endpoint_positive=False,
                self_citation_ratio=0.5,
                citation_clusters_detected=True,
                journal_warning="LOW_ALERT",
            ),
        )
        assert result.score >= 0.0

    def test_ceiling_at_100(self, scorer: TrustScorer):
        result = scorer.score(
            EvidenceLevel.L1_SYSTEMATIC_REVIEW,
            SourceMetadata(
                venue_type=VenueType.TOP_JOURNAL,
                conflicts_disclosed=True,
                publication_year=2025,
            ),
        )
        assert result.score <= 100.0


class TestRealWorldValidation:
    """The two motivating papers must be correctly discriminated."""

    def test_lianhuaqingwen_scores_low(self, scorer: TrustScorer):
        """Conflicted open-label RCT with hidden COI and negative objective
        endpoint must score far below the naive 90 base."""
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(
                venue_type=VenueType.REGULAR_JOURNAL,  # Phytomedicine
                conflicts_disclosed=False,  # COI hidden until 2022 corrigendum
                has_corrigendum=True,
                blinded=False,  # open-label
                objective_endpoint_positive=False,  # viral conversion NS
                publication_year=2021,
            ),
        )
        assert result.score < 50
        assert ("UNDISCLOSED_COI", -20) in result.modifiers

    def test_epic_hr_scores_high(self, scorer: TrustScorer):
        """Clean double-blind top-journal RCT with disclosed COI scores high,
        but sponsor-run applies a small governance correction."""
        result = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(
                venue_type=VenueType.TOP_JOURNAL,  # NEJM
                conflicts_disclosed=True,  # "Supported by Pfizer"
                sponsor_run=True,  # all authors Pfizer employees
                blinded=True,  # double-blind
                objective_endpoint_positive=True,  # 89% RRR
                publication_year=2022,
            ),
        )
        assert result.score >= 85
        assert ("SPONSOR_RUN", -5) in result.modifiers
        assert "needs_independent_verification" in result.flags

    def test_same_level_different_trust(self, scorer: TrustScorer):
        """Both papers are L2_MULTICENTER_RCT yet must score very differently."""
        lianhua = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(
                venue_type=VenueType.REGULAR_JOURNAL,
                conflicts_disclosed=False,
                has_corrigendum=True,
                blinded=False,
                objective_endpoint_positive=False,
                publication_year=2021,
            ),
        )
        epic = scorer.score(
            EvidenceLevel.L2_MULTICENTER_RCT,
            SourceMetadata(
                venue_type=VenueType.TOP_JOURNAL,
                conflicts_disclosed=True,
                sponsor_run=True,
                blinded=True,
                objective_endpoint_positive=True,
                publication_year=2022,
            ),
        )
        assert epic.score - lianhua.score >= 40
