import random

import networkx as nx
import networkx.generators


# utils
def get_random_graph(n: int, p: float) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(list(range(n)))

    for v in range(n):
        for w in range(v + 1, n):
            if random.random() < p:
                graph.add_edge(v, w)

    return graph


def get_k_regular(n: int, k: int) -> nx.Graph:
    nodes = [0]
    graph = nx.Graph()
    while len(nodes) > 0:
        graph = networkx.generators.complete_graph(n)
        nodes = [node for (node, val) in graph.degree() if val > k]
        edges = [(v, w) for v in nodes for w in graph.neighbors(v) if w in nodes]
        while len(edges) > 0:
            random.shuffle(edges)
            graph.remove_edge(edges[0][0], edges[0][1])
            nodes = [node for (node, val) in graph.degree() if val > k]
            edges = [(v, w) for v in nodes for w in graph.neighbors(v) if w in nodes]

    return graph


# tests
def test_random_graphs(draw: bool, min_n: int, max_n: int, p: float, k_iter: int):
    graphs = []
    for i in range(k_iter):
        n = random.randint(min_n, max_n)

        graphs += [(get_random_graph(n, p), {'draw': draw})]

    return graphs


def test_2_degree_graph(draw: bool, min_n: int, max_n: int):
    n = random.randint(min_n, max_n)

    graph1 = nx.Graph()
    graph2 = nx.Graph()
    graph3 = nx.Graph()
    graph1.add_nodes_from(list(range(n)))
    graph2.add_nodes_from(list(range(n)))
    graph3.add_nodes_from(list(range(n + 1)))

    for v in range(n - 1):
        graph1.add_edge(v, v + 1)
        graph2.add_edge(v, v + 1)
        graph3.add_edge(v, v + 1)

    graph2.add_edge(0, n - 1)
    graph3.add_edge(0, n)
    graph3.add_edge(n - 1, n)

    return [(graph1, {'draw': draw}), (graph2, {'draw': draw}), (graph3, {'draw': draw})]


def test_full_connected_graph(draw: bool, min_n: int, max_n: int):
    n = random.randint(min_n, max_n)
    graph = networkx.generators.complete_graph(n)
    return [(graph, {'draw': draw})]


def test_k_regular(draw: bool, n: int, k: int, to_remove: int = 0):
    graph = get_k_regular(n, k)
    if to_remove > 0:
        edges = list(graph.edges)
        random.shuffle(edges)
        for v, w in edges[:to_remove]:
            graph.remove_edge(v, w)

    return [(graph, {'draw': draw})]


def test_k_regular_min_cut_one(draw: bool, k: int, n_blocks: int, max_block_nodes: int):
    block_graph = networkx.generators.random_tree(n_blocks, create_using=nx.DiGraph)
    block_nodes = list(block_graph.nodes())
    block_edges = list(block_graph.edges())

    components = {node: {"n": 0} for node in block_nodes}
    bridges = {e: None for e in block_edges}

    for block_edge_i in range(n_blocks - 1):
        m = 2 * random.randint(1, int(k / 2) - 1)
        bridges[block_edges[block_edge_i]] = (m, k - m)

    for node in block_nodes:
        n = components[node]["n"] = random.randint(2 * k, max_block_nodes)

        graph = get_k_regular(n, k)
        graph = nx.relabel_nodes(graph, {v: str(node) + "_" + str(v) for v in graph.nodes()})

        components[node]["g"] = graph

    graph = nx.Graph()

    for node in block_nodes:
        g = components[node]["g"]
        graph.add_nodes_from(list(g.nodes()))
        graph.add_edges_from(list(g.edges()))

    for g_v, g_w in block_edges:
        center_node = "B-" + str(g_v) + "-" + str(g_w)
        graph.add_node(center_node)

        a, b = bridges[(g_v, g_w)]

        graph_v = components[g_v]["g"]
        while a > 0:
            graph_nodes = list([node for (node, val) in graph_v.degree() if val == k])
            edges = [(v, w) for (v, w) in graph.edges() if v in graph_nodes and w in graph_nodes]

            random.shuffle(edges)
            e = edges[0]
            graph.remove_edge(e[0], e[1])
            graph.add_edge(e[0], center_node)
            graph.add_edge(e[1], center_node)
            a -= 2

        graph_w = components[g_w]["g"]
        while b > 0:
            graph_nodes = list([node for (node, val) in graph_w.degree() if val == k])
            edges = [(v, w) for (v, w) in graph.edges() if v in graph_nodes and w in graph_nodes]

            random.shuffle(edges)
            e = edges[0]
            graph.remove_edge(e[0], e[1])
            graph.add_edge(e[0], center_node)
            graph.add_edge(e[1], center_node)
            b -= 2

    return [(graph, {'draw': draw})]


def test_e2e(draw: bool):
    inputs = []
    print("test_2_degree_graph")
    inputs += test_2_degree_graph(draw, 3, 20)
    print("test_full_connected_graph")
    inputs += test_full_connected_graph(draw, 3, 20)
    print("test_k_regular")
    inputs += test_k_regular(draw, 12, 4, 1)
    print("test_k_regular")
    inputs += test_k_regular(draw, 12, 4, 4)
    for k in [4, 6, 8]:
        for b in [2, 3, 4, 5]:
            print("test_k_regular_min_cut_one", k, b)
            inputs += test_k_regular_min_cut_one(draw, k, b, 4 * k)
    print("test_k_regular")
    inputs += test_k_regular(draw, 12, 4)
    print("test_k_regular")
    inputs += test_k_regular(draw, 32, 8)
    print("test_random_graphs")
    inputs += test_random_graphs(draw, 15, 15, 0.1, 1)

    return inputs


def test_e2e_large(draw: bool):
    inputs = []
    print("test_2_degree_graph")
    inputs += test_2_degree_graph(draw, 3, 20)
    print("test_full_connected_graph")
    inputs += test_full_connected_graph(draw, 3, 20)
    print("test_k_regular")
    inputs += test_k_regular(draw, 12, 4, 1)
    print("test_k_regular")
    inputs += test_k_regular(draw, 12, 4, 4)
    for k in range(4, 17, 4):
        for b in [2, 3, 4, 5]:
            print("test_k_regular_min_cut_one", k, b)
            inputs += test_k_regular_min_cut_one(draw, k, b, 4 * k)

    for n, k in [(12, 2), (12, 4), (8, 4), (20, 4), (32, 8)]:
        print("test_k_regular", n, k)
        inputs += test_k_regular(draw, n, k)

    return inputs
