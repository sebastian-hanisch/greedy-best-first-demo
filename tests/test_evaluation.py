import gbfs_constants as C
import gbfs_evaluation as EV


def test_analyse_grid_and_trap_both_return_valid_results():
    for network in ("grid", "trap"):
        a = EV.analyse(EV.Settings(network=network, side=10, obstacle_pct=20, seed=1))
        assert a.gbfs.path and a.ucs.path
        assert a.gbfs.path[0] == a.inst.start and a.gbfs.path[-1] == a.inst.goal


def test_gap_is_zero_or_positive_never_negative():
    for seed in range(10):
        a = EV.analyse(EV.Settings(side=10, obstacle_pct=20, seed=seed))
        assert a.gap >= -1e-9


def test_expansion_ratio_is_finite_and_positive():
    for seed in range(10):
        a = EV.analyse(EV.Settings(side=10, obstacle_pct=20, seed=seed))
        assert a.expansion_ratio > 0


def test_run_config_averages_over_the_five_sweep_seeds():
    out = EV.run_config(EV.Settings(), seeds=(1, 2, 3))
    assert out["n_runs"] == 3
    assert out["gap"] >= 0


def test_sweep_returns_one_row_per_value():
    rows = EV.sweep("obstacle_pct", EV.Settings())
    assert [r["value"] for r in rows] == list(C.OBSTACLE_SWEEP)
    rows2 = EV.sweep("side", EV.Settings())
    assert [r["value"] for r in rows2] == list(C.SCALING_SIDES)


def test_worse_expansion_share_is_a_valid_fraction():
    worse, total = EV.worse_expansion_share(EV.Settings(), seeds=C.SWEEP_SEEDS)
    assert 0 <= worse <= total == len(C.SWEEP_SEEDS)


def test_analyse_is_deterministic():
    a1 = EV.analyse(EV.Settings(side=12, obstacle_pct=25, seed=7))
    a2 = EV.analyse(EV.Settings(side=12, obstacle_pct=25, seed=7))
    assert a1.gap == a2.gap and a1.expansion_ratio == a2.expansion_ratio
