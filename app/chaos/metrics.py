"""Deterministic chaos metrics for topology graphs."""

from __future__ import annotations

import math
from collections import Counter
from typing import Iterable, Union

import networkx as nx

Edge = Union[tuple[str, str], tuple[str, str, str]]


def _build_graph(edges: Iterable[Edge]) -> nx.DiGraph:
    graph = nx.DiGraph()
    for edge in edges:
        if len(edge) >= 2:
            graph.add_edge(edge[0], edge[1])
    return graph


def calculate_entropy(edges: Iterable[Edge]) -> float:
    """Calculate Shannon entropy of node degree distribution."""
    graph = _build_graph(edges)
    if graph.number_of_nodes() == 0:
        return 0.0

    degrees = [degree for _, degree in graph.degree()]
    counts = Counter(degrees)
    total = sum(counts.values())
    entropy = -sum((count / total) * math.log2(count / total) for count in counts.values())
    return round(entropy, 6)


def calculate_instability(edges: Iterable[Edge]) -> float:
    """Estimate graph instability from cycles and density."""
    graph = _build_graph(edges)
    if graph.number_of_nodes() <= 1:
        return 0.0

    density = nx.density(graph)
    cycle_penalty = 1.0 if list(nx.simple_cycles(graph)) else 0.0
    weak_components = nx.number_weakly_connected_components(graph)
    fragmentation = max(0.0, (weak_components - 1) / graph.number_of_nodes())
    return round(min(1.0, (density * 0.5) + (cycle_penalty * 0.3) + (fragmentation * 0.2)), 6)


def calculate_complexity_score(edges: Iterable[Edge]) -> float:
    """Combine entropy, instability, and graph size into a normalized complexity score."""
    edge_list = list(edges)
    graph = _build_graph(edge_list)
    if graph.number_of_nodes() == 0:
        return 0.0

    entropy = calculate_entropy(edge_list)
    instability = calculate_instability(edge_list)
    size_factor = min(1.0, (graph.number_of_nodes() + graph.number_of_edges()) / 100)
    normalized_entropy = min(1.0, entropy / 4.0)
    return round(min(1.0, (normalized_entropy * 0.4) + (instability * 0.4) + (size_factor * 0.2)), 6)
