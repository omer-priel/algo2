# tests for edmonds blossom algo

import random

import networkx as nx


# utils
def data_to_graph(n: int, edges: list[tuple[int, int]], matching: list[set[int]] | None = None) -> tuple[nx.Graph, dict]:
    graph = nx.Graph()
    graph.add_nodes_from(list(range(n)))
    graph.add_edges_from(edges)

    if matching is None:
        return graph, {}
    return graph, {'matching': matching}


# tests
def test1():
    n = 6
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 4), (2, 5), (3, 4), (4, 5)]
    return [data_to_graph(n, edges)]


def test2():
    n = 17
    edges = [(0, 1), (1, 2), (1, 3), (3, 4), (3, 5), (5, 6), (3, 7), (7, 8), (7, 9),
             (9, 10), (7, 15), (15, 16), (7, 11), (11, 12), (11, 13), (13, 14)]
    return [data_to_graph(n, edges)]


def test3():
    n = 9
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (3, 5), (2, 6), (6, 7), (7, 8), (3, 8)]
    return [data_to_graph(n, edges)]


def test4():
    n = 9
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 6), (6, 2), (6, 7), (6, 8)]
    matching = [{1, 2}, {3, 4}, {5, 6}]
    return [data_to_graph(n, edges, matching)]


def test_from_random():
    graphs = [
        (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3)]),
        (6, [(0, 1), (0, 4), (0, 5), (1, 2), (2, 3), (3, 4), (3, 5)]),
        (8, [(0, 1), (0, 4), (0, 5), (1, 2), (2, 3), (3, 4), (3, 5), (0, 6), (3, 6), (0, 7), (3, 7)]),
        (5, [(0, 1), (0, 2), (0, 3), (0, 4), (1, 3), (2, 3), (3, 4)]),
        (10, [(0, 1), (0, 8), (0, 9), (1, 8), (1, 4), (1, 5), (1, 8), (1, 9), (8, 5), (4, 5), (5, 6), (5, 7), (6, 9), (7, 9), (8, 9)]),
        (10, [(0, 2), (0, 6), (0, 8), (1, 4), (1, 5), (1, 8), (2, 6), (2, 7), (2, 8), (2, 9), (3, 5), (4, 5), (4, 7), (5, 6), (5, 8), (6, 8)]),
        (11, [(0, 2), (0, 6), (0, 8), (1, 4), (1, 5), (1, 8), (2, 6), (2, 7), (2, 8), (2, 9), (3, 5), (4, 5), (4, 7), (5, 6), (5, 8), (6, 8)])
    ]
    return [data_to_graph(*data) for data in graphs]


def test_random_graphs(min_n: int, max_n: int, p: float, k_iter: int):
    tests_data = []

    for i_iter in range(k_iter):
        n = random.randint(min_n, max_n)
        edges = []
        for i in range(n):
            for j in range(i+1, n):
                if random.random() <= p:
                    edges.append((i, j))

        tests_data += [(n, edges)]

    return [data_to_graph(*data) for data in tests_data]
