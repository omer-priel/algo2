# tests for edmonds blossom algo

import random

import networkx as nx

from src.infra.algo import AlgoChecker
from src.infra.step import PlotStep, DrawReturn
from src.algo.tests.lib.max_matching import get_max_matching, is_matching


# steps
class MatchingStep(PlotStep):
    def __init__(self, graph: nx.Graph, matching: list[set[int]], text: str) -> None:
        self.graph = graph.copy()
        self.matching = matching.copy()
        self.text = text

    def draw(self) -> DrawReturn:
        edge_color = [("r" if (set(list(e)) in self.matching) else "b") for e in self.graph.edges()]
        nx.draw_networkx(self.graph, edge_color=edge_color)

        return None, self.text


# algo checker
class EdmondsBlossomAlgoChecker(AlgoChecker):
    def checker(self, graph: nx.Graph, arg: dict, matching: list[set[int]]):
        if not is_matching(graph, matching):
            self.add_step(MatchingStep(graph, matching, "Is not matching!"))
            return matching

        max_matching = get_max_matching(graph)

        if len(matching) != max_matching:
            self.add_step(MatchingStep(graph, matching, "Got {} but the max matching is {}!".format(len(matching), max_matching)))
            return matching

        self.add_step(MatchingStep(graph, matching, "The max matching is {}".format(len(matching))))
        return matching
