# Checker for testing

import networkx as nx

from src.algo.tests.lib.edmonds_blossom import edmonds_blossom


def is_matching(graph: nx.Graph, matching: list[set[int]]) -> bool:
    vs = []
    for v, w in matching:
        if (not graph.has_edge(v, w)) or (v in vs) or (w in vs):
            return False
        vs.append(v)
        vs.append(w)

    return len(set(vs)) == 2 * len(matching)


def get_max_matching(graph: nx.Graph):
    edges = [tuple(e) for e in graph.edges()]
    n = len(list(graph.nodes()))

    matching = edmonds_blossom((list(range(n)), edges))

    if matching == "NICE":
        return (n - len(list(nx.isolates(graph)))) // 2

    return len(matching)
