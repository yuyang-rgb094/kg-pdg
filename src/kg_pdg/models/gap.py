"""Gap report and meta-path data structures.

A MetaPath is a concrete 5-node instantiation of the reasoning chain used to
probe a knowledge graph. A GapReport captures what the probe found to be
missing, broken, or under-covered.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class MetaPath:
    """A 5-node meta-path instance representing a reasoning chain.

    The nodes correspond to the ontology meta-path template:
    modality -> feature -> risk_stratification -> intervention -> outcome.
    Each node holds the (possibly empty) keyword/token extracted from the
    probe question for that slot.
    """

    modality: str = ""
    feature: str = ""
    risk_stratification: str = ""
    intervention: str = ""
    outcome: str = ""


@dataclass
class GapReport:
    """Report describing knowledge gaps identified during the Probe phase.

    Attributes:
        probe_question: The original natural-language probe question.
        meta_path: The MetaPath derived from the probe question.
        missing_entities: Descriptions of entities the meta-path expects but
            the graph does not contain.
        broken_links: (source_id, target_id) pairs that are connected in only
            one direction and therefore lack a bidirectional counterpart.
        coverage_gaps: Dictionaries describing entities whose coverage of a
            given source falls below the required threshold.
        tier_classification: Mapping of tier label -> list of entity
            descriptions, produced by Probe.classify_tiers.
        severity: One of P0_CRITICAL, P1_HIGH, P2_MODERATE, P3_LOW.
    """

    probe_question: str
    meta_path: MetaPath
    missing_entities: list[str] = field(default_factory=list)
    broken_links: list[tuple[str, str]] = field(default_factory=list)
    coverage_gaps: list[dict] = field(default_factory=list)
    tier_classification: dict[str, list[str]] = field(default_factory=dict)
    severity: str = "P3_LOW"
