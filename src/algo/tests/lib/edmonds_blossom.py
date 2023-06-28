
Edge = tuple[int, int]
Graph = tuple[list[int], list[Edge]]


def neighbours(v: int, graph: Graph) -> list[int]:
    """Return the neighbours of the vertex v in the graph."""
    return list(
        set([a for a, b in graph[1] if b == v]).union(
            set([b for a, b in graph[1] if a == v])
        )
    )


def get_exposed_vertices(graph: Graph, matching: list[Edge]) -> list[int]:
    """Return the exposed vertices of the graph, given a matching."""
    return [
        v
        for v in graph[0]
        if v not in list(set([v for _, v in matching] + [v for v, _ in matching]))
    ]


def path_to_root(v, parent):
    """Return the path to the root of the forest, given a vertex."""
    path = []
    while parent[v] != v:
        path.append((v, parent[v]))
        v = parent[v]
    return path


def reverse_tuples(ls: list) -> list:
    """[(0, 1), (2, 3)] -> [(1, 0), (3, 2)]."""
    return list(map(lambda x: tuple(reversed(x)), ls))


def reverse_list(ls: list) -> list:
    return list(reversed(ls))


def get_blossom_edges(v: int, w: int, parent) -> list[Edge]:
    """Get the path around the blossom, starting from the root."""
    v_path = reverse_list(reverse_tuples(path_to_root(v, parent)))
    w_path = reverse_list(reverse_tuples(path_to_root(w, parent)))

    while len(v_path) != 0 and len(w_path) != 0 and v_path[0] == w_path[0]:
        v_path.pop(0)
        w_path.pop(0)

    return v_path + [(v, w)] + reverse_list(reverse_tuples(w_path))


def get_blossom_vertices(v: int, w: int, parent) -> list[int]:
    """Get the vertices of a blossom from the forest that ends in v, w.
    It is guaranteed that the first vertex is the root."""
    combined_path_vertices = [v for e in get_blossom_edges(v, w, parent) for v in e]

    return [combined_path_vertices[0]] + list(
        set(combined_path_vertices) - {combined_path_vertices[0]}
    )


def get_augmenting_blossom_path(v: int, w: int, edges: list[Edge]):
    """Get the path around the blossom edges, with the root being v and exit point being w."""
    if v == w:
        return []

    # first, try to go this way
    cycle = edges + edges
    s, e = -1, -1
    path = []
    for i, (a, b) in enumerate(cycle):
        if a == v:
            s = i

        if s != -1:
            path.append((a, b))

        if b == w:
            if len(path) % 2 == 0:
                return path
            break

    # now try to go the other way
    cycle = reverse_list(reverse_tuples(cycle))
    s, e = -1, -1
    path = []
    for i, (a, b) in enumerate(cycle):
        if a == v:
            s = i

        if s != -1:
            path.append((a, b))

        if b == w:
            if len(path) % 2 == 0:
                return path
            break

    print("This should not have happened, there is a bug somewhere.")
    quit()


def find_augmenting_path(graph: Graph, matching: list[Edge]) -> list[Edge] | str:
    """Find and return an augmenting path in the graph, or [] if there isn't one."""
    # FOREST variables
    parent = {}  # parent[v]... parent of v in the forest
    root_node = {}  # root_node[v]... root node for v
    layer = {}  # layer[v]... which layer is v in

    # start with all exposed vertices as tree roots
    queue = get_exposed_vertices(graph, matching)
    marked = set(matching)

    for v in queue:
        parent[v] = v
        root_node[v] = v
        layer[v] = 0

    # run a BFS to add the augmenting paths to the forest
    while len(queue) != 0:
        v = queue.pop(0)

        # skip marked vertices
        if v in marked:
            continue

        for w in neighbours(v, graph):
            if (v, w) in marked or (w, v) in marked:
                continue

            # add neighbours of w that are in the matching to the forest
            if w not in layer:
                # w is in the forest, so it is matched
                parent[w] = v
                layer[w] = layer[v] + 1
                root_node[w] = root_node[v]

                # find the one vertex it is matched with
                for x in neighbours(w, graph):
                    if (w, x) in matching or (x, w) in matching:
                        parent[x] = w
                        layer[x] = layer[w] + 1
                        root_node[x] = root_node[w]

                        queue.append(x)
            else:
                if layer[w] % 2 == 0:
                    if root_node[v] != root_node[w]:
                        return (
                            reverse_list(path_to_root(v, parent))
                            + [(v, w)]
                            + path_to_root(w, parent)
                        )
                    else:
                        vertices = get_blossom_vertices(v, w, parent)
                        root = vertices[0]

                        # preserve the root as the new vertex
                        new_vertices = list(set(graph[0]) - set(vertices[1:]))

                        # transform all edges that previously went to the blossom to the new single vertex
                        new_edges = [
                            (
                                a if a not in vertices else vertices[0],
                                b if b not in vertices else vertices[0],
                            )
                            for a, b in graph[1]
                        ]

                        # remove loops and multi-edges
                        new_edges = [(a, b) for a, b in new_edges if a != b]
                        new_edges = [
                            (a, b)
                            for a, b in new_edges
                            if (b, a) not in new_edges or b < a
                        ]

                        # remove removed edges from the matching
                        new_matching = [
                            (a, b)
                            for a, b in matching
                            if a not in vertices[1:] and b not in vertices[1:]
                        ]
                        new_graph = (new_vertices, new_edges)

                        # recursively find the augmenting path in the new graph
                        path = find_augmenting_path(new_graph, new_matching)
                        if path == "NICE":
                            return "NICE"

                        # if no path was found, no path lifting will be done
                        if path == []:
                            return []

                        # find the edges that are connected to the compressed vertex
                        edges_in_vertices = []
                        for a, b in path:
                            if a in vertices or b in vertices:
                                edges_in_vertices.append((a, b))

                        # if the path doesn't cross the blossom, simply return it
                        if len(edges_in_vertices) == 0:
                            return path

                        # find the other vertex that the blossom is connected to
                        # it enters through the root and must leave somewhere...
                        enter_edge = None
                        leave_edge = None
                        leave_edge_match = None
                        for a_orig, b_orig in edges_in_vertices:
                            vertex = a_orig if a_orig != root else b_orig

                            candidates = []

                            for b, c in graph[1]:
                                if (
                                    b == vertex
                                    and c in vertices
                                    or c == vertex
                                    and b in vertices
                                ):
                                    candidates.append((b, c))

                            for a, b in candidates:
                                if a == root or b == root and enter_edge is None:
                                    enter_edge = (a if a != root else b, root)
                                    break
                            else:
                                # doesn't matter... we can make any vertex work
                                a, b = candidates[0]

                                leave_edge_match = (a_orig, b_orig)
                                leave_edge = (
                                    a if a not in vertices else b,
                                    a if a in vertices else b,
                                )

                        if leave_edge is None:
                            return path

                        if leave_edge is not None and enter_edge is not None:
                            print(graph)
                            # print("NICE")
                            # for a, b in graph[1]:
                            #     print(a, b)
                            # quit()
                            return "NICE"

                        blossom_path = get_augmenting_blossom_path(
                            root, leave_edge[1], get_blossom_edges(v, w, parent)
                        )

                        i = path.index(leave_edge_match)

                        # improve the matching by injecting the lifted path
                        if i - 1 >= 0 and root in path[i]:
                            reverse_list(blossom_path)

                        return path[:i] + blossom_path + [leave_edge] + path[i + 1 :]
                else:
                    pass  # do nothing!

            marked.add((v, w))

        marked.add(v)

    return []


def improve_matching(graph: Graph, matching: list[Edge]) -> list[Edge] | str:
    """Attempt to improve the given matching in the graph."""
    path = find_augmenting_path(graph, matching)
    if path == "NICE":
        return "NICE"

    improved_matching = list(matching)
    if path != []:
        for i, e in enumerate(path):
            # a bit of a hack since the edges are all messed up
            if e not in graph[1]:
                e = (e[1], e[0])

            if i % 2 == 0:
                improved_matching.append(e)
            else:
                improved_matching.remove(e)

    return improved_matching


def edmonds_blossom(graph: Graph) -> list[Edge] | str:
    """Find the maximum matching in a graph."""
    matching = []

    while True:
        improved_matching = improve_matching(graph, matching)
        if improved_matching == "NICE":
            return "NICE"

        if matching == improved_matching:
            return matching

        matching = improved_matching

