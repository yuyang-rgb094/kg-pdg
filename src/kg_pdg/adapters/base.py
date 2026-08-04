"""Abstract base adapter defining the domain adaptation interface.

A domain adapter supplies the domain-specific configuration (knowledge types,
evidence levels, meta-path template, literature sources, granularity
triggers) and the domain-specific behaviour (question parsing, search-query
formatting, evidence grading, depth standards) that the generic phase engines
rely on.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from kg_pdg.models.evidence import EvidenceLevel
from kg_pdg.models.gap import MetaPath


class BaseAdapter(ABC):
    """Abstract base class for domain adapters."""

    # Domain-specific knowledge type classification.
    knowledge_types: dict = {}
    # Domain-specific evidence hierarchy.
    evidence_levels: list = []
    # Domain-specific reasoning chain (slot names).
    meta_path_template: list[str] = []
    # Domain-specific literature databases.
    literature_sources: list[str] = []
    # Domain-specific complexity thresholds.
    granularity_triggers: dict = {}

    @abstractmethod
    def parse_question(self, nl_question: str) -> MetaPath:
        """Map a natural-language question to a domain MetaPath instance."""
        raise NotImplementedError

    @abstractmethod
    def format_search_query(self, entity_desc: str) -> str:
        """Format an entity description into a literature search query."""
        raise NotImplementedError

    @abstractmethod
    def grade_evidence(self, paper: dict) -> EvidenceLevel:
        """Grade a retrieved paper into an EvidenceLevel."""
        raise NotImplementedError

    @abstractmethod
    def get_depth_standard(self, knowledge_type) -> dict:
        """Return the domain depth standard for a knowledge type."""
        raise NotImplementedError
