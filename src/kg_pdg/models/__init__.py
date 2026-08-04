"""Models package: data structures for the KG-PDG framework.

Re-exports the core dataclasses and enums used across the framework so that
callers can import everything from ``kg_pdg.models``.
"""
from kg_pdg.models.entity import Entity
from kg_pdg.models.evidence import Evidence, EvidenceLevel, KnowledgeType
from kg_pdg.models.gap import GapReport, MetaPath
from kg_pdg.models.relation import Relation, RelationType

__all__ = [
    "Entity",
    "Relation",
    "RelationType",
    "Evidence",
    "EvidenceLevel",
    "KnowledgeType",
    "GapReport",
    "MetaPath",
]
