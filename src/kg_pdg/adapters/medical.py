"""Medical domain adapter.

Implements the BaseAdapter interface for the medical / interventional
cardiology domain used by the Cardio-PCI knowledge base.
"""
from __future__ import annotations

from kg_pdg.adapters.base import BaseAdapter
from kg_pdg.models.evidence import EvidenceLevel, KnowledgeType
from kg_pdg.models.gap import MetaPath
from kg_pdg.models.source import RetractionStatus, SourceMetadata, VenueType


class MedicalAdapter(BaseAdapter):
    """Domain adapter for the medical (cardio-PCI) knowledge base."""

    knowledge_types = {
        KnowledgeType.A_CONCEPT: "Foundational concept / threshold definition",
        KnowledgeType.B_DIAGNOSIS: "Diagnostic criteria and imaging feature identification",
        KnowledgeType.C_OPERATION: "Operational procedure and intervention technique",
        KnowledgeType.D_DECISION: "Clinical decision and risk stratification logic",
        KnowledgeType.E_COMPLICATION: "Complication, adverse event, and management",
    }

    evidence_levels = [
        EvidenceLevel.L1_SYSTEMATIC_REVIEW,
        EvidenceLevel.L2_MULTICENTER_RCT,
        EvidenceLevel.L3_SINGLE_CENTER_RCT,
        EvidenceLevel.L4_GUIDELINE,
        EvidenceLevel.L5_MULTICENTER_COHORT,
        EvidenceLevel.L6_SINGLE_CENTER_COHORT,
        EvidenceLevel.L7_CONSENSUS,
        EvidenceLevel.L8_TEXTBOOK,
        EvidenceLevel.L9_NARRATIVE_REVIEW,
        EvidenceLevel.L10_CASE_SERIES,
        EvidenceLevel.L11_CASE_REPORT,
    ]

    meta_path_template = [
        "assessment_modality",
        "imaging_feature",
        "risk_stratification",
        "intervention",
        "outcome",
    ]

    literature_sources = [
        "PubMed",
        "ClinicalTrials.gov",
        "Semantic Scholar",
        "Cochrane",
    ]

    granularity_triggers = {
        "max_lines": 300,
        "single_source_ratio": 0.6,
        "complication_types": 3,
        "strategy_types": 3,
    }

    # Domain-specific depth standards (min sources + required content sections).
    _DEPTH_STANDARDS = {
        KnowledgeType.A_CONCEPT: {
            "min_sources": 2,
            "required_fields": ["definition", "threshold_value", "origin_reference"],
        },
        KnowledgeType.B_DIAGNOSIS: {
            "min_sources": 2,
            "required_fields": ["criteria", "sensitivity", "specificity"],
        },
        KnowledgeType.C_OPERATION: {
            "min_sources": 3,
            "required_fields": ["procedure", "indications", "contraindications"],
        },
        KnowledgeType.D_DECISION: {
            "min_sources": 3,
            "required_fields": ["decision_rule", "risk_factors", "outcome_measure"],
        },
        KnowledgeType.E_COMPLICATION: {
            "min_sources": 2,
            "required_fields": ["complication", "incidence", "management"],
        },
    }

    # Keyword heuristics for mapping medical questions to meta-path slots.
    _SLOT_KEYWORDS = {
        "assessment_modality": [
            "oct", "ivus", "ct", "mri", "ultrasound",
            "angiography", "imaging", "modality",
        ],
        "imaging_feature": [
            "plaque", "calcification", "stenosis", "morphology", "feature",
            "finding",
        ],
        "risk_stratification": [
            "risk", "score", "stratification", "classification", "vulnerable",
        ],
        "intervention": [
            "stent", "pci", "procedure", "treatment", "intervention", "surgery",
        ],
        "outcome": [
            "mace", "mortality", "prognosis", "outcome", "survival", "endpoint",
        ],
    }

    def parse_question(self, nl_question: str) -> MetaPath:
        """Map a medical natural-language question to a MetaPath."""
        q = nl_question.lower()
        slots: dict[str, str] = {}
        for slot, keywords in self._SLOT_KEYWORDS.items():
            for kw in keywords:
                if kw in q:
                    slots[slot] = kw
                    break
        return MetaPath(
            modality=slots.get("assessment_modality", ""),
            feature=slots.get("imaging_feature", ""),
            risk_stratification=slots.get("risk_stratification", ""),
            intervention=slots.get("intervention", ""),
            outcome=slots.get("outcome", ""),
        )

    def format_search_query(self, entity_desc: str) -> str:
        """Format an entity description as a PubMed-style boolean query."""
        terms = [t for t in entity_desc.replace(":", " ").split() if t]
        return " AND ".join(terms) if terms else entity_desc

    def grade_evidence(self, paper: dict) -> EvidenceLevel:
        """Grade a paper into an EvidenceLevel from its publication type.

        This is a provenance classification only: it maps the publication
        type to the study-design taxonomy. Quality and integrity are scored
        separately via ``build_source_metadata`` + TrustScorer.
        """
        pub_type = (paper.get("publication_type") or "").lower()
        if "textbook" in pub_type:
            return EvidenceLevel.L8_TEXTBOOK
        if "meta-analysis" in pub_type or "systematic review" in pub_type:
            return EvidenceLevel.L1_SYSTEMATIC_REVIEW
        if "randomized" in pub_type or "rct" in pub_type:
            return EvidenceLevel.L2_MULTICENTER_RCT
        if "guideline" in pub_type:
            return EvidenceLevel.L4_GUIDELINE
        if "consensus" in pub_type:
            return EvidenceLevel.L7_CONSENSUS
        if "case series" in pub_type:
            return EvidenceLevel.L10_CASE_SERIES
        if "case report" in pub_type:
            return EvidenceLevel.L11_CASE_REPORT
        if "registry" in pub_type:
            return EvidenceLevel.L5_MULTICENTER_COHORT
        return EvidenceLevel.L6_SINGLE_CENTER_COHORT

    def build_source_metadata(self, paper: dict) -> SourceMetadata:
        """Build SourceMetadata from a paper dict for trust scoring.

        Reads integrity signals from the paper record. Missing keys fall back
        to neutral defaults (no penalty).
        """
        return SourceMetadata(
            venue_type=VenueType(paper.get("venue_type", "REGULAR_JOURNAL")),
            conflicts_disclosed=bool(paper.get("conflicts_disclosed", False)),
            retraction_status=RetractionStatus(
                paper.get("retraction_status", "NOT_RETRACTED")
            ),
            has_expression_of_concern=bool(
                paper.get("has_expression_of_concern", False)
            ),
            has_corrigendum=bool(paper.get("has_corrigendum", False)),
            sponsor_run=bool(paper.get("sponsor_run", False)),
            blinded=bool(paper.get("blinded", True)),
            objective_endpoint_positive=paper.get("objective_endpoint_positive"),
            self_citation_ratio=paper.get("self_citation_ratio"),
            citation_clusters_detected=bool(
                paper.get("citation_clusters_detected", False)
            ),
            publication_year=paper.get("publication_year"),
            journal_warning=paper.get("journal_warning"),
        )

    def get_depth_standard(self, knowledge_type) -> dict:
        """Return the medical depth standard for a knowledge type."""
        if isinstance(knowledge_type, str):
            try:
                knowledge_type = KnowledgeType(knowledge_type)
            except ValueError:
                return {}
        return self._DEPTH_STANDARDS.get(knowledge_type, {})
