"""Dual-path relation inference engine (RelationInference).

Routes each candidate relation through a confidence gate:

- High LLM confidence (>= threshold): semantic path. The relation is accepted
  as an LLM prior (LLM_INFERRED), then CitationBacker automatically searches
  local corpus text for supporting evidence. If supporting evidence is found,
  the relation's traceability is upgraded to CITATION_BACKED.
- Low LLM confidence (< threshold): corpus path. The relation is derived
  directly from local corpus evidence (CORPUS_DERIVED); confidence is computed
  from the quantity and grade of supporting evidence rather than the LLM prior.

This completes the dual-path relation inference: familiar entities are backed
by the LLM's semantic layer plus automated citation retrieval, while novel
entities are grounded purely in explicit corpus text.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from kg_pdg.core.citation_backer import CitationBacker, Evidence
from kg_pdg.models.relation import Relation, RelationType


class Traceability(str, Enum):
    """How a relation's existence is grounded.

    LLM_INFERRED: accepted from the LLM's semantic prior, no corpus anchor.
    CITATION_BACKED: LLM prior confirmed by automated corpus citation backing.
    CORPUS_DERIVED: derived directly from explicit corpus text evidence.
    """

    LLM_INFERRED = "LLM_INFERRED"
    CITATION_BACKED = "CITATION_BACKED"
    CORPUS_DERIVED = "CORPUS_DERIVED"


@dataclass
class InferenceResult:
    """Outcome of running one relation through the inference gate.

    Attributes:
        relation: The accepted Relation, or None when the corpus path found
            no supporting evidence.
        traceability: How the relation is grounded.
        evidence: Sentence-level evidence located by CitationBacker.
        confidence: Final confidence of the relation.
    """

    relation: Relation | None
    traceability: Traceability
    evidence: list[Evidence] = field(default_factory=list)
    confidence: float = 0.0


class RelationInference:
    """Dual-path relation inference with a confidence gate."""

    def __init__(
        self,
        backer: CitationBacker,
        confidence_threshold: float = 0.7,
    ) -> None:
        self.backer = backer
        self.confidence_threshold = confidence_threshold

    def infer(
        self,
        source: str,
        target: str,
        relation_type: RelationType,
        llm_confidence: float,
    ) -> InferenceResult:
        """Run one candidate relation through the confidence gate."""
        if llm_confidence >= self.confidence_threshold:
            return self._semantic_path(
                source, target, relation_type, llm_confidence
            )
        return self._corpus_path(source, target, relation_type)

    # ------------------------------------------------------------------ #
    # Semantic path: LLM prior, upgraded by citation backing.
    # ------------------------------------------------------------------ #
    def _semantic_path(
        self,
        source: str,
        target: str,
        relation_type: RelationType,
        llm_confidence: float,
    ) -> InferenceResult:
        relation = Relation(
            source_id=source,
            target_id=target,
            relation_type=relation_type,
            confidence=llm_confidence,
        )
        evidence = self.backer.back(source, target, relation_type)
        supporting = [ev for ev in evidence if ev.direction == "SUPPORT"]
        if supporting:
            relation.evidence = [ev.source for ev in supporting]
            return InferenceResult(
                relation=relation,
                traceability=Traceability.CITATION_BACKED,
                evidence=evidence,
                confidence=llm_confidence,
            )
        return InferenceResult(
            relation=relation,
            traceability=Traceability.LLM_INFERRED,
            evidence=evidence,
            confidence=llm_confidence,
        )

    # ------------------------------------------------------------------ #
    # Corpus path: evidence-driven derivation for novel / low-confidence.
    # ------------------------------------------------------------------ #
    def _corpus_path(
        self,
        source: str,
        target: str,
        relation_type: RelationType,
    ) -> InferenceResult:
        evidence = self.backer.back(source, target, relation_type)
        supporting = [ev for ev in evidence if ev.direction == "SUPPORT"]
        if not supporting:
            return InferenceResult(
                relation=None,
                traceability=Traceability.CORPUS_DERIVED,
                evidence=evidence,
                confidence=0.0,
            )
        confidence = self._derive_confidence(supporting)
        relation = Relation(
            source_id=source,
            target_id=target,
            relation_type=relation_type,
            confidence=confidence,
            evidence=[ev.source for ev in supporting],
        )
        return InferenceResult(
            relation=relation,
            traceability=Traceability.CORPUS_DERIVED,
            evidence=supporting,
            confidence=confidence,
        )

    @staticmethod
    def _derive_confidence(supporting: list[Evidence]) -> float:
        """Compute confidence from the quantity and grade of evidence."""
        base = 0.4
        base += 0.1 * min(len(supporting), 5)
        if any(ev.grade == "GUIDELINE" for ev in supporting):
            base += 0.1
        if any(ev.grade == "TRIAL" for ev in supporting):
            base += 0.1
        return round(min(base, 0.95), 2)
