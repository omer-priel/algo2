# tests for hungarian algo

import random

import networkx as nx


def test_random_graph(min_n: int, max_n: int, p: float, k: int) -> list[tuple[nx.Graph, dict]]:
    graphs = []

    for i in range(k):
        n = random.randint(min_n, max_n)
        m = random.randint(min_n, max_n)

        a = ["A" + str(i) for i in range(0, n)]
        b = ["B" + str(i) for i in range(0, m)]

        graph = nx.Graph()
        graph.add_nodes_from(a, bipartite=0)
        graph.add_nodes_from(b, bipartite=1)

        for v in a:
            for w in b:
                if random.random() < p:
                    graph.add_edge(v, w)

        graphs.append((graph, {}))

    return graphs
