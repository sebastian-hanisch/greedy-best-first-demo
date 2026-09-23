"""Jede Zahl in den Hilfetexten, Presets, Tabellen und Grenzen der App ist hier über die fünf festen Sweep-
Instanzen belegt, mit denselben Auswertungsfunktionen wie die App selbst (`ev.run_config`/`ev.sweep`/
`ev.worse_expansion_share`) - NIE über ein Ad-hoc-Skript mit abweichender Zufalls-Bindung. Positive UND negative
Aussagen: GBFS ist klar effizienter (positiv) - aber die Vorab-Vermutung "mehr Hindernisse = größere
Optimalitätslücke" ist FALSCH, es ist genau umgekehrt (negativ, der zentrale ehrliche Befund)."""

from functools import lru_cache

import pytest

import gbfs_constants as C
import gbfs_evaluation as ev


@lru_cache(maxsize=None)
def _cfg(items):
    return ev.run_config(ev.Settings(), **dict(items))


def cfg(**kw):
    return _cfg(tuple(sorted(kw.items())))


def near(value, expected, tol):
    assert abs(value - expected) <= tol, f"{value:.3f} statt {expected}"


# --- Standardfall ------------------------------------------------------------------------------------------------------------------------------


def test_default_gap_and_ratio():
    row = cfg()
    near(row["gap"], 16.517, 2.0)
    near(row["ratio"], 4.993, 0.6)


# --- Hindernisdichte-Sweep: GEGEN die Vorab-Vermutung ---------------------------------------------------------------------------------------


@pytest.mark.parametrize("obstacle_pct,expected_gap,tol", [(0, 22.117, 3.0), (10, 11.349, 2.5), (20, 12.168, 2.5), (30, 9.851, 3.0), (40, 4.150, 2.0)])
def test_obstacle_sweep_gap_numbers(obstacle_pct, expected_gap, tol):
    row = cfg(obstacle_pct=obstacle_pct)
    near(row["gap"], expected_gap, tol)


def test_gap_shrinks_with_more_obstacles_not_grows():
    """Der zentrale ehrliche Befund: die Vorab-Vermutung 'mehr Hindernisse -> mehr Heuristik-Fallen -> größere
    Lücke' ist FALSCH - gemessen ist es umgekehrt."""
    no_obstacles = cfg(obstacle_pct=0)["gap"]
    many_obstacles = cfg(obstacle_pct=40)["gap"]
    assert no_obstacles > many_obstacles + 5.0


def test_expansion_ratio_also_shrinks_with_more_obstacles():
    no_obstacles = cfg(obstacle_pct=0)["ratio"]
    many_obstacles = cfg(obstacle_pct=40)["ratio"]
    assert no_obstacles > many_obstacles + 2.0


# --- Skalierungs-Sweep: Effizienzvorteil wächst klar mit der Größe -----------------------------------------------------------------------------


@pytest.mark.parametrize("side,expected_ratio,tol", [(6, 2.8, 1.0), (14, 6.018, 1.5), (22, 8.532, 2.0)])
def test_scaling_ratio_numbers(side, expected_ratio, tol):
    row = cfg(side=side)
    near(row["ratio"], expected_ratio, tol)


def test_expansion_ratio_grows_with_grid_size():
    small = cfg(side=6)["ratio"]
    large = cfg(side=22)["ratio"]
    assert large > small + 3.0


# --- Effizienz-Frage: expandiert GBFS wirklich IMMER weniger Knoten? -----------------------------------------------------------------------


def test_gbfs_never_expands_more_nodes_than_ucs_on_the_sweep_instances():
    for obstacle_pct in C.OBSTACLE_SWEEP:
        worse, total = ev.worse_expansion_share(ev.Settings(obstacle_pct=obstacle_pct), seeds=C.SWEEP_SEEDS)
        assert worse == 0, f"obstacle_pct={obstacle_pct}: {worse}/{total} Instanzen mit mehr GBFS-Expansionen"


# --- Handgebaute Heuristik-Falle ----------------------------------------------------------------------------------------------------------------


def test_trap_instance_numbers():
    a = ev.analyse(ev.Settings(network="trap"))
    near(a.gap, 7.468, 0.1)
    assert a.gbfs.expansions == 6 and a.ucs.expansions == 8
    assert a.gbfs.cost > a.ucs.cost


# --- Sonstiges --------------------------------------------------------------------------------------------------------------------------------


def test_preset_count_matches_the_readme():
    assert len(C.PRESETS) == 5


def test_uniform_cost_search_cost_is_always_positive_and_finite_on_sweep_instances():
    for seed in C.SWEEP_SEEDS:
        a = ev.analyse(ev.Settings(seed=seed))
        assert 0 < a.ucs.cost < float("inf")
