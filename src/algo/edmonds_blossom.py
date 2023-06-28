import typing

import networkx as nx

from src.infra.algo import Algo
from src.infra.step import PlotStep, DrawReturn


Node = typing.Any
BlossomParams = tuple[Node, Node, dict[Node, Node | None]]


# steps
class MatchingStep(PlotStep):
    def __init__(self, graph: nx.Graph, matching: list[set[int]], text: str = "", augmenting_path: list | None = None) -> None:
        self.graph = graph.copy()
        self.matching = matching.copy()
        self.text = text
        self.augmenting_path = augmenting_path

    def draw(self) -> DrawReturn:
        augmenting_path = []
        if self.augmenting_path is not None:
            augmenting_path = [{self.augmenting_path[i-1], self.augmenting_path[i]} for i in range(1, len(self.augmenting_path))]

        colors = {e: 'b' for e in self.graph.edges()}
        colors.update({e: 'r' for e in self.graph.edges() if set(list(e)) in self.matching})
        colors.update({e: 'g' for e in self.graph.edges() if set(list(e)) in augmenting_path})

        node_color = [colors[e] for e in self.graph.edges()]
        nx.draw_networkx(self.graph, edge_color=node_color)

        return None, self.text + "Matching: {}".format(len(self.matching))


# algo
class EdmondsBlossomAlgo(Algo):
    def run(self, graph: nx.Graph, args: dict) -> list[set[int]]:
        matching: list[set[int]] = []

        if 'matching' in args:
            matching = args['matching']

        self.add_step(MatchingStep(graph, matching))
        return self.edmonds_blossom(graph, matching)

    def edmonds_blossom(self, graph: nx.Graph, matching: list[set[Node]]) -> list[set[Node]]:
        path, blossom_params = self.find_augmenting_path(graph, matching)
        if path:
            self.add_step(MatchingStep(graph, matching, augmenting_path=path))
            self.improve_matching_by_path(matching, path)

        while path:
            path, blossom_params = self.find_augmenting_path(graph, matching)
            if path:
                self.add_step(MatchingStep(graph, matching, augmenting_path=path))
                self.improve_matching_by_path(matching, path)

        if blossom_params is not None:
            matching = self.improve_matching_by_blossom(graph, matching, blossom_params)

        return matching

    def improve_matching_by_path(self, matching: list[set[Node]], path: list[Node]) -> None:
        for i in range(1, len(path)):
            e = {path[i - 1], path[i]}
            if e not in matching:
                matching.append(e)
            else:
                matching.remove(e)

    def improve_matching_by_blossom(self, graph: nx.Graph, matching: list[set[Node]], blossom_params: BlossomParams):
        w, v, bfs_tree = blossom_params

        p1 = self.get_path(bfs_tree, w)
        p2 = self.get_path(bfs_tree, v)

        p = []
        while len(p1) > 0 and len(p2) and p1[0] == p2[0]:
            p = p + [p1[0]]
            p1.pop(0)
            p2.pop(0)

        circle = [p[-1]] + p1 + list(reversed(p2))

        b = 0
        while graph.has_node("b" + str(b)):
            b += 1

        u = "b" + str(b)

        blossom_g = nx.Graph()
        blossom_g.add_node(u)
        blossom_g.add_nodes_from([v1 for v1 in graph.nodes() if v1 not in circle])
        blossom_g.add_edges_from([(v1, w1) for v1, w1 in graph.edges() if (v1 not in circle) and (w1 not in circle)])
        blossom_g.add_edges_from([(v1, u) for v1, w1 in graph.edges() if (v1 not in circle) and (w1 in circle)])
        blossom_g.add_edges_from([(w1, u) for v1, w1 in graph.edges() if (v1 in circle) and (w1 not in circle)])

        blossom_matching = []
        for e in matching:
            v1, w1 = list(e)
            if (v1 not in circle) or (w1 not in circle):
                if (v1 not in circle) and (w1 not in circle):
                    blossom_matching.append(e)
                elif v1 not in circle:
                    blossom_matching.append({u, v1})
                else:
                    blossom_matching.append({u, w1})

        blossom_matching = self.edmonds_blossom(blossom_g, blossom_matching)
        self.add_step(MatchingStep(blossom_g, blossom_matching, "Blossom Graph of " + u + " - "))

        matching.clear()

        u_true = None
        for e in blossom_matching:
            if u not in e:
                matching.append(e)
            else:
                v1 = [v1 for v1 in e if v1 != u][0]
                u_true_arr = [w2 for w2 in circle if graph.has_edge(v1, w2)]
                if len(u_true_arr) > 0:
                    u_true = u_true_arr[0]
                    matching.append({v1, u_true})

        if u_true is None:
            u_true = circle[0]

        end = i = circle.index(u_true)
        i = (i + 1) % len(circle)
        while i != end:
            matching.append({circle[i], circle[(i + 1) % len(circle)]})
            i = (i + 2) % len(circle)

        return matching

    def in_matching(self, node: Node, matching: list[set[Node]]):
        return not all([node not in e for e in matching])

    def find_augmenting_path(self, graph: nx.Graph, matching: list[set[Node]]) -> tuple[list[Node] | None, BlossomParams | None]:
        selected_blossom_params: BlossomParams | None = None

        for s in graph.nodes():
            if not self.in_matching(s, matching):
                path, blossom_params = self.find_augmenting_path_from_node(graph, matching, s)
                if path is not None:
                    return path, None

                if selected_blossom_params is None:
                    selected_blossom_params = blossom_params

        return None, selected_blossom_params

    def find_augmenting_path_from_node(self, graph: nx.Graph, matching: list[set[Node]], s: Node) -> tuple[
        list[Node] | None, BlossomParams | None]:
        bfs_tree: dict[Node, Node | None] = {s: None}
        explored: list[Node] = []
        to_explore: list[Node] = [s]
        to_explore_next: list[Node] = []

        blossom_params: BlossomParams | None = None

        while len(to_explore) > 0 or len(to_explore_next) > 0:
            if len(to_explore) == 0:
                to_explore = to_explore_next
                to_explore_next = []

            v = to_explore.pop(0)
            explored.append(v)

            from_matching_edge = (bfs_tree[v] is None) or ({v, bfs_tree[v]} in matching)

            if not from_matching_edge:
                if not self.in_matching(v, matching):
                    return self.get_path(bfs_tree, v), None

                for w in graph.neighbors(v):
                    if {v, w} in matching:
                        if w not in bfs_tree:
                            to_explore_next = to_explore_next + [w]
                            bfs_tree[w] = v
                        elif blossom_params is None:
                            if w in explored and (({w, bfs_tree[w]} in matching) == from_matching_edge):
                                blossom_params = (v, w, bfs_tree.copy())
            else:
                for w in graph.neighbors(v):
                    if {v, w} not in matching:
                        if w not in bfs_tree:
                            to_explore_next = to_explore_next + [w]
                            bfs_tree[w] = v
                        elif blossom_params is None:
                            if w in explored and (({w, bfs_tree[w]} in matching) == from_matching_edge):
                                blossom_params = (v, w, bfs_tree.copy())

        return None, blossom_params

    def get_path(self, bfs_tree: dict[Node, Node | None], node: Node) -> list[Node]:
        path = []
        while node is not None:
            path = [node] + path
            node = bfs_tree[node]
        return path
