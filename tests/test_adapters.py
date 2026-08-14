"""Tests for domain adapters."""

from __future__ import annotations

import pytest

from kg_pdg.adapters.base import BaseAdapter
from kg_pdg.adapters.medical import MedicalAdapter
from kg_pdg.models.evidence import EvidenceLevel, KnowledgeType
from kg_pdg.models.gap import MetaPath


@pytest.fixture
def medical_adapter() -> MedicalAdapter:
    return MedicalAdapter()


class TestMedicalAdapter:
    """Tests for the medical domain adapter."""

    def test_implements_base_adapter(self, medical_adapter: MedicalAdapter):
        assert isinstance(medical_adapter, BaseAdapter)

    def test_has_five_knowledge_types(self, medical_adapter: MedicalAdapter):
        assert len(medical_adapter.knowledge_types) == 5
        assert KnowledgeType.A_CONCEPT in medical_adapter.knowledge_types
        assert KnowledgeType.E_COMPLICATION in medical_adapter.knowledge_types

    def test_has_eleven_evidence_levels(self, medical_adapter: MedicalAdapter):
        assert len(medical_adapter.evidence_levels) == 11

    def test_has_five_node_meta_path(self, medical_adapter: MedicalAdapter):
        assert len(medical_adapter.meta_path_template) == 5
        assert medical_adapter.meta_path_template[0] == "assessment_modality"
        assert medical_adapter.meta_path_template[-1] == "outcome"

    def test_has_medical_literature_sources(self, medical_adapter: MedicalAdapter):
        assert "PubMed" in medical_adapter.literature_sources
        assert "ClinicalTrials.gov" in medical_adapter.literature_sources
        assert "Cochrane" in medical_adapter.literature_sources

    def test_granularity_triggers(self, medical_adapter: MedicalAdapter):
        triggers = medical_adapter.granularity_triggers
        assert triggers["max_lines"] == 300
        assert triggers["single_source_ratio"] == 0.6
        assert triggers["complication_types"] == 3


class TestMedicalParseQuestion:
    """Tests for medical question parsing."""

    def test_parses_oct_question(self, medical_adapter: MedicalAdapter):
        mp = medical_adapter.parse_question(
            "What is the latest OCT research on plaque risk?"
        )
        assert mp.modality == "oct"
        assert mp.feature == "plaque"
        assert mp.risk_stratification == "risk"

    def test_parses_intervention_question(self, medical_adapter: MedicalAdapter):
        mp = medical_adapter.parse_question(
            "Does PCI with stent improve prognosis in TCFA patients?"
        )
        assert mp.intervention in ("pci", "stent")
        assert mp.outcome == "prognosis"

    def test_parses_empty_question(self, medical_adapter: MedicalAdapter):
        mp = medical_adapter.parse_question("")
        assert mp.modality == ""
        assert mp.feature == ""


class TestMedicalFormatSearchQuery:
    """Tests for medical search query formatting."""

    def test_formats_boolean_query(self, medical_adapter: MedicalAdapter):
        query = medical_adapter.format_search_query("OCT TCFA prognosis")
        assert "AND" in query

    def test_handles_colon_descriptions(self, medical_adapter: MedicalAdapter):
        query = medical_adapter.format_search_query("intervention:stent")
        assert "intervention" in query
        assert "stent" in query


class TestMedicalGradeEvidence:
    """Tests for medical evidence grading."""

    def test_grades_rct(self, medical_adapter: MedicalAdapter):
        paper = {"publication_type": "Randomized Controlled Trial"}
        level = medical_adapter.grade_evidence(paper)
        assert level == EvidenceLevel.L2_MULTICENTER_RCT

    def test_grades_guideline(self, medical_adapter: MedicalAdapter):
        paper = {"publication_type": "Clinical Practice Guideline"}
        level = medical_adapter.grade_evidence(paper)
        assert level == EvidenceLevel.L4_GUIDELINE

    def test_grades_consensus(self, medical_adapter: MedicalAdapter):
        paper = {"publication_type": "Expert Consensus"}
        level = medical_adapter.grade_evidence(paper)
        assert level == EvidenceLevel.L7_CONSENSUS

    def test_grades_meta_analysis(self, medical_adapter: MedicalAdapter):
        paper = {"publication_type": "Meta-Analysis"}
        level = medical_adapter.grade_evidence(paper)
        assert level == EvidenceLevel.L1_SYSTEMATIC_REVIEW

    def test_grades_textbook(self, medical_adapter: MedicalAdapter):
        paper = {"publication_type": "Textbook Chapter"}
        level = medical_adapter.grade_evidence(paper)
        assert level == EvidenceLevel.L8_TEXTBOOK

    def test_grades_registry(self, medical_adapter: MedicalAdapter):
        paper = {"publication_type": "Retrospective Registry"}
        level = medical_adapter.grade_evidence(paper)
        assert level == EvidenceLevel.L5_MULTICENTER_COHORT

    def test_grades_case_report(self, medical_adapter: MedicalAdapter):
        paper = {"publication_type": "Case Report"}
        level = medical_adapter.grade_evidence(paper)
        assert level == EvidenceLevel.L11_CASE_REPORT

    def test_grades_empty_type(self, medical_adapter: MedicalAdapter):
        paper = {}
        level = medical_adapter.grade_evidence(paper)
        assert level == EvidenceLevel.L6_SINGLE_CENTER_COHORT


class TestMedicalDepthStandard:
    """Tests for medical depth standards."""

    def test_concept_requires_two_sources(self, medical_adapter: MedicalAdapter):
        standard = medical_adapter.get_depth_standard(KnowledgeType.A_CONCEPT)
        assert standard["min_sources"] == 2

    def test_operation_requires_three_sources(self, medical_adapter: MedicalAdapter):
        standard = medical_adapter.get_depth_standard(KnowledgeType.C_OPERATION)
        assert standard["min_sources"] == 3

    def test_accepts_string_key(self, medical_adapter: MedicalAdapter):
        standard = medical_adapter.get_depth_standard("C_OPERATION")
        assert standard["min_sources"] == 3

    def test_unknown_type_returns_empty(self, medical_adapter: MedicalAdapter):
        standard = medical_adapter.get_depth_standard("NONEXISTENT")
        assert standard == {}
