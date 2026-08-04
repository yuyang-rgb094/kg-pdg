"""Citation network utilities.

A citation network is built from a list of paper dicts. Each paper is
expected to expose a ``doi`` (or ``id``) key and an optional ``references``
list of cited DOIs. The resulting network is a dict with ``nodes`` (doi ->
paper) and ``edges`` (list of (citing_doi, cited_doi) pairs).
"""
from __future__ import annotations

from collections import deque


class CitationUtils:
    """Static helpers for building and analysing citation networks."""

    @staticmethod
    def build_citation_network(papers: list[dict]) -> dict:
        """Build a citation graph from a list of papers.

        Edges are directed as (citing_doi, cited_doi).
        """
        network: dict[str, dict] = {"nodes": {}, "edges": []}
        for paper in papers:
            doi = paper.get("doi") or paper.get("id")
            if not doi:
                continue
            network["nodes"][doi] = paper

        node_dois = set(network["nodes"])
        edges: set[tuple[str, str]] = set()
        for paper in papers:
            doi = paper.get("doi") or paper.get("id")
            for ref in paper.get("references", []):
                if ref in node_dois and ref != doi:
                    edges.add((doi, ref))
        network["edges"] = list(edges)
        return network

    @staticmethod
    def find_citation_path(
        network: dict, source_doi: str, target_doi: str
    ) -> list[str]:
        """Find the shortest citation path between two DOIs.

        Returns the path as a list of DOIs, or an empty list if none exists.
        """
        adjacency: dict[str, set[str]] = {}
        for a, b in network.get("edges", []):
            adjacency.setdefault(a, set()).add(b)
            adjacency.setdefault(b, set()).add(a)

        if source_doi == target_doi:
            return [source_doi]
        visited = {source_doi}
        queue = deque([(source_doi, [source_doi])])
        while queue:
            node, path = queue.popleft()
            for neighbor in adjacency.get(node, set()):
                if neighbor == target_doi:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []

    @staticmethod
    def identify_precursor(paper: dict, network: dict) -> str:
        """Identify the technical precursor of a paper.

        The precursor is the most-cited reference (highest in-degree within the
        network) among the paper's references. Falls back to the first
        reference, or an empty string if there are none.
        """
        in_degree: dict[str, int] = {}
        for _a, b in network.get("edges", []):
            in_degree[b] = in_degree.get(b, 0) + 1

        refs = paper.get("references", [])
        best = None
        best_score = -1
        for ref in refs:
            score = in_degree.get(ref, 0)
            if score > best_score:
                best_score = score
                best = ref
        if best is not None:
            return best
        return refs[0] if refs else ""

    @staticmethod
    def trace_threshold_origin(concept: str, network: dict) -> list[str]:
        """Trace the origin chain of a threshold / standard concept.

        Locates the first node mentioning the concept and follows its
        references backward toward the root source. Returns the chain of DOIs
        from the mentioning paper to the oldest reachable reference.
        """
        nodes = network.get("nodes", {})
        directed: dict[str, set[str]] = {}
        for a, b in network.get("edges", []):
            directed.setdefault(a, set()).add(b)

        start = None
        for doi, paper in nodes.items():
            text = (
                str(paper.get("title", ""))
                + " "
                + str(paper.get("abstract", ""))
            ).lower()
            if concept.lower() in text:
                start = doi
                break
        if start is None:
            return []

        chain = [start]
        visited = {start}
        current = start
        while True:
            refs = directed.get(current, set())
            next_node = next((r for r in refs if r not in visited), None)
            if next_node is None:
                break
            chain.append(next_node)
            visited.add(next_node)
            current = next_node
            if len(chain) > 50:  # safety guard against cycles in the data
                break
        return chain
