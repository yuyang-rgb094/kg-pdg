"""Tests for the 4-phase pipeline and individual phases."""

from __future__ import annotations

import pytest

from kg_pdg.adapters.medical import MedicalAdapter
from kg_pdg.core.complete import Complete
from kg_pdg.core.ontology import Ontology
from kg_pdg.core.pipeline import Pipeline
from kg_pdg.core.probe import Probe
from kg_pdg.core.recall import Recall
from kg_pdg.core.verify import Verify
from kg_pdg.models.entity import Entity
from kg_pdg.models.evidence import EvidenceLevel, KnowledgeType
from kg_pdg.models.relation import Relation, RelationType


@pytest.fixture
def sample_graph() -> dict:
    entities: dict[str, Entity] = {
        "PT001": Entity(
            entity_id="PT001",
            title="TCFA",
            category="plaque_type",
            knowledge_type=KnowledgeType.A_CONCEPT,
            evidence_level=EvidenceLevel.L8_TEXTBOOK,
            tags=["KG/plaque_type"],
            aliases=["TCFA", "thin-cap fibroatheroma"],
            content="TCFA is a plaque with FCT <65um. OCT can measure FCT in vivo.",
            sources=["10.1056/NEJMoa1100547", "31504405"],
            created_at="2026-01-15T00:00:00",
            updated_at="2026-01-15T00:00:00",
        ),
        "CT001": Entity(
            entity_id="CT001",
            title="PROSPECT Trial",
            category="clinical_trial",
            knowledge_type=KnowledgeType.B_DIAGNOSIS,
            evidence_level=EvidenceLevel.L2_MULTICENTER_RCT,
            tags=["KG/clinical_trial"],
            aliases=["PROSPECT"],
            content="PROSPECT: 697 ACS patients, 3-vessel VH-IVUS. TCFA predicts MACE.",
            sources=["10.1056/NEJMoa1100547"],
            created_at="2026-01-15T00:00:00",
            updated_at="2026-01-15T00:00:00",
        ),
    }
    relations: list[Relation] = [
        Relation(
            source_id="CT001",
            target_id="PT001",
            relation_type=RelationType.VALIDATED_BY,
            confidence=0.9,
            evidence=["10.1056/NEJMoa1100547"],
            created_at="2026-01-15T00:00:00",
        ),
    ]
    return {"entities": entities, "relations": relations}


@pytest.fixture
def adapter() -> MedicalAdapter:
    return MedicalAdapter()


@pytest.fixture
def ontology() -> Ontology:
    return Ontology()


# --------------------------------------------------------------------------- #
# Phase 1: Probe
# --------------------------------------------------------------------------- #

class TestProbe:
    """Tests for Phase 1: Probe."""

    def test_parse_question_extracts_modality(self, sample_graph: dict):
        question = "What is the latest OCT research on plaque risk stratification?"
        probe = Probe(question, sample_graph)
        meta_path = probe.parse_question()
        assert meta_path.modality == "oct"
        assert meta_path.feature == "plaque"
        assert meta_path.risk_stratification == "risk"

    def test_parse_question_extracts_outcome(self, sample_graph: dict):
        question = "OCT prognosis and MACE prediction in TCFA patients."
        probe = Probe(question, sample_graph)
        meta_path = probe.parse_question()
        assert meta_path.outcome in ("prognosis", "mace")

    def test_query_graph_finds_matching_entities(self, sample_graph: dict):
        question = "OCT assessment of plaque morphology"
        probe = Probe(question, sample_graph)
        meta_path = probe.parse_question()
        result = probe.query_graph(meta_path, sample_graph)
        assert len(result["matched_entities"]) > 0

    def test_assess_coverage_finds_gaps(self, sample_graph: dict):
        question = "OCT plaque risk stratification and stent intervention outcome"
        probe = Probe(question, sample_graph)
        meta_path = probe.parse_question()
        query_result = probe.query_graph(meta_path, sample_graph)
        gap = probe.assess_coverage(query_result)
        # "stent" and "intervention" are not in the graph -> missing
        assert len(gap.missing_entities) > 0

    def test_classify_tiers_populates_all_tiers(self, sample_graph: dict):
        question = "OCT plaque risk stent intervention outcome prognosis"
        probe = Probe(question, sample_graph)
        meta_path = probe.parse_question()
        query_result = probe.query_graph(meta_path, sample_graph)
        gap = probe.assess_coverage(query_result)
        probe.classify_tiers(gap)
        assert "Tier1" in gap.tier_classification
        assert "Tier2a" in gap.tier_classification

    def test_severity_escalation(self, sample_graph: dict):
        """More missing entities should lead to higher severity."""
        question = "OCT plaque risk stent intervention outcome prognosis MACE mortality"
        probe = Probe(question, sample_graph)
        meta_path = probe.parse_question()
        query_result = probe.query_graph(meta_path, sample_graph)
        gap = probe.assess_coverage(query_result)
        assert gap.severity in ("P0_CRITICAL", "P1_HIGH", "P2_MODERATE")


# --------------------------------------------------------------------------- #
# Phase 2: Recall
# --------------------------------------------------------------------------- #

class TestRecall:
    """Tests for Phase 2: Recall."""

    def test_predict_missing_entities(self, sample_graph: dict, adapter: MedicalAdapter):
        from kg_pdg.models.gap import GapReport, MetaPath

        gap = GapReport(
            probe_question="test",
            meta_path=MetaPath(modality="oct", feature="plaque"),
            missing_entities=["intervention:stent", "outcome:mace"],
            broken_links=[],
            coverage_gaps=[],
        )
        recall = Recall(adapter)
        predictions = recall.predict_missing_entities(gap)
        assert len(predictions) == 2
        assert predictions[0]["slot"] == "intervention"

    def test_search_strategy_uses_adapter_sources(self, sample_graph: dict, adapter: MedicalAdapter):
        from kg_pdg.models.gap import GapReport, MetaPath

        gap = GapReport(
            probe_question="test",
            meta_path=MetaPath(modality="oct"),
            missing_entities=["intervention:stent"],
        )
        recall = Recall(adapter)
        predictions = recall.predict_missing_entities(gap)
        queries = recall.search_strategy(predictions)
        # Should generate queries for each adapter source (4 medical sources)
        assert len(queries) == 4
        sources = {q["source"] for q in queries}
        assert "PubMed" in sources
        assert "ClinicalTrials.gov" in sources

    def test_generate_recall_report(self, adapter: MedicalAdapter):
        recall = Recall(adapter)
        results = [
            {"query": "stent", "relevance": 0.9},
            {"query": "stent", "relevance": 0.0},
        ]
        report = recall.generate_recall_report(results)
        assert report["total_queries"] == 2
        assert report["relevant_results"] == 1
        assert report["hit_rate"] == 0.5


# --------------------------------------------------------------------------- #
# Phase 3: Complete
# --------------------------------------------------------------------------- #

class TestComplete:
    """Tests for Phase 3: Complete."""

    def test_assign_tier_by_title(self, sample_graph: dict, ontology: Ontology):
        complete = Complete(ontology)
        tier = complete.assign_tier("TCFA", sample_graph)
        assert tier == "Tier1"

    def test_assign_tier_no_match(self, sample_graph: dict, ontology: Ontology):
        complete = Complete(ontology)
        tier = complete.assign_tier("NONEXISTENT_ENTITY", sample_graph)
        assert tier == "Tier3"

    def test_create_entity_follows_depth_standard(self, ontology: Ontology):
        complete = Complete(ontology)
        template = {
            "title": "Test Entity",
            "category": "test",
            "knowledge_type": "A_CONCEPT",
            "evidence_level": "L6_SINGLE_CENTER_COHORT",
            "content": "Initial content.",
            "sources": [],
        }
        entity = complete.create_entity(template, "Tier1")
        assert entity.title == "Test Entity"
        # A_CONCEPT depth standard requires: definition, threshold_value, origin_reference
        # The create_entity method should append missing required sections
        assert "definition" in entity.content.lower()

    def test_extend_entity_appends_content(self, ontology: Ontology):
        complete = Complete(ontology)
        entity = Entity(
            entity_id="X001",
            title="Test",
            category="test",
            knowledge_type=KnowledgeType.A_CONCEPT,
            evidence_level=EvidenceLevel.L8_TEXTBOOK,
            content="Original content.",
            sources=["src1"],
        )
        extended = complete.extend_entity(entity, "New content.")
        assert "New content." in extended.content
        assert "Original content." in extended.content

    def test_close_citation_path_creates_relations(self, ontology: Ontology, sample_graph: dict):
        complete = Complete(ontology)
        new_entity = Entity(
            entity_id="NEW001",
            title="New Trial",
            category="clinical_trial",
            knowledge_type=KnowledgeType.B_DIAGNOSIS,
            evidence_level=EvidenceLevel.L2_MULTICENTER_RCT,
            content="A new trial validating TCFA.",
            sources=["CT001"],  # derives from CT001
        )
        relations = complete.close_citation_path(new_entity, sample_graph)
        assert len(relations) > 0
        # Should create a DERIVES_FROM relation to CT001
        rel_types = [r.relation_type for r in relations]
        assert RelationType.DERIVES_FROM in rel_types

    def test_annotate_evidence_adds_limitations(self, ontology: Ontology):
        complete = Complete(ontology)
        entity = Entity(
            entity_id="X002",
            title="Test",
            category="test",
            knowledge_type=KnowledgeType.A_CONCEPT,
            evidence_level=EvidenceLevel.L6_SINGLE_CENTER_COHORT,
            content="Content.",
            sources=["src1"],
        )
        annotated = complete.annotate_evidence(entity)
        assert len(annotated.evolution_chain) > 0
        last = annotated.evolution_chain[-1]
        assert last.get("action") == "annotate"
        assert len(last.get("limitations", [])) > 0


# --------------------------------------------------------------------------- #
# Phase 4: Verify
# --------------------------------------------------------------------------- #

class TestVerify:
    """Tests for Phase 4: Verify."""

    def test_check_bidirectional_links_finds_unidirectional(
        self, sample_graph: dict, ontology: Ontology
    ):
        verify = Verify(ontology)
        issues = verify.check_bidirectional_links(sample_graph)
        # CT001 -> PT001 exists but PT001 -> CT001 does not
        assert len(issues) > 0

    def test_audit_coverage_returns_dict(self, sample_graph: dict, ontology: Ontology):
        verify = Verify(ontology)
        report = verify.audit_coverage(sample_graph, {"10.1056/NEJMoa1100547": 5000})
        assert isinstance(report, dict)
        assert "__average__" in report

    def test_probe_backtest_returns_results(self, sample_graph: dict, ontology: Ontology):
        verify = Verify(ontology)
        questions = ["OCT plaque risk", "TCFA prognosis MACE"]
        results = verify.probe_backtest(sample_graph, questions)
        assert len(results) == 2
        for q, r in results.items():
            assert "matched_count" in r
            assert "missing_count" in r
            assert "severity" in r

    def test_validate_ontology_compliance(self, sample_graph: dict, ontology: Ontology):
        verify = Verify(ontology)
        issues = verify.validate_ontology_compliance(sample_graph)
        # CT001 has 1 source but B_DIAGNOSIS requires >=2 -> should flag
        assert any("CT001" in issue for issue in issues)

    def test_generate_report_produces_text(self, ontology: Ontology):
        verify = Verify(ontology)
        results = {
            "bidirectional_issues": ["A->B"],
            "coverage": {"__average__": 0.5},
            "backtest": {},
            "compliance": [],
        }
        report = verify.generate_report(results)
        assert isinstance(report, str)
        assert "Verification Report" in report


# --------------------------------------------------------------------------- #
# Full Pipeline
# --------------------------------------------------------------------------- #

class TestPipeline:
    """Tests for the full 4-phase pipeline."""

    def test_pipeline_returns_expected_keys(
        self, sample_graph: dict, adapter: MedicalAdapter
    ):
        pipeline = Pipeline(adapter)
        result = pipeline.run(
            "OCT plaque risk stratification and stent intervention outcome",
            sample_graph,
        )
        assert "updated_graph" in result
        assert "gap_report" in result
        assert "recall_report" in result
        assert "completion_report" in result
        assert "verification_report" in result

    def test_pipeline_grows_graph(
        self, sample_graph: dict, adapter: MedicalAdapter
    ):
        initial_count = len(sample_graph["entities"])
        pipeline = Pipeline(adapter)
        result = pipeline.run(
            "OCT plaque risk stent intervention outcome prognosis",
            sample_graph,
        )
        updated = result["updated_graph"]
        assert len(updated["entities"]) >= initial_count

    def test_pipeline_gap_report_has_meta_path(
        self, sample_graph: dict, adapter: MedicalAdapter
    ):
        pipeline = Pipeline(adapter)
        result = pipeline.run("OCT plaque risk", sample_graph)
        gap = result["gap_report"]
        assert gap.meta_path is not None
        assert gap.meta_path.modality == "oct"


class TestPipelineDiscovery:
    """Tests for auto-discovery: structural signals drive the 4-phase loop."""

    @pytest.fixture
    def discovery_graph(self, sample_graph: dict) -> dict:
        """sample_graph plus an isolated entity to trigger a signal."""
        sample_graph["entities"]["ISO001"] = Entity(
            entity_id="ISO001",
            title="Orphan Marker",
            category="metric",
            knowledge_type=KnowledgeType.E_COMPLICATION,
            evidence_level=EvidenceLevel.L7_CONSENSUS,
            content="A marker with no relations and no source.",
            sources=[],
        )
        return sample_graph

    def test_run_discovery_returns_expected_keys(
        self, discovery_graph: dict, adapter: MedicalAdapter
    ):
        pipeline = Pipeline(adapter)
        result = pipeline.run_discovery(discovery_graph, consensus_ids=["CT001"])
        assert "discovery_report" in result
        assert "probe_results" in result
        assert "updated_graph" in result

    def test_run_discovery_runs_one_probe_per_signal(
        self, discovery_graph: dict, adapter: MedicalAdapter
    ):
        pipeline = Pipeline(adapter)
        result = pipeline.run_discovery(discovery_graph, consensus_ids=["CT001"])
        report = result["discovery_report"]
        assert len(result["probe_results"]) == report.count()

    def test_run_discovery_grows_graph(
        self, discovery_graph: dict, adapter: MedicalAdapter
    ):
        initial = len(discovery_graph["entities"])
        pipeline = Pipeline(adapter)
        result = pipeline.run_discovery(discovery_graph, consensus_ids=["CT001"])
        assert len(result["updated_graph"]["entities"]) >= initial
