# Algo Controller for Manager

from typing import Callable, Any

import networkx as nx

from src.infra.algo import Algo, AlgoChecker


TestGenerator = Callable[..., list[tuple[nx.Graph, dict]]]
TestParamOption = tuple[str] | tuple[str, Any] | tuple[str, Any, Callable[[str], Any]]


class AlgoTestParam:
    key: str
    default_value: Any
    converter: Callable[[str], Any]

    def __init__(self, key: str, default_value: str = '', converter: Callable[[str], Any] = None) -> None:
        self.key = key
        self.default_value = default_value
        if converter is None:
            self.converter = type(self.default_value)
        else:
            self.converter = converter


class AlgoTest:
    test_name: str
    test_generator: TestGenerator
    params: list[AlgoTestParam]

    def __init__(self, test_name: str, test_generator: TestGenerator, params: list[AlgoTestParam | TestParamOption]):
        self.test_name = test_name
        self.test_generator = test_generator
        self.params = []
        for param in params:
            if type(param) == tuple:
                self.params.append(AlgoTestParam(*param))
            else:
                self.params.append(param)


class AlgoController:
    name: str
    tests: list[AlgoTest]
    run: Callable[[], Algo]

    def __init__(self, name: str, run: Callable[[], Algo]):
        self.name = name
        self.tests = []
        self.run = run

    def add_test(self, test_name: str, test_generator: TestGenerator, params: list[AlgoTestParam | TestParamOption]) -> None:
        self.tests.append(AlgoTest(test_name, test_generator, params))


def create_algo_checker(run: Callable[[], Algo], checker: Callable[[Algo], AlgoChecker]):
    def wrapper() -> Algo:
        return checker(run())

    return wrapper
