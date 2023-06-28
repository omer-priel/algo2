import typing

import networkx as nx

from src.infra.algo import Algo
from src.infra.step import GraphStep, PlotStep, DrawReturn


Node = typing.Any


# steps
class BipartiteStep(PlotStep):
    def __init__(self, graph: nx.Graph, b: set, a: set, matching: set[tuple[Node, Node]] | None = None) -> None:
        self.graph = graph.copy()
        self.a = a.copy()
        self.b = b.copy()
        self.matching = matching

    def draw(self) -> DrawReturn:
        pos = {}
        i = 0
        for v in self.a:
            pos[v] = (5, i * 3)
            i += 1

        i = 0
        for v in self.b:
            pos[v] = (10, i * 3)
            i += 1

        if self.matching is not None:
            edge_color = [("r" if (tuple(e) in self.matching) or (tuple(reversed(list(e))) in self.matching) else "b")
                          for e in self.graph.edges()]

            nx.draw_networkx(self.graph, pos=pos, edge_color=edge_color)
        else:
            nx.draw_networkx(self.graph, pos=pos)

        return None, ""


class HungarianStep(PlotStep):
    def __init__(self, directed_graph: nx.Graph,
                 matching: set[tuple[Node, Node]],
                 a_matched: set, a_unmatched: set,
                 b_matched: set, b_unmatched: set,
                 path: list[tuple[Node, Node]] | None = None) -> None:
        self.directed_graph = directed_graph.copy()
        self.matching = matching.copy()
        self.a_matched = a_matched.copy()
        self.a_unmatched = a_unmatched.copy()
        self.b_matched = b_matched.copy()
        self.b_unmatched = b_unmatched.copy()
        self.path = path

    def draw(self) -> DrawReturn:
        pos = {}
        i = 0
        for v in self.a_unmatched:
            pos[v] = (5, i * 3)
            i += 1

        i = 0
        for v in self.b_unmatched:
            pos[v] = (10, i * 3)
            i += 1

        i = max(len(self.a_unmatched), len(self.b_unmatched)) + 2
        for v in self.a_matched:
            pos[v] = (5, i * 3)
            i += 1

        i = max(len(self.a_unmatched), len(self.b_unmatched)) + 2
        for v in self.b_matched:
            pos[v] = (10, i * 3)
            i += 1

        if self.path is None:
            self.path = []

        edge_color = ["g" if e in self.path else
                      ("r" if (tuple(e) in self.matching) or (tuple(reversed(list(e))) in self.matching) else "b")
                      for e in self.directed_graph.edges()]
        nx.draw_networkx(self.directed_graph, pos=pos, edge_color=edge_color)

        return None, ""


# algo
class HungarianAlgo(Algo):
    def run(self, graph: nx.Graph, args: dict) -> set[tuple[Node, Node]] | None:
        matching = set()

        if len(graph.nodes()) == 0 or not nx.is_bipartite(graph):
            self.tracker.add_step(GraphStep(graph, "Is not Bipartite Graph!"))
            return

        a, b = set(), set()

        for v in graph.nodes():
            to_a = True
            for w in graph.neighbors(v):
                if w in a:
                    to_a = False
                    break
            if to_a:
                a.add(v)
            else:
                b.add(v)

        edges = list(graph.edges())

        graph = nx.Graph()
        graph.add_nodes_from(a, bipartite=0)
        graph.add_nodes_from(b, bipartite=1)
        graph.add_edges_from(edges)

        self.add_step(BipartiteStep(graph, a, b))

        path = self.find_augmenting_path(graph, matching)

        while path is not None:
            matching = self.improve_matching(a, matching, path)
            path = self.find_augmenting_path(graph, matching)

        self.add_step(BipartiteStep(graph, a, b, matching))

        return matching

    def get_sets(self, graph: nx.Graph, matching: set[tuple[Node, Node]]) -> tuple[set, set, set, set]:
        matched = [v for e in matching for v in e]

        a = {v for v, d in graph.nodes(data=True) if d["bipartite"] == 0}
        b = {v for v, d in graph.nodes(data=True) if d["bipartite"] == 1}

        a_matched = {v for v in a if v in matched}
        a_unmatched = {v for v in a if v not in matched}
        b_matched = {v for v in b if v in matched}
        b_unmatched = {v for v in b if v not in matched}

        return a_matched, a_unmatched, b_matched, b_unmatched

    def find_augmenting_path(self, graph: nx.Graph, matching: set[tuple]) -> list[tuple] | None:
        a_matched, a_unmatched, b_matched, b_unmatched = self.get_sets(graph, matching)

        directed_graph = nx.DiGraph()
        directed_graph.add_nodes_from(a_matched, bipartite=0)
        directed_graph.add_nodes_from(a_unmatched, bipartite=0)
        directed_graph.add_nodes_from(b_matched, bipartite=1)
        directed_graph.add_nodes_from(b_unmatched, bipartite=1)

        for e in graph.edges:
            if e in matching:
                directed_graph.add_edge(e[1], e[0], color='r')
            else:
                directed_graph.add_edge(e[0], e[1], color='b')

        self.add_step(HungarianStep(directed_graph, matching, a_matched, a_unmatched, b_matched, b_unmatched))

        for v in a_unmatched:
            path = self.find_augmenting_path_from_s(directed_graph, v, b_unmatched)
            if path is not None:
                self.add_step(HungarianStep(directed_graph, matching, a_matched, a_unmatched, b_matched, b_unmatched, path))
                return path

        return None

    def find_augmenting_path_from_s(self, directed_graph: nx.Graph, s: Node, targets: set) -> list[tuple] | None:
        # simple BFS with end of one in targets
        paths = {v: None for v, d in directed_graph.nodes(data=True)}
        visited = []
        toVisit = [s]
        while len(toVisit) > 0:
            v = toVisit.pop(0)
            visited.append(v)
            if v in targets:
                path = []
                w = v
                while w != s:
                    path = [(paths[w], w)] + path
                    w = paths[w]
                return path

            for w in directed_graph.neighbors(v):
                if w not in visited + toVisit:
                    toVisit = [w] + toVisit
                    paths[w] = v

        return None

    def improve_matching(self, a: set, matching: set[tuple], path: list[tuple]) -> set[tuple]:
        for i in range(len(path)):
            v, w = path[i]
            if w in a:
                u = w
                w = v
                v = u

            if i % 2 == 0:
                matching.add((v, w))
            else:
                matching.remove((v, w))

        return matching
