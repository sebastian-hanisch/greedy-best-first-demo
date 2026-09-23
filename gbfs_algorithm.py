"""Gemeinsamer Suchkern für Greedy Best-First Search UND die Uniform-Cost-Search-Referenz - EIN
`_search(graph, start, goal, priority_fn)` mit Prioritätswarteschlange und `visited`-Menge (kein Backtracking,
keine Wiedereröffnung eines bereits expandierten Knotens - Standard-Lehrbuchverhalten). `greedy_best_first`
verwendet `priority = h(n)` (ignoriert den bisher aufgelaufenen Pfadwert vollständig), `uniform_cost_search`
verwendet `priority = g(n)` (Dijkstra auf diesem Graphen) als exakte Referenz. Legt die Grundlage für das
spätere A*-Stück (`priority = g(n) + h(n)`), ohne hier schon mehr zu bauen als nötig.

Determinismus: fester Tie-Break bei gleicher Priorität über einen monoton steigenden Einfüge-Zähler (klassisches
`heapq`-Muster) - derselbe Lauf liefert immer dasselbe Ergebnis."""

import heapq
from dataclasses import dataclass, field

import numpy as np


def heuristic(xy, goal):
    """Euklidischer Abstand jedes Knotens zum Ziel - vektorisiert. Bei echten Kantengewichten (siehe
    `gbfs_scenario.py`) automatisch zulässig (Dreiecksungleichung)."""
    return np.hypot(*(xy - xy[goal]).T)


@dataclass
class SearchResult:
    path: list                  # Knotenfolge Start..Ziel, oder [] falls kein Pfad existiert
    cost: float                 # Summe der Kantengewichte entlang des Pfades
    expansions: int             # Zahl der expandierten Knoten (Effizienz-Kennzahl dieses Stücks)
    order: list = field(default_factory=list)     # Reihenfolge der expandierten Knoten (für die Schritt-Visualisierung)


def _search(graph, start, goal, priority_fn, relax=True):
    """`priority_fn(node, g_cost) -> float` bestimmt die Warteschlangen-Priorität. `g_cost` ist der bislang
    aufgelaufene Pfadwert zu `node` (für Uniform-Cost-Search gebraucht, von Greedy Best-First ignoriert).

    `relax`: ob ein noch nicht expandierter, aber schon entdeckter Knoten einen GÜNSTIGEREN Elternknoten
    bekommt, sobald ein billigerer Weg zu ihm gefunden wird (klassische Dijkstra-Relaxation - für
    Uniform-Cost-Search nötig, damit es tatsächlich optimal bleibt). Bei `relax=False` behält ein Knoten für
    immer den ERSTEN gefundenen Elternknoten (echtes "kein Backtracking" - der Kern der GBFS-Schwäche: eine
    Relaxation hier würde den gemessenen Qualitätsverlust künstlich kleinrechnen, da GBFS dann doch beiläufig
    von g(n) profitieren würde, obwohl es g(n) laut Definition komplett ignoriert)."""
    counter = 0
    frontier = [(priority_fn(start, 0.0), counter, start, 0.0)]
    came_from = {start: None}
    g_cost = {start: 0.0}
    visited = set()
    order = []

    while frontier:
        _priority, _c, node, g = heapq.heappop(frontier)
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        if node == goal:
            path = []
            cur = node
            while cur is not None:
                path.append(cur)
                cur = came_from[cur]
            path.reverse()
            return SearchResult(path, g, len(order), order)
        for v, w in zip(graph.neighbors[node], graph.weights[node]):
            if v in visited:
                continue
            g_v = g + w
            is_new = v not in g_cost
            if is_new or (relax and g_v < g_cost[v]):
                g_cost[v] = g_v
                came_from[v] = node
                counter += 1
                heapq.heappush(frontier, (priority_fn(v, g_v), counter, v, g_v))

    return SearchResult([], float("inf"), len(order), order)


def greedy_best_first(graph, start, goal):
    h = heuristic(graph.xy, goal)
    return _search(graph, start, goal, lambda node, g: h[node], relax=False)


def uniform_cost_search(graph, start, goal):
    return _search(graph, start, goal, lambda node, g: g, relax=True)
