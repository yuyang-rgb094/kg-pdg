"""Graph utility functions.

The graph is represented as a dict with two keys:

    {"entities": dict[str, Entity], "relations": list[Relation]}

All methods are static and operate on this structure.
"""
from __future__ import annotations

from collections import deque

from kg_pdg.models.entity import Entity
from kg_pdg.models.relation import Relation


class GraphUtils:
    """Static helpers for analysing a knowledge graph."""

    @staticmethod
    def _build_adjacency(graph: dict) -> dict[str, set[str]]:
        """Build an undirected adjacency map from the graph's relations."""
        entities: dict[str, Entity] = graph.get("entities", {})
        adjacency: dict[str, set[str]] = {eid: set() for eid in entities}
        relations: list[Relation] = graph.get("relations", [])
        for r in relations:
            adjacency.setdefault(r.source_id, set()).add(r.target_id)
            adjacency.setdefault(r.target_id, set()).add(r.source_id)
        return adjacency

    @staticmethod
    def shortest_path(graph: dict, source_id: str, target_id: str) -> int:
        """Return the BFS shortest path length (in hops) between two nodes.

        Returns 0 if source and target are identical, and -1 if no path exists
        or the source is not present in the graph.
        """
        if source_id == target_id:
            return 0
        adjacency = GraphUtils._build_adjacency(graph)
        if source_id not in adjacency:
            return -1
        visited = {source_id}
        queue = deque([(source_id, 0)])
        while queue:
            node, dist = queue.popleft()
            for neighbor in adjacency.get(node, set()):
                if neighbor == target_id:
                    return dist + 1
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, dist + 1))
        return -1

    @staticmethod
    def _bfs_path(
        adjacency: dict[str, set[str]], source: str, target: str
    ) -> list[str]:
        """Return one shortest path (as a node list) between source and target."""
        if source == target:
            return [source]
        visited = {source}
        queue = deque([(source, [source])])
        while queue:
            node, path = queue.popleft()
            for neighbor in adjacency.get(node, set()):
                if neighbor == target:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        return []

    @staticmethod
    def find_bridge_nodes(graph: dict) -> list[str]:
        """Find nodes with high betweenness centrality.

        Betweenness is approximated by counting how often a node appears on
        shortest paths between sampled pairs of nodes. Nodes whose score is at
        least half of the maximum observed score are returned as bridges.
        """
        entities: dict[str, Entity] = graph.get("entities", {})
        ids = list(entities.keys())
        if len(ids) < 3:
            return []
        adjacency = GraphUtils._build_adjacency(graph)
        betweenness: dict[str, int] = {eid: 0 for eid in ids}

        sample = ids[:50]
        for i, src in enumerate(sample):
            for tgt in sample[i + 1:]:
                path = GraphUtils._bfs_path(adjacency, src, tgt)
                for mid in path[1:-1]:
                    betweenness[mid] = betweenness.get(mid, 0) + 1

        max_score = max(betweenness.values()) if betweenness else 0
        if max_score <= 0:
            return []
        threshold = max_score / 2
        return sorted(n for n, b in betweenness.items() if b >= threshold)

    @staticmethod
    def detect_broken_links(graph: dict) -> list[tuple[str, str]]:
        """Find relations that are unidirectional (no reverse counterpart)."""
        relations: list[Relation] = graph.get("relations", [])
        directed = {(r.source_id, r.target_id) for r in relations}
        broken: list[tuple[str, str]] = []
        seen: set[tuple[str, str]] = set()
        for r in relations:
            a, b = r.source_id, r.target_id
            if (a, b) in seen or (b, a) in seen:
                continue
            seen.add((a, b))
            if (b, a) not in directed:
                broken.append((a, b))
        return broken

    @staticmethod
    def compute_coverage(graph: dict, source_id: str) -> float:
        """Compute the average coverage ratio of a source across the graph."""
        entities: dict[str, Entity] = graph.get("entities", {})
        referencing = [e for e in entities.values() if source_id in e.sources]
        if not referencing:
            return 0.0
        total_ratio = sum(e.coverage_ratio(source_id) for e in referencing)
        return total_ratio / len(referencing)

    @staticmethod
    def tier_classify(
        graph: dict, target_entity: str, max_distance: int = 3
    ) -> dict[str, list[str]]:
        """Classify nearby entities into tiers by graph distance.

        - Tier1:  distance 1 (direct neighbours)
        - Tier2a: distance 2
        - Tier2b: distance 3
        - Tier3:  distance > max_distance or unreachable
        """
        adjacency = GraphUtils._build_adjacency(graph)
        distances: dict[str, int] = {target_entity: 0}
        queue = deque([target_entity])
        while queue:
            node = queue.popleft()
            d = distances[node]
            if d >= max_distance:
                continue
            for neighbor in adjacency.get(node, set()):
                if neighbor not in distances:
                    distances[neighbor] = d + 1
                    queue.append(neighbor)

        tiers: dict[str, list[str]] = {
            "Tier1": [],
            "Tier2a": [],
            "Tier2b": [],
            "Tier3": [],
        }
        for eid, d in distances.items():
            if eid == target_entity:
                continue
            if d == 1:
                tiers["Tier1"].append(eid)
            elif d == 2:
                tiers["Tier2a"].append(eid)
            elif d == 3:
                tiers["Tier2b"].append(eid)
            else:
                tiers["Tier3"].append(eid)

        entities = graph.get("entities", {})
        for eid in entities:
            if eid not in distances and eid != target_entity:
                tiers["Tier3"].append(eid)
        return tiers
