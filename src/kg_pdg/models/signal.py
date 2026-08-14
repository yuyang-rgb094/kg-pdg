"""Data structures for the probe-discovery engine.

A StructuralSignal captures a single structural gap found in a knowledge
graph, along with a templated probe question that can feed the KG-PDG
four-phase loop. A DiscoveryReport aggregates all signals from a scan.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class StructuralSignal:
    """A single structural gap that warrants a probe.

    Attributes:
        signal_type: One of ISOLATED_NODE, DEAD_END, UNSOURCED_FACT,
            UNCLOSED_CITATION.
        entity_id: Identifier of the entity involved.
        detail: Human-readable description of the gap.
        severity: One of P0_CRITICAL, P1_HIGH, P2_MODERATE, P3_LOW.
        suggested_probe: Templated probe question to feed the growth loop.
    """

    signal_type: str
    entity_id: str
    detail: str
    severity: str
    suggested_probe: str


@dataclass
class DiscoveryReport:
    """Aggregated result of a structural-signal scan."""

    signals: list[StructuralSignal] = field(default_factory=list)

    def count(self) -> int:
        """Return the total number of detected signals."""
        return len(self.signals)

    def by_type(self, signal_type: str) -> list[StructuralSignal]:
        """Return signals of a given type."""
        return [s for s in self.signals if s.signal_type == signal_type]
