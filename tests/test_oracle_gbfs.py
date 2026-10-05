"""Unabhängiges Orakel für den Suchkern: GBFS gegen eine naive Neuimplementierung (lineare Suche statt Heap,
Einfügereihenfolge als Tie-Break), UCS gegen networkx-Dijkstra (Pfadkosten, Erreichbarkeit, Expansionszahl
zwischen #{Knoten mit Abstand < D}+1 und #{Abstand <= D}) - auf Zufallsgraphen mit ganzzahligen Koordinaten
(viele Gleichstände), getrennten Komponenten und doppelten Kanten sowie auf den Raster-Instanzen."""

import math
import random

import pytest

import gbfs_algorithm as A
import gbfs_graph as G
import gbfs_scenario as S

nx = pytest.importorskip("networkx")


def _naive_gbfs(graph, start, goal):
    def h(u):
        return math.dist(graph.xy[u], graph.xy[goal])

    pending, parent, closed = [start], {start: None}, []
    while pending:
        best = min(range(len(pending)), key=lambda i: (h(pending[i]), i))
        u = pending.pop(best)
        closed.append(u)
        if u == goal:
            path = [u]
            while parent[path[-1]] is not None:
                path.append(parent[path[-1]])
            return path[::-1], closed
        for v in graph.neighbors[u]:
            if v not in parent:
                parent[v] = u
                pending.append(v)
    return [], closed


def _nx(graph):
    g = nx.Graph()
    g.add_nodes_from(range(graph.n))
    for u in range(graph.n):
        for v, w in zip(graph.neighbors[u], graph.weights[u]):
            g.add_edge(u, v, weight=w)
    return g


def _check(graph, start, goal):
    g = _nx(graph)
    gb = A.greedy_best_first(graph, start, goal)
    uc = A.uniform_cost_search(graph, start, goal)
    path, order = _naive_gbfs(graph, start, goal)
    assert gb.path == path and gb.order == order and gb.expansions == len(order)
    reachable = nx.has_path(g, start, goal)
    assert reachable == bool(gb.path) == bool(uc.path)
    if not reachable:
        assert gb.cost == uc.cost == float("inf")
        return
    d = nx.dijkstra_path_length(g, start, goal)
    assert uc.cost == pytest.approx(d, abs=1e-9)
    assert gb.cost == pytest.approx(sum(g[u][v]["weight"] for u, v in zip(path[:-1], path[1:])), abs=1e-9)
    assert gb.cost >= d - 1e-9
    dist = nx.single_source_dijkstra_path_length(g, start)
    lower = sum(1 for x in dist.values() if x < d - 1e-12)
    upper = sum(1 for x in dist.values() if x <= d + 1e-12)
    assert lower + 1 <= uc.expansions <= upper


def test_random_graphs_with_ties_match_the_oracle():
    rnd = random.Random(1)
    for _ in range(150):
        n = rnd.randint(2, 12)
        xy = [(rnd.randint(0, 4), rnd.randint(0, 4)) for _ in range(n)]
        edges = [(u, v, float(rnd.randint(1, 6))) for u, v in
                 ((rnd.randrange(n), rnd.randrange(n)) for _ in range(rnd.randint(0, 2 * n))) if u != v]
        _check(G.from_edges(n, xy, edges), rnd.randrange(n), rnd.randrange(n))


def test_grid_instances_match_the_oracle():
    rnd = random.Random(2)
    for _ in range(40):
        inst = S.grid_instance(rnd.randint(2, 8), rnd.choice([0, 15, 40]), rnd.randint(0, 10**6))
        _check(inst.graph, inst.start, inst.goal)


def test_trap_by_hand():
    """Handrechnung: GBFS läuft Köder-Korridor (14.47), optimal ist der Umweg (13.46), Lücke 7.47 %."""
    inst = S.trap_instance()
    gbfs = A.greedy_best_first(inst.graph, inst.start, inst.goal)
    ucs = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
    d = math.dist
    corridor = d((0, 0), (8, .5)) + d((8, .5), (8.5, 1.5)) + d((8.5, 1.5), (8.7, 2.5)) + d((8.7, 2.5), (8.8, 3.5)) + d((8.8, 3.5), (9, .2))
    detour = d((0, 0), (2, 3)) + d((2, 3), (5, 5)) + d((5, 5), (9, .2))
    assert gbfs.cost == pytest.approx(corridor, abs=1e-9) and ucs.cost == pytest.approx(detour, abs=1e-9)
    assert gbfs.expansions == 6 and ucs.expansions == 8
