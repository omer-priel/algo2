# entry point

from src.infra.algo_controller import AlgoController, create_algo_checker
from src.manager.manager import Manager

from src.algo.dfs import DFSAlgo
from src.algo.hungarian import HungarianAlgo
from src.algo.edmonds_blossom import EdmondsBlossomAlgo
from src.algo.brooks import BrooksAlgo
from src.algo.tests import hungarian_tests
from src.algo.tests import brooks_tests
from src.algo.tests import edmonds_blossom_tests
from src.algo.checkers.edmonds_blossom_checker import EdmondsBlossomAlgoChecker


def get_algo_controllers() -> list[AlgoController]:
    dfs = AlgoController('DFS', DFSAlgo)

    hungarian = AlgoController('Hungarian', HungarianAlgo)
    hungarian.add_test('Test Random Graphs', hungarian_tests.test_random_graph, [('min_n', 2), ('max_n', 5), ('p', 0.5), ('k', 3)])

    brooks = AlgoController('Brooks', BrooksAlgo)
    brooks.add_test('Test Random Graphs', brooks_tests.test_random_graphs, [('draw', True), ('min_n', 1), ('max_n', 10), ('p', 0.2),
                                                                            ('k_iter', 3)])
    brooks.add_test('2 Degree Graph', brooks_tests.test_2_degree_graph, [('draw', True), ('min_n', 1), ('max_n', 10)])
    brooks.add_test('Full Connected', brooks_tests.test_full_connected_graph, [('draw', True), ('min_n', 1), ('max_n', 10)])
    brooks.add_test('Not k-Regular', brooks_tests.test_k_regular, [('draw', True), ('n', 12), ('k', 4), ('to_remove', 1)])
    brooks.add_test('k-Regular', brooks_tests.test_k_regular, [('draw', True), ('n', 12), ('k', 4), ('to_remove', 0)])
    brooks.add_test('k-Regular min cut of 1', brooks_tests.test_k_regular_min_cut_one, [('draw', True), ('k', 4), ('n_blocks', 2),
                                                                                        ('max_block_nodes', 16)])
    brooks.add_test('E2E', brooks_tests.test_e2e, [('draw', False)])
    brooks.add_test('E2E Large', brooks_tests.test_e2e_large, [('draw', False)])

    edmonds = AlgoController('Edmonds', create_algo_checker(EdmondsBlossomAlgo, EdmondsBlossomAlgoChecker))
    edmonds.add_test('Test Random Graphs', edmonds_blossom_tests.test_random_graphs, [('min_n', 1), ('max_n', 10), ('p', '0.2', float),
                                                                                      ('k_iter', 3)])
    edmonds.add_test('Test 1', edmonds_blossom_tests.test1, [])
    edmonds.add_test('Test 2', edmonds_blossom_tests.test2, [])
    edmonds.add_test('Test 3', edmonds_blossom_tests.test3, [])
    edmonds.add_test('Test 4 - Start with matching', edmonds_blossom_tests.test4, [])
    edmonds.add_test('Test from random', edmonds_blossom_tests.test_from_random, [])

    return [dfs, hungarian, brooks, edmonds]


def main() -> None:
    manager = Manager(1000, 600, algo_controllers=get_algo_controllers())
    manager.run()


if __name__ == '__main__':
    main()
