import typing

import networkx as nx

import matplotlib

from src.infra.algo import Algo
from src.infra.step import PlotStep, DrawReturn


Node = typing.Any


# steps
class NodesColoringGraphStep(PlotStep):
    def __init__(self, graph: nx.Graph, colors_assigned: dict[Node, int]) -> None:
        self.graph = graph.copy()
        self.colors_assigned = colors_assigned.copy()

    def draw(self) -> DrawReturn:
        max_color = max([0] + [self.colors_assigned[v] for v in self.colors_assigned]) + 1
        node_color = [NodesColoringGraphStep.get_color(v, max_color, self.colors_assigned) for v in self.graph.nodes()]
        nx.draw_networkx(self.graph, node_color=node_color)

        return None, "Nodes: {}, Max Color: {}".format(len(list(self.graph.nodes())), max_color)

    @staticmethod
    def get_color(node: typing.Any, max_color: int, colors_assigned: dict[typing.Any, int]) -> typing.Any:
        if max_color == 0:
            return "b"

        if node not in colors_assigned:
            return "r"

        return matplotlib.colormaps['plasma'](colors_assigned[node] / max_color)


# algo
class BrooksAlgo(Algo):
    def run(self, graph: nx.Graph, args: dict) -> dict[Node, int]:
        draw = 'draw' not in args or args['draw']

        colors_assigned = {}

        components = self.get_components(graph)
        for component in components:
            component_colors_assigned = self.brooks_algorithm_connected(component)
            colors_assigned.update(component_colors_assigned)

        if draw:
            self.add_step(NodesColoringGraphStep(graph, colors_assigned))

        return colors_assigned

    def bfs(self, graph: nx.Graph, s: Node) -> nx.Graph:
        visited = set()
        toVisit = [s]

        bfs_graph = nx.DiGraph()
        bfs_graph.add_node(s)

        while len(toVisit) > 0:
            v = toVisit.pop(0)
            visited.add(v)
            for w in graph.neighbors(v):
                if (w not in toVisit) and (w not in visited):
                    toVisit = [w] + toVisit
                    bfs_graph.add_node(w)
                    bfs_graph.add_edge(v, w)

        return bfs_graph

    def get_components(self, graph: nx.Graph) -> set[nx.Graph]:
        graph = graph.copy()
        components: set[nx.Graph] = set()

        nodes = list(graph.nodes())
        while len(nodes) > 0:
            s = nodes[0]
            component_nodes = self.bfs(graph, s).nodes()

            component = nx.Graph()
            component.add_nodes_from(component_nodes)
            for v in component_nodes:
                for w in component_nodes:
                    if graph.has_edge(v, w):
                        component.add_edge(v, w)
                        graph.remove_edge(v, w)

            graph.remove_nodes_from(component_nodes)

            components.add(component)

            nodes = list(graph.nodes())

        return components

    def color_graph(self, graph: nx.Graph, order: list[Node]) -> dict[Node, int]:
        colors_assigned = {}
        for v in order:
            neighbors_colors = []
            for w in graph.neighbors(v):
                if w in colors_assigned:
                    neighbors_colors.append(colors_assigned[w])
            color = 0
            while color in neighbors_colors:
                color += 1
            colors_assigned[v] = color

        return colors_assigned

    def color_path_graph(self, graph: nx.Graph) -> dict[Node, int]:
        start, end = [node for (node, val) in graph.degree() if val == 1]
        order = [start]
        last = None
        now = start
        while now != end:
            neb = list(graph.neighbors(now))
            if neb[0] != last:
                last = now
                now = neb[0]
                order.append(now)
            else:
                last = now
                now = neb[1]
                order.append(now)

        return self.color_graph(graph, order)

    def color_circular_graph(self, graph: nx.Graph) -> dict[Node, int]:
        now = start = list(graph.nodes())[0]
        last = None

        order = [start]
        while now != start or len(order) == 1:
            neb = list(graph.neighbors(now))
            if neb[0] != last:
                last = now
                now = neb[0]
                order.append(now)
            else:
                last = now
                now = neb[1]
                order.append(now)

        return self.color_graph(graph, order)

    def get_spinning_tree_order(self, tree: nx.Graph, root: Node) -> list[Node]:
        order = []

        tree = tree.copy()

        leaves = [v for (v, val) in tree.degree() if val == 1 and v != root]
        while len(leaves) > 0:
            order = order + leaves
            tree.remove_nodes_from(leaves)
            leaves = [v for (v, val) in tree.degree() if val == 1 and v != root]

        return order + [root]

    def find_vertex_cut(self, graph: nx.Graph) -> tuple[Node, set[nx.Graph]] | None:
        for v in graph.nodes():
            g = graph.copy()
            g.remove_node(v)
            components = self.get_components(g)
            if len(components) > 1:
                return v, components

        return None

    def find_x_y_z(self, graph: nx.Graph) -> tuple[Node, Node, Node] | None:
        for x in graph.nodes():
            for y in graph.neighbors(x):
                for z in graph.neighbors(x):
                    if y != z and not graph.has_edge(z, y):
                        return x, y, z
        return None

    def brooks_algorithm_connected(self, graph: nx.Graph) -> dict[Node, int]:
        nodes = list(graph.nodes())
        max_degree = max([val for (node, val) in graph.degree()])
        is_k_regular = len([node for (node, val) in graph.degree() if val != max_degree]) == 0

        # check full connected
        is_full_connected = True
        for v in nodes:
            for w in nodes:
                if v != w:
                    is_full_connected = graph.has_edge(v, w)
                    if not is_full_connected:
                        break
            if not is_full_connected:
                break

        if is_full_connected:
            return {nodes[i]: i for i in range(len(nodes))}

        # check max degree is 2
        if max_degree == 2:
            if is_k_regular:
                return self.color_circular_graph(graph)
            return self.color_path_graph(graph)

        # is not k-regular
        if not is_k_regular:
            # A: create spinning tree T from graph
            s = [node for (node, val) in graph.degree() if val != max_degree][0]
            spinning_tree = self.bfs(graph, s)
            order = self.get_spinning_tree_order(spinning_tree, s)
            return self.color_graph(graph, order)

        # is k-regular
        # B: check if exists cut size of graph is 1
        res = self.find_vertex_cut(graph)
        if res is not None:
            # B.A: separate into graphs from the cut
            # B.A: solve the g1 and g2 parts as not k-regular solver
            s, components = res
            components_colored = {}
            for component in components:
                component.add_node(s)
                component.add_edges_from([(s, v) for v in graph.neighbors(s) if v in component.nodes()])
                component_colored = self.brooks_algorithm_connected(component)

                # B.A: replace so the color of s be same (or simply 0)
                color_of_s = component_colored[s]
                if color_of_s != 0:
                    has_zero = [node for node in component.nodes if component_colored[node] == 0]
                    has_s_color = [node for node in component.nodes if component_colored[node] == color_of_s]
                    component_colored.update({node: color_of_s for node in has_zero})
                    component_colored.update({node: 0 for node in has_s_color})

                components_colored.update(component_colored)

            return components_colored

        # B: cut size of graph > 1
        # B.B: for each y,z try find x
        # B.B: need to find (x, y), (x, z) in graph, (y, z) not in graph
        x, y, z = self.find_x_y_z(graph)

        # B.B: create spinning tree T from graph - [y,z]
        graph_mis = graph.copy()
        graph_mis.remove_nodes_from([y, z])
        spinning_tree = self.bfs(graph_mis, x)
        # B.B: order = [y,z] + order from T by levels of leaves of T
        order = [y, z] + self.get_spinning_tree_order(spinning_tree, x)
        # B.B: return by greedy with order
        return self.color_graph(graph, order)
