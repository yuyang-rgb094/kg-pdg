"""Tests for the CitationBacker (automated citation-backing pipeline).

When the LLM inference gate emits a high-confidence relation, CitationBacker
automatically searches local corpus text for sentence-level evidence that
supports or refutes it, upgrading the relation's traceability from
LLM_INFERRED to CITATION_BACKED.
"""

from __future__ import annotations

import pytest

from kg_pdg.core.citation_backer import CitationBacker, Evidence, SearchQuery
from kg_pdg.models.relation import RelationType


class TestBuildQueries:
    """Query construction: synonym expansion + relation keyword mapping."""

    def test_expands_entity_synonyms(self):
        backer = CitationBacker()
        queries = backer.build_queries(
            "OCT", "IVUS", RelationType.COMPLEMENTARY_TO
        )
        assert len(queries) >= 1
        q = queries[0]
        assert "OCT" in q.source_terms
        assert "optical coherence tomography" in q.source_terms
        assert "IVUS" in q.target_terms
        assert "intravascular ultrasound" in q.target_terms

    def test_maps_relation_to_keywords(self):
        backer = CitationBacker()
        queries = backer.build_queries(
            "OCT", "IVUS", RelationType.COMPLEMENTARY_TO
        )
        assert "complementary" in queries[0].relation_keywords

    def test_unknown_entity_keeps_original_term(self):
        backer = CitationBacker()
        queries = backer.build_queries(
            "NovelConcept", "IVUS", RelationType.CITES
        )
        assert "NovelConcept" in queries[0].source_terms

    def test_contradicts_maps_to_dispute_keywords(self):
        backer = CitationBacker()
        queries = backer.build_queries(
            "TrialA", "TrialB", RelationType.CONTRADICTS
        )
        assert "contradicts" in queries[0].relation_keywords


class TestSearchLocal:
    """Local full-text search locating sentence-level evidence."""

    def test_finds_sentence_with_both_entities_and_keyword(self, tmp_path):
        corpus = tmp_path / "corpus"
        corpus.mkdir()
        (corpus / "oct_vs_ivus.txt").write_text(
            "OCT provides higher resolution than IVUS, whereas IVUS offers "
            "deeper penetration; the two modalities are complementary in PCI "
            "guidance. This is a common comparison in imaging."
        )
        backer = CitationBacker(corpus_dirs=[str(corpus)])
        queries = backer.build_queries(
            "OCT", "IVUS", RelationType.COMPLEMENTARY_TO
        )
        evidence = backer.search_local(queries)
        assert len(evidence) >= 1
        assert "OCT" in evidence[0].text
        assert "IVUS" in evidence[0].text
        assert evidence[0].source.endswith("oct_vs_ivus.txt")

    def test_returns_empty_when_no_matching_sentence(self, tmp_path):
        corpus = tmp_path / "corpus"
        corpus.mkdir()
        (corpus / "unrelated.txt").write_text(
            "Statins reduce LDL cholesterol in patients with coronary disease."
        )
        backer = CitationBacker(corpus_dirs=[str(corpus)])
        queries = backer.build_queries(
            "OCT", "IVUS", RelationType.COMPLEMENTARY_TO
        )
        assert backer.search_local(queries) == []

    def test_scans_multiple_files_in_corpus(self, tmp_path):
        corpus = tmp_path / "corpus"
        corpus.mkdir()
        (corpus / "a.txt").write_text("OCT versus IVUS in PCI guidance.")
        (corpus / "b.txt").write_text("No relevant content here.")
        backer = CitationBacker(corpus_dirs=[str(corpus)])
        queries = backer.build_queries(
            "OCT", "IVUS", RelationType.COMPLEMENTARY_TO
        )
        evidence = backer.search_local(queries)
        assert len(evidence) == 1
        assert evidence[0].source.endswith("a.txt")


class TestVerify:
    """Evidence direction: support vs refute vs neutral."""

    def test_marks_support_for_positive_evidence(self):
        backer = CitationBacker()
        ev = Evidence(
            source="x.txt",
            text="OCT and IVUS are complementary imaging modalities.",
        )
        assert backer.verify(ev, RelationType.COMPLEMENTARY_TO) == "SUPPORT"

    def test_marks_refute_for_contradicting_evidence(self):
        backer = CitationBacker()
        ev = Evidence(
            source="x.txt",
            text="However, IVUS is not complementary to OCT for this indication.",
        )
        assert backer.verify(ev, RelationType.COMPLEMENTARY_TO) == "REFUTE"


class TestGrade:
    """Evidence grading by source type."""

    def test_grade_guideline(self):
        backer = CitationBacker()
        assert backer.grade("_CN_OCT共识2023.md") == "GUIDELINE"

    def test_grade_trial(self):
        backer = CitationBacker()
        assert backer.grade("FAME_trial_2022.txt") == "TRIAL"

    def test_grade_textbook(self):
        backer = CitationBacker()
        assert backer.grade("topol_ch67_oct.txt") == "TEXTBOOK"

    def test_grade_unknown(self):
        backer = CitationBacker()
        assert backer.grade("random_file.txt") == "UNKNOWN"


class TestBack:
    """The back() entry point runs the full pipeline."""

    def test_back_returns_verified_and_graded_evidence(self, tmp_path):
        corpus = tmp_path / "corpus"
        corpus.mkdir()
        (corpus / "OCT_consensus_2023.md").write_text(
            "OCT and IVUS are complementary imaging modalities in PCI guidance."
        )
        backer = CitationBacker(corpus_dirs=[str(corpus)])
        evidence = backer.back("OCT", "IVUS", RelationType.COMPLEMENTARY_TO)
        assert len(evidence) == 1
        assert evidence[0].direction == "SUPPORT"
        assert evidence[0].grade == "GUIDELINE"

    def test_back_returns_empty_when_no_evidence(self, tmp_path):
        corpus = tmp_path / "corpus"
        corpus.mkdir()
        (corpus / "unrelated.txt").write_text(
            "Statins reduce LDL cholesterol."
        )
        backer = CitationBacker(corpus_dirs=[str(corpus)])
        evidence = backer.back("OCT", "IVUS", RelationType.COMPLEMENTARY_TO)
        assert evidence == []
