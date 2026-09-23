"""Die zentrale Korrektheits-Kette: UCS ist wirklich optimal (gegen Brute-Force-Enumeration aller einfachen Pfade
auf kleinen Instanzen), GBFS liefert immer einen gültigen Pfad, Pfadkosten stimmen mit einer unabhängigen
Neuberechnung überein, die Heuristik ist auf den Instanzen dieses Stücks tatsächlich zulässig, die handgebaute
Sackgassen-Instanz zeigt NACHWEISLICH einen echten Qualitätsunterschied, und beide Suchen sind deterministisch."""

import pytest

import gbfs_algorithm as A
import gbfs_graph as G
import gbfs_scenario as S

EPS = 1e-9


def _brute_force_shortest_path(graph, start, goal, max_len=8):
    """Enumeriert ALLE einfachen Pfade bis `max_len` Knoten per DFS - nur für sehr kleine Instanzen brauchbar,
    aber unabhängig von jeder Prioritätswarteschlangen-Logik."""
    best = None
    stack = [(start, [start], 0.0)]
    while stack:
        node, path, cost = stack.pop()
        if node == goal:
            if best is None or cost < best[1]:
                best = (path, cost)
            continue
        if len(path) >= max_len:
            continue
        for v, w in zip(graph.neighbors[node], graph.weights[node]):
            if v not in path:
                stack.append((v, path + [v], cost + w))
    return best


@pytest.mark.parametrize("seed", range(15))
def test_uniform_cost_search_finds_the_true_shortest_path(seed):
    inst = S.grid_instance(side=5, obstacle_pct=15, seed=seed)
    result = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
    brute = _brute_force_shortest_path(inst.graph, inst.start, inst.goal, max_len=inst.graph.n)
    assert brute is not None
    assert result.cost == pytest.approx(brute[1], abs=1e-6)


def test_uniform_cost_search_matches_brute_force_on_the_trap_instance():
    inst = S.trap_instance()
    result = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
    brute = _brute_force_shortest_path(inst.graph, inst.start, inst.goal, max_len=inst.graph.n)
    assert result.cost == pytest.approx(brute[1], abs=1e-6)


@pytest.mark.parametrize("seed", range(30))
def test_greedy_best_first_returns_a_valid_connected_path(seed):
    inst = S.grid_instance(side=10, obstacle_pct=25, seed=seed)
    result = A.greedy_best_first(inst.graph, inst.start, inst.goal)
    assert result.path[0] == inst.start and result.path[-1] == inst.goal
    assert len(set(result.path)) == len(result.path)                          # keine Wiederholungen
    for u, v in zip(result.path[:-1], result.path[1:]):
        assert v in inst.graph.neighbors[u]


def test_no_path_is_correctly_reported_for_disconnected_graphs():
    graph = G.from_edges(4, [(0, 0), (1, 0), (2, 0), (3, 0)], [(0, 1, 1.0), (2, 3, 1.0)])
    for search in (A.greedy_best_first, A.uniform_cost_search):
        result = search(graph, 0, 3)
        assert result.path == [] and result.cost == float("inf")


@pytest.mark.parametrize("seed", range(20))
def test_returned_costs_match_an_independent_recomputation(seed):
    inst = S.grid_instance(side=12, obstacle_pct=25, seed=seed)
    for search in (A.greedy_best_first, A.uniform_cost_search):
        result = search(inst.graph, inst.start, inst.goal)
        assert G.path_cost(inst.graph, result.path) == pytest.approx(result.cost, abs=1e-6)


@pytest.mark.parametrize("seed", range(10))
def test_heuristic_is_admissible_on_generated_instances(seed):
    """h(n) darf den TATSÄCHLICHEN Restweg nie überschätzen - hier gegen UCS-Distanzen von jedem Knoten zum Ziel
    geprüft (UCS selbst schon gegen Brute-Force verifiziert, siehe oben)."""
    inst = S.grid_instance(side=8, obstacle_pct=20, seed=seed)
    h = A.heuristic(inst.graph.xy, inst.goal)
    for node in range(inst.graph.n):
        true_dist = A.uniform_cost_search(inst.graph, node, inst.goal).cost
        if true_dist == float("inf"):
            continue
        assert h[node] <= true_dist + EPS


def test_heuristic_is_admissible_on_the_trap_instance():
    inst = S.trap_instance()
    h = A.heuristic(inst.graph.xy, inst.goal)
    for node in range(inst.graph.n):
        true_dist = A.uniform_cost_search(inst.graph, node, inst.goal).cost
        assert h[node] <= true_dist + EPS


def test_the_hand_built_trap_makes_greedy_best_first_strictly_worse_than_optimal():
    inst = S.trap_instance()
    gbfs = A.greedy_best_first(inst.graph, inst.start, inst.goal)
    ucs = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
    assert gbfs.cost > ucs.cost + 0.5                                          # ein echter, klarer Unterschied
    assert gbfs.path != ucs.path


def test_greedy_best_first_is_deterministic():
    inst = S.grid_instance(side=12, obstacle_pct=25, seed=3)
    r1 = A.greedy_best_first(inst.graph, inst.start, inst.goal)
    r2 = A.greedy_best_first(inst.graph, inst.start, inst.goal)
    assert r1.path == r2.path and r1.cost == r2.cost and r1.expansions == r2.expansions


def test_uniform_cost_search_is_deterministic():
    inst = S.grid_instance(side=12, obstacle_pct=25, seed=3)
    r1 = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
    r2 = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
    assert r1.path == r2.path and r1.cost == r2.cost and r1.expansions == r2.expansions


def test_greedy_best_first_never_beats_uniform_cost_search_in_quality():
    """UCS ist per Definition optimal - GBFS darf NIE einen kürzeren Pfad finden, höchstens gleich lang."""
    for seed in range(30):
        inst = S.grid_instance(side=10, obstacle_pct=25, seed=seed)
        gbfs = A.greedy_best_first(inst.graph, inst.start, inst.goal)
        ucs = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
        assert gbfs.cost >= ucs.cost - EPS


def test_expansion_count_never_exceeds_the_number_of_nodes():
    for seed in range(10):
        inst = S.grid_instance(side=12, obstacle_pct=25, seed=seed)
        for search in (A.greedy_best_first, A.uniform_cost_search):
            result = search(inst.graph, inst.start, inst.goal)
            assert result.expansions <= inst.graph.n
