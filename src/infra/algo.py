from typing import Any

import networkx as nx

from src.infra.step import Step
from src.tracker.tracker import Tracker


class Algo:
    tracker: Tracker

    def __init__(self) -> None:
        self.tracker = Tracker()

    def get_tracker(self) -> Tracker:
        return self.tracker

    def add_step(self, step: Step) -> None:
        self.tracker.add_step(step)

    def run(self, graph: nx.Graph, args: dict) -> Any:
        pass


class AlgoChecker(Algo):
    algo: Algo

    def __init__(self, algo: Algo) -> None:
        super().__init__()

        self.algo = algo

    def get_tracker(self) -> Tracker:
        return self.algo.get_tracker()

    def add_step(self, step: Step) -> None:
        self.algo.add_step(step)

    def run(self, graph: nx.Graph, args: dict) -> Any:
        return self.checker(graph, args, self.algo.run(graph, args))

    def checker(self, graph: nx.Graph, arg: dict, res: Any):
        return res
