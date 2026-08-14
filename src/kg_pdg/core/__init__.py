"""Core package: pipeline and phase engines for KG-PDG."""
from kg_pdg.core.citation_backer import CitationBacker, Evidence, SearchQuery
from kg_pdg.core.complete import Complete
from kg_pdg.core.discovery import StructuralProbeDiscovery
from kg_pdg.core.inference import InferenceResult, RelationInference, Traceability
from kg_pdg.core.pipeline import Pipeline
from kg_pdg.core.probe import Probe
from kg_pdg.core.recall import Recall
from kg_pdg.core.trust import TrustResult, TrustScorer
from kg_pdg.core.verify import Verify

__all__ = [
    "Pipeline",
    "Probe",
    "Recall",
    "Complete",
    "Verify",
    "StructuralProbeDiscovery",
    "CitationBacker",
    "Evidence",
    "SearchQuery",
    "RelationInference",
    "InferenceResult",
    "Traceability",
    "TrustScorer",
    "TrustResult",
]
