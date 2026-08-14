"""Tests for the RelationInference dual-path relation inference engine.

Routes each candidate relation through a confidence gate:

- High LLM confidence (>= threshold): semantic path. The relation is accepted
  as an LLM prior (LLM_INFERRED), then CitationBacker automatically searches
  local corpus text for supporting evidence, upgrading traceability to
  CITATION_BACKED when evidence is found.
- Low LLM confidence (< threshold): corpus path. The relation is derived
  directly from local corpus evidence (CORPUS_DERIVED); confidence is computed
  from the quantity and grade of supporting evidence.
"""

from __future__ import annotations

import pytest

from kg_pdg.core.citation_backer import CitationBacker
from kg_pdg.core.inference import InferenceResult, RelationInference, Traceability
from kg_pdg.models.relation import RelationType


@pytest.fixture
def corpus_with_evidence(tmp_path):
    corpus = tmp_path / "corpus"
    corpus.mkdir()
    (corpus / "OCT_consensus_2023.md").write_text(
        "OCT and IVUS are complementary imaging modalities in PCI guidance."
    )
    (corpus / "unrelated.txt").write_text(
        "Statins reduce LDL cholesterol in coronary disease."
    )
    return str(corpus)


def make_backer(corpus_dir: str) -> CitationBacker:
    return CitationBacker(corpus_dirs=[corpus_dir])


class TestConfidenceGate:
    """The gate routes by LLM confidence vs the configured threshold."""

    def test_default_threshold_is_0_7(self):
        engine = RelationInference(backer=CitationBacker())
        assert engine.confidence_threshold == 0.7

    def test_high_confidence_takes_semantic_path(self, corpus_with_evidence):
        engine = RelationInference(backer=make_backer(corpus_with_evidence))
        result = engine.infer("OCT", "IVUS", RelationType.COMPLEMENTARY_TO, 0.9)
        assert result.traceability == Traceability.CITATION_BACKED

    def test_low_confidence_takes_corpus_path(self, corpus_with_evidence):
        engine = RelationInference(backer=make_backer(corpus_with_evidence))
        result = engine.infer("OCT", "IVUS", RelationType.COMPLEMENTARY_TO, 0.3)
        assert result.traceability == Traceability.CORPUS_DERIVED

    def test_exact_threshold_takes_semantic_path(self, corpus_with_evidence):
        engine = RelationInference(backer=make_backer(corpus_with_evidence))
        result = engine.infer("OCT", "IVUS", RelationType.COMPLEMENTARY_TO, 0.7)
        assert result.traceability == Traceability.CITATION_BACKED


class TestSemanticPath:
    """High-confidence LLM prior, upgraded by citation backing."""

    def test_supporting_evidence_upgrades_to_citation_backed(
        self, corpus_with_evidence
    ):
        engine = RelationInference(backer=make_backer(corpus_with_evidence))
        result = engine.infer("OCT", "IVUS", RelationType.COMPLEMENTARY_TO, 0.9)
        assert result.relation is not None
        assert result.relation.confidence == 0.9
        assert result.relation.evidence  # evidence sources attached
        assert result.evidence  # evidence objects returned

    def test_no_evidence_keeps_llm_inferred(self, tmp_path):
        corpus = tmp_path / "corpus"
        corpus.mkdir()
        (corpus / "unrelated.txt").write_text("Statins reduce LDL cholesterol.")
        engine = RelationInference(backer=make_backer(str(corpus)))
        result = engine.infer("OCT", "IVUS", RelationType.COMPLEMENTARY_TO, 0.9)
        assert result.traceability == Traceability.LLM_INFERRED
        assert result.relation is not None
        assert result.relation.evidence == []

    def test_refuting_evidence_keeps_llm_inferred(self, tmp_path):
        corpus = tmp_path / "corpus"
        corpus.mkdir()
        (corpus / "trial_x.txt").write_text(
            "However, IVUS is not complementary to OCT for this indication."
        )
        engine = RelationInference(backer=make_backer(str(corpus)))
        result = engine.infer("OCT", "IVUS", RelationType.COMPLEMENTARY_TO, 0.9)
        assert result.traceability == Traceability.LLM_INFERRED
        assert result.relation is not None

    def test_relation_preserves_type_and_direction(self, corpus_with_evidence):
        engine = RelationInference(backer=make_backer(corpus_with_evidence))
        result = engine.infer("OCT", "IVUS", RelationType.COMPLEMENTARY_TO, 0.9)
        assert result.relation.relation_type == RelationType.COMPLEMENTARY_TO
        assert result.relation.source_id == "OCT"
        assert result.relation.target_id == "IVUS"


class TestCorpusPath:
    """Low-confidence relations derived from corpus evidence."""

    def test_evidence_creates_relation(self, corpus_with_evidence):
        engine = RelationInference(backer=make_backer(corpus_with_evidence))
        result = engine.infer("OCT", "IVUS", RelationType.COMPLEMENTARY_TO, 0.3)
        assert result.relation is not None
        assert result.relation.evidence
        assert result.relation.confidence > 0.3  # corpus evidence boosts it

    def test_no_evidence_returns_no_relation(self, tmp_path):
        corpus = tmp_path / "corpus"
        corpus.mkdir()
        (corpus / "unrelated.txt").write_text("Statins reduce LDL cholesterol.")
        engine = RelationInference(backer=make_backer(str(corpus)))
        result = engine.infer("OCT", "IVUS", RelationType.COMPLEMENTARY_TO, 0.3)
        assert result.relation is None
        assert result.traceability == Traceability.CORPUS_DERIVED

    def test_more_evidence_yields_higher_confidence(self, tmp_path):
        corpus = tmp_path / "corpus"
        corpus.mkdir()
        (corpus / "a.md").write_text("OCT and IVUS are complementary in PCI guidance.")
        (corpus / "b.md").write_text("OCT complements IVUS for plaque assessment.")
        (corpus / "c.md").write_text("OCT and IVUS together improve stent optimization.")
        engine = RelationInference(backer=make_backer(str(corpus)))
        result = engine.infer("OCT", "IVUS", RelationType.COMPLEMENTARY_TO, 0.2)
        assert result.relation.confidence >= 0.6

    def test_guideline_grade_boosts_confidence(self, tmp_path):
        corpus = tmp_path / "corpus"
        corpus.mkdir()
        (corpus / "OCT_consensus_2023.md").write_text(
            "OCT and IVUS are complementary imaging modalities in PCI guidance."
        )
        engine = RelationInference(backer=make_backer(str(corpus)))
        result = engine.infer("OCT", "IVUS", RelationType.COMPLEMENTARY_TO, 0.2)
        assert result.relation.confidence >= 0.5
