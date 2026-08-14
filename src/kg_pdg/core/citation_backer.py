"""Automated citation-backing pipeline (CitationBacker).

When the LLM inference gate emits a high-confidence relation, CitationBacker
automatically searches local corpus text for sentence-level evidence that
supports or refutes it. This upgrades the relation's traceability from
LLM_INFERRED to CITATION_BACKED, giving the graph's edges a verifiable
evidence anchor without requiring manual literature lookup.

Pipeline: build_queries -> search_local -> verify -> grade -> back
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from kg_pdg.models.relation import RelationType


@dataclass
class SearchQuery:
    """A structured query for local corpus search.

    Attributes:
        source_terms: Synonym-expanded terms for the source entity.
        target_terms: Synonym-expanded terms for the target entity.
        relation_keywords: Keywords that signal the relation type in text.
    """

    source_terms: list[str]
    target_terms: list[str]
    relation_keywords: list[str]


@dataclass
class Evidence:
    """A sentence-level evidence item located in the corpus.

    Attributes:
        source: Corpus file / citation identifier the evidence came from.
        text: The sentence-level evidence text.
        direction: One of SUPPORT, REFUTE, NEUTRAL.
        grade: Evidence grade derived from the source type.
    """

    source: str
    text: str
    direction: str = "NEUTRAL"
    grade: str = "UNKNOWN"


# Default synonym table for common cardiovascular terms. Extensible by
# passing a custom table to CitationBacker.
_DEFAULT_SYNONYMS: dict[str, list[str]] = {
    "OCT": ["OCT", "optical coherence tomography"],
    "IVUS": ["IVUS", "intravascular ultrasound"],
    "FFR": ["FFR", "fractional flow reserve"],
    "TCFA": ["TCFA", "thin-cap fibroatheroma", "thin cap fibroatheroma"],
    "IVL": ["IVL", "intravascular lithotripsy"],
    "RA": ["rotational atherectomy"],
    "DCB": ["DCB", "drug-coated balloon"],
    "DES": ["DES", "drug-eluting stent"],
    "MACE": ["MACE", "major adverse cardiac events"],
    "ISR": ["ISR", "in-stent restenosis"],
}

# Mapping of relation type to text keywords that signal the relation.
_RELATION_KEYWORDS: dict[RelationType, list[str]] = {
    RelationType.COMPLEMENTARY_TO: [
        "complementary",
        "complement",
        "advantage",
        "limitation",
        "versus",
        "vs",
        "compared with",
        "comparison",
    ],
    RelationType.VALIDATED_BY: [
        "supports",
        "validated",
        "confirmed",
        "demonstrated",
        "showed",
    ],
    RelationType.EXTENDS: ["extends", "expands", "builds on", "based on"],
    RelationType.CONTRADICTS: [
        "contradicts",
        "challenges",
        "disputes",
        "in contrast",
    ],
    RelationType.CITES: ["cites", "references", "according to"],
    RelationType.DERIVES_FROM: ["derived from", "originates from"],
    RelationType.SOURCE_OF_THRESHOLD: ["threshold", "cutoff", "defined as"],
    RelationType.PRECURSOR_OF: ["precursor", "precedes", "prior to"],
}


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences on terminal punctuation."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _matches(sentence: str, query: SearchQuery) -> bool:
    """Return True if a sentence mentions both entities and a keyword."""
    lowered = sentence.lower()
    has_source = any(term.lower() in lowered for term in query.source_terms)
    has_target = any(term.lower() in lowered for term in query.target_terms)
    has_keyword = any(
        keyword.lower() in lowered for keyword in query.relation_keywords
    )
    return has_source and has_target and has_keyword


class CitationBacker:
    """Search local corpus text for evidence backing a relation."""

    def __init__(
        self,
        corpus_dirs: list[str] | None = None,
        synonyms: dict[str, list[str]] | None = None,
    ) -> None:
        self.corpus_dirs = corpus_dirs or []
        self.synonyms = {** _DEFAULT_SYNONYMS, **(synonyms or {})}

    def build_queries(
        self,
        source: str,
        target: str,
        relation_type: RelationType,
    ) -> list[SearchQuery]:
        """Build structured queries from a relation declaration.

        Entity names are expanded with synonyms; the relation type is mapped
        to text keywords that signal it. Returns one SearchQuery combining
        both expansions.
        """
        source_terms = self.synonyms.get(source.upper(), [source])
        target_terms = self.synonyms.get(target.upper(), [target])
        keywords = _RELATION_KEYWORDS.get(relation_type, [])
        return [
            SearchQuery(
                source_terms=source_terms,
                target_terms=target_terms,
                relation_keywords=keywords,
            )
        ]

    def search_local(self, queries: list[SearchQuery]) -> list[Evidence]:
        """Search local corpus files for sentence-level evidence.

        Scans every text file in the configured corpus directories, splits it
        into sentences, and keeps sentences that mention at least one source
        term, one target term, and one relation keyword.
        """
        evidence: list[Evidence] = []
        for corpus_dir in self.corpus_dirs:
            for path in sorted(Path(corpus_dir).rglob("*")):
                if not path.is_file() or path.suffix.lower() not in (
                    ".txt",
                    ".md",
                    ".xml",
                ):
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                for sentence in _split_sentences(text):
                    for query in queries:
                        if _matches(sentence, query):
                            evidence.append(
                                Evidence(source=str(path), text=sentence)
                            )
        return evidence

    def verify(self, evidence: Evidence, relation_type: RelationType) -> str:
        """Determine whether the evidence supports or refutes the relation.

        Uses keyword heuristics on the sentence text. Returns one of
        SUPPORT, REFUTE, or NEUTRAL.
        """
        lowered = evidence.text.lower()
        keywords = _RELATION_KEYWORDS.get(relation_type, [])
        negation = {"not", "no", "without", "lacks", "limitation", "cannot"}

        has_positive = any(kw in lowered for kw in keywords)
        has_negation = any(neg in lowered.split() for neg in negation)

        if has_positive and not has_negation:
            return "SUPPORT"
        if has_positive and has_negation:
            return "REFUTE"
        return "NEUTRAL"

    def grade(self, source: str) -> str:
        """Grade evidence by source type inferred from the file name.

        Returns one of GUIDELINE, TRIAL, TEXTBOOK, REVIEW, UNKNOWN.
        """
        lowered = source.lower()
        if any(k in lowered for k in ("guideline", "consensus", "共识", "指南")):
            return "GUIDELINE"
        if any(k in lowered for k in ("trial", "试验")):
            return "TRIAL"
        if any(k in lowered for k in ("textbook", "topol", "braunwald", "内科学")):
            return "TEXTBOOK"
        if any(k in lowered for k in ("review", "meta", "综述")):
            return "REVIEW"
        return "UNKNOWN"

    def back(
        self,
        source: str,
        target: str,
        relation_type: RelationType,
    ) -> list[Evidence]:
        """Run the full citation-backing pipeline for a relation.

        Builds queries, searches local corpus text, then verifies direction
        and grades each located evidence item.
        """
        queries = self.build_queries(source, target, relation_type)
        evidence = self.search_local(queries)
        for ev in evidence:
            ev.direction = self.verify(ev, relation_type)
            ev.grade = self.grade(ev.source)
        return evidence
