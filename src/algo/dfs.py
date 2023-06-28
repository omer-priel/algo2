
import networkx as nx

from src.infra.algo import Algo
from src.infra.step import GraphStep, PlotStep, DrawReturn


# steps
class DFSStep(PlotStep):
    def __init__(self, graph: nx.Graph, current: int, tree: dict[int, int | None], explored: list[int], to_explore: list[int]) -> None:
        self.current = current
        self.tree = tree.copy()
        self.graph = graph.copy()
        self.explored = explored.copy()
        self.to_explore = to_explore.copy()

    def draw(self) -> DrawReturn:
        text = "Explored: {}, To Explore {}".format(str(len(self.explored)), str(len(self.to_explore)))

        node_color = []
        for node in self.graph.nodes():
            if node == self.current:
                node_color.append('r')
            elif node in self.explored:
                node_color.append('g')
            elif node in self.to_explore:
                node_color.append('b')
            else:
                node_color.append('#888888')

        edge_color = []
        for e in self.graph.edges():
            v, w = e
            if (v in self.tree and self.tree[v] == w) or (w in self.tree and self.tree[w] == v):
                edge_color.append('g')
            else:
                edge_color.append('#888888')

        nx.draw_networkx(self.graph, node_color=node_color, edge_color=edge_color)

        return None, text


# the algo
class DFSAlgo(Algo):
    def run(self, graph: nx.Graph, args: dict) -> dict[int, int | None] | None:
        if len(graph.nodes()) == 0:
            self.get_tracker().add_step(GraphStep(graph, "Is Empty graph!"))
            return

        if not nx.is_connected(graph):
            self.get_tracker().add_step(GraphStep(graph, "Is Not Connected!"))
            return

        self.add_step(GraphStep(graph))

        s = list(graph.nodes())[0]

        dfs_tree: dict[int, int | None] = {s: None}

        explored = []
        to_explore = [s]

        while len(to_explore) > 0:
            v = to_explore.pop(0)
            explored += [v]

            add = [w for w in graph.neighbors(v) if w not in explored + to_explore]
            for w in add:
                dfs_tree[w] = v

            to_explore = add + to_explore

            self.add_step(DFSStep(graph, v, dfs_tree, explored, to_explore))

        return dfs_tree
