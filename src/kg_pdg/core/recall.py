"""Phase 2: Recall.

Predicts what entities should exist based on the gap report, generates
literature search strategies across domain databases, ranks retrieved
papers by relevance to the gaps, and produces a recall report with a hit
rate.
"""
from __future__ import annotations

from kg_pdg.models.gap import GapReport


class Recall:
    """Phase 2 engine: predict -> search -> rank -> report."""

    def __init__(self, adapter=None) -> None:
        self.adapter = adapter

    def predict_missing_entities(self, gap_report: GapReport) -> list[dict]:
        """Predict what entities should exist based on the gap analysis."""
        predictions: list[dict] = []

        for desc in gap_report.missing_entities:
            slot, _, value = desc.partition(":")
            predictions.append(
                {
                    "slot": slot,
                    "description": desc,
                    "predicted_entity_type": slot,
                    "search_terms": [value] if value else [],
                }
            )

        for gap in gap_report.coverage_gaps:
            predictions.append(
                {
                    "slot": "coverage_expansion",
                    "description": (
                        f"Expand coverage for {gap['entity_id']} "
                        f"from source {gap['source_id']}"
                    ),
                    "predicted_entity_type": "coverage_expansion",
                    "search_terms": [gap["entity_id"], gap["source_id"]],
                }
            )

        return predictions

    def search_strategy(self, predictions: list[dict]) -> list[dict]:
        """Generate search queries for the configured literature databases."""
        sources = (
            self.adapter.literature_sources
            if self.adapter
            else ["PubMed", "arXiv", "Semantic Scholar"]
        )
        queries: list[dict] = []
        for pred in predictions:
            terms = [t for t in pred.get("search_terms", []) if t]
            base = " ".join(terms)
            for src in sources:
                queries.append(
                    {
                        "query": base,
                        "source": src,
                        "target_slot": pred.get("slot"),
                        "description": pred.get("description"),
                    }
                )
        return queries

    def rank_results(self, results: list[dict], gap_report: GapReport) -> list[dict]:
        """Rank retrieved papers by relevance to the identified gaps."""
        gap_terms: set[str] = set()
        for desc in gap_report.missing_entities:
            gap_terms.update(part for part in desc.lower().split(":") if part)
        for gap in gap_report.coverage_gaps:
            gap_terms.add(str(gap.get("entity_id", "")).lower())
            gap_terms.add(str(gap.get("source_id", "")).lower())

        def score(item: dict) -> float:
            text = (
                str(item.get("query", ""))
                + " "
                + str(item.get("title", ""))
                + " "
                + str(item.get("abstract", ""))
            ).lower()
            hits = sum(1 for term in gap_terms if term and term in text)
            return hits + float(item.get("relevance", 0.0))

        return sorted(results, key=score, reverse=True)

    def generate_recall_report(self, results: list[dict]) -> dict:
        """Produce a recall report including the hit rate."""
        total = len(results)
        relevant = sum(1 for r in results if float(r.get("relevance", 0.0)) > 0)
        hit_rate = relevant / total if total else 0.0
        return {
            "total_queries": total,
            "relevant_results": relevant,
            "hit_rate": hit_rate,
            "top_results": results[:10],
        }
