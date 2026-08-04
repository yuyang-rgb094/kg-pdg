#!/usr/bin/env python3
"""
Example: Cardiovascular OCT Knowledge Graph
============================================
This example demonstrates the KG-PDG framework using a real cardiovascular
OCT (Optical Coherence Tomography) knowledge graph.

It reproduces the methodology from the 5-probe practice described in
docs/examples/medical-cardio-example.md.

Usage:
    python examples/cardio_kg_example.py
"""

from __future__ import annotations

from kg_pdg.adapters.medical import MedicalAdapter
from kg_pdg.core.pipeline import Pipeline
from kg_pdg.models.entity import Entity
from kg_pdg.models.evidence import EvidenceLevel, KnowledgeType
from kg_pdg.models.relation import Relation, RelationType


def build_sample_graph() -> dict:
    """Build a minimal cardiovascular KG with known gaps (simulating pre-probe state)."""
    entities: dict[str, Entity] = {}

    # --- Plaque Types ---
    entities["PT001"] = Entity(
        entity_id="PT001",
        title="TCFA (Thin-Cap Fibroatheroma)",
        category="plaque_type",
        knowledge_type=KnowledgeType.A_CONCEPT,
        evidence_level=EvidenceLevel.T0_TEXTBOOK,
        tags=["KG/plaque_type"],
        aliases=["TCFA", "thin-cap fibroatheroma"],
        content=(
            "TCFA is defined as a plaque with fibrous cap thickness <65um "
            "measured by histology (Virmani 2000). OCT can measure FCT in vivo "
            "with axial resolution ~10-20um. Threshold: FCT <65um (consensus) "
            "or <80um (some clinical trials).\n\n"
            "Key evidence: PROSPECT trial (2011) showed TCFA predicts MACE.\n"
            "CLIMA study (2020, Eur Heart J) identified 4 OCT predictors "
            "including FCT <75um."
        ),
        sources=["10.1016/S0735-1097(01)01617-3", "31504405"],
        created_at="2026-01-15T00:00:00",
        updated_at="2026-01-15T00:00:00",
        evolution_chain=[
            {"year": 2000, "event": "Virmani histological definition (65um)", "source": "10.1016/S0735-1097(01)01617-3"},
            {"year": 2012, "event": "Tearney consensus standardization", "source": "consensus"},
            {"year": 2020, "event": "CLIMA clinical threshold (75um)", "source": "31504405"},
        ],
    )

    entities["PT002"] = Entity(
        entity_id="PT002",
        title="Calcified Plaque",
        category="plaque_type",
        knowledge_type=KnowledgeType.A_CONCEPT,
        evidence_level=EvidenceLevel.T0_TEXTBOOK,
        tags=["KG/plaque_type"],
        aliases=["calcified nodule", "calcified plaque"],
        content="Calcified plaque with calcium deposits detectable by OCT as low-signal regions.",
        sources=["textbook"],
        created_at="2026-01-15T00:00:00",
        updated_at="2026-01-15T00:00:00",
    )

    # --- Clinical Trials (limited -- gaps will be found) ---
    entities["CT001"] = Entity(
        entity_id="CT001",
        title="PROSPECT Trial",
        category="clinical_trial",
        knowledge_type=KnowledgeType.B_DIAGNOSIS,
        evidence_level=EvidenceLevel.P0_RCT,
        tags=["KG/clinical_trial"],
        aliases=["PROSPECT"],
        content=(
            "PROSPECT (2011, NEJM): 697 ACS patients, 3-vessel VH-IVUS imaging. "
            "TCFA (FCT <65um), plaque burden >70%, and MLA <4.0mm2 predicted "
            "3-year MACE (HR 3.21, 11.8% vs 4.9%).\n"
            "DOI: 10.1056/NEJMoa1100547"
        ),
        sources=["10.1056/NEJMoa1100547"],
        created_at="2026-01-15T00:00:00",
        updated_at="2026-01-15T00:00:00",
    )

    entities["CT002"] = Entity(
        entity_id="CT002",
        title="CLIMA Study",
        category="clinical_trial",
        knowledge_type=KnowledgeType.B_DIAGNOSIS,
        evidence_level=EvidenceLevel.P0_RCT,
        tags=["KG/clinical_trial"],
        aliases=["CLIMA"],
        content=(
            "CLIMA (2020, Eur Heart J): 843 patients, OCT of non-culprit lesions. "
            "4 predictors of MACE: MLA <3.5mm2, FCT <75um, lipid arc >90, "
            "macrophages. FCT <75um HR=2.56.\n"
            "DOI: 10.1093/eurheartj/ehz520 | PMID: 31504405"
        ),
        sources=["10.1093/eurheartj/ehz520"],
        created_at="2026-01-15T00:00:00",
        updated_at="2026-01-15T00:00:00",
    )

    # NOTE: PECTUS-AI, PREVENT, VULNERABLE, COMBINE OCT-FFR are intentionally
    # missing -- the probe should detect these gaps.

    # --- Relations ---
    relations: list[Relation] = [
        Relation(
            source_id="CT001",
            target_id="PT001",
            relation_type=RelationType.VALIDATED_BY,
            confidence=0.9,
            evidence=["10.1056/NEJMoa1100547"],
            created_at="2026-01-15T00:00:00",
        ),
        Relation(
            source_id="CT002",
            target_id="PT001",
            relation_type=RelationType.VALIDATED_BY,
            confidence=0.85,
            evidence=["10.1093/eurheartj/ehz520"],
            created_at="2026-01-15T00:00:00",
        ),
    ]

    return {"entities": entities, "relations": relations}


def run_probe_5_simulation():
    """
    Simulate Probe #5: OCT assessment of diabetic TCFA prognosis.

    This probe asks: "What is the latest research on OCT assessment of
    prognostic risk in diabetic patients with TCFA lesions?"

    Expected gaps (from real practice):
    - Missing entities: PREVENT, PECTUS-AI, VULNERABLE, COMBINE OCT-FFR,
      AI-TCFA, Lipid-to-Cap Ratio, etc.
    - Broken links: No relation from TCFA to preventive PCI
    - Coverage gaps: TCFA entity lacks AI-based detection info
    """
    print("=" * 70)
    print("  KG-PDG Example: Cardiovascular OCT Knowledge Graph")
    print("  Probe #5: OCT + Diabetic TCFA Prognosis")
    print("=" * 70)
    print()

    # 1. Build sample graph (pre-probe state, 4 entities)
    graph = build_sample_graph()
    entity_count = len(graph["entities"])
    relation_count = len(graph["relations"])
    print(f"[Setup] Initial graph: {entity_count} entities, {relation_count} relations")
    print(f"  Entities: {', '.join(sorted(graph['entities'].keys()))}")
    print()

    # 2. Initialize pipeline with medical adapter
    adapter = MedicalAdapter()
    pipeline = Pipeline(adapter)

    # 3. Define the probe question
    question = (
        "What is the latest research on OCT assessment of prognostic risk "
        "in diabetic patients with TCFA lesions? Include PREVENT trial, "
        "PECTUS-AI study, and VULNERABLE trial."
    )
    print(f"[Probe] Question: {question}")
    print()

    # 4. Run the 4-phase pipeline
    print("[Pipeline] Running 4-phase loop...")
    print("-" * 70)
    result = pipeline.run(question, graph)
    print("-" * 70)
    print()

    # 5. Display results
    # NOTE: gap_report is a GapReport dataclass, not a dict
    gap = result.get("gap_report")
    if gap:
        print("[Phase 1: Probe]")
        mp = gap.meta_path
        print(f"  Meta-path: {mp.modality} -> {mp.feature} -> {mp.risk_stratification} -> {mp.intervention} -> {mp.outcome}")
        print(f"  Missing entities ({len(gap.missing_entities)}): {gap.missing_entities[:5]}")
        print(f"  Broken links: {len(gap.broken_links)}")
        print(f"  Coverage gaps: {len(gap.coverage_gaps)}")
        print(f"  Severity: {gap.severity}")
        for tier, items in gap.tier_classification.items():
            print(f"  {tier}: {len(items)} items")
    print()

    # recall_report is a dict
    recall = result.get("recall_report", {})
    print("[Phase 2: Recall]")
    print(f"  Total queries: {recall.get('total_queries', 0)}")
    print(f"  Relevant results: {recall.get('relevant_results', 0)}")
    print(f"  Hit rate: {recall.get('hit_rate', 0):.1%}")
    print()

    # completion_report is a string
    completion = result.get("completion_report", "")
    print("[Phase 3: Complete]")
    # Count new entities by comparing graph sizes
    updated_graph = result.get("updated_graph", graph)
    new_count = len(updated_graph.get("entities", {})) - entity_count
    print(f"  New entities created: {new_count}")
    print(f"  Total entities now: {len(updated_graph.get('entities', {}))}")
    print()

    # verification_report is a dict
    verify = result.get("verification_report", {})
    print("[Phase 4: Verify]")
    bi_issues = verify.get("bidirectional_issues", [])
    print(f"  Bidirectional link issues: {len(bi_issues)}")
    coverage = verify.get("coverage", {})
    avg_cov = coverage.get("__average__", 0.0) if isinstance(coverage, dict) else 0.0
    print(f"  Average coverage: {avg_cov:.1%}")
    backtest = verify.get("backtest", {})
    print(f"  Backtest questions: {len(backtest)}")
    compliance = verify.get("compliance", [])
    print(f"  Ontology compliance issues: {len(compliance)}")
    print()

    # 6. Summary
    final_count = len(updated_graph.get("entities", {}))
    growth = final_count - entity_count
    hit_rate = recall.get("hit_rate", 0)
    print("=" * 70)
    print(f"  Summary: {entity_count} -> {final_count} entities (+{growth})")
    print(f"  Hit rate: {hit_rate:.1%} | Severity: {gap.severity if gap else 'N/A'}")
    print("=" * 70)

    return result


def demonstrate_ontology():
    """Demonstrate the four-dimensional ontology framework."""
    print()
    print("=" * 70)
    print("  Ontology Framework Demonstration")
    print("=" * 70)
    print()

    from kg_pdg.core.ontology import Ontology

    onto = Ontology()

    # Knowledge types
    print("[Knowledge Types]")
    for kt, info in onto.KNOWLEDGE_TYPES.items():
        print(f"  {kt.value}: {info['description']}")
    print()

    # Evidence hierarchy
    print("[Evidence Hierarchy]")
    for level in onto.EVIDENCE_HIERARCHY:
        print(f"  {level.value}")
    print()

    # Meta-path template
    print("[Meta-Path Template]")
    print(f"  {' -> '.join(onto.META_PATH_TEMPLATE)}")
    print()

    # Relation types
    print("[Citation Network Relation Types]")
    for rtype, desc in onto.RELATION_TYPES.items():
        print(f"  {rtype}: {desc}")
    print()

    # Validate an entity
    entity = build_sample_graph()["entities"]["PT001"]
    errors = onto.validate_entity(entity)
    status = "None -- compliant" if not errors else errors
    print(f"[Entity Validation] PT001 errors: {status}")

    # Check granularity
    needs_split = onto.should_trigger_split(entity)
    print(f"[Granularity Check] PT001 needs split: {needs_split}")

    # Reverse reconstruction check
    should_restruct = onto.should_trigger_reverse_restruct(source_length=1200)
    print(f"[Reverse Restructuring] source_length=1200 -> trigger: {should_restruct}")


if __name__ == "__main__":
    result = run_probe_5_simulation()
    demonstrate_ontology()
