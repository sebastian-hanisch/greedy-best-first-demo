"""Presets: Vollständigkeit, gültige Werte, Optimalitätslücke bleibt in der gemessenen Spannweite über die 5
festen Sweep-Instanzen (kein Ketten-Mittel nötig - diese Suche ist vollständig deterministisch)."""

import pytest

import gbfs_constants as C
import gbfs_evaluation as ev
import gbfs_presets as P


def _settings(p, seed=None):
    return ev.Settings(network=p["network"], side=p["side"], obstacle_pct=p["obstacle_pct"], seed=p["seed"] if seed is None else seed)


def test_every_preset_has_help_and_a_band():
    assert set(C.PRESETS) == set(C.PRESET_HELP) == set(C.PRESET_EXPECTED_BANDS)
    assert len(C.PRESETS) == 5
    for name, p in C.PRESETS.items():
        assert set(p) == set(P.PRESET_KEYS) and C.PRESET_HELP[name]


def test_preset_values_are_valid_and_match_the_setting_specs():
    for p in C.PRESETS.values():
        assert p["network"] in P.NETWORKS
        assert C.SIDE_MIN <= p["side"] <= C.SIDE_MAX
        assert C.OBSTACLE_MIN <= p["obstacle_pct"] <= C.OBSTACLE_MAX


def test_default_preset_equals_the_default_settings():
    assert _settings(C.PRESETS["Standardfall (Voreinstellung)"]) == ev.Settings()


@pytest.mark.parametrize("name", list(C.PRESETS))
def test_preset_gap_stays_in_its_measured_band_over_instances(name):
    p = C.PRESETS[name]
    lo, hi = C.PRESET_EXPECTED_BANDS[name]
    seeds = C.SWEEP_SEEDS if p["network"] == "grid" else (p["seed"],)         # die Falle ignoriert seed/side/obstacle
    for seed in seeds:
        a = ev.analyse(_settings(p, seed=seed))
        assert lo <= a.gap <= hi, (seed, a.gap)


def test_open_field_preset_has_a_larger_mean_gap_than_many_obstacles_preset():
    """Die zentrale, ehrlich gegen die Vorab-Vermutung laufende Erkenntnis: weniger Hindernisse heißt im Mittel
    eine GRÖSSERE Lücke, nicht kleiner."""
    open_field = ev.run_config(_settings(C.PRESETS["Offenes Feld (größte Lücke im Mittel)"]))
    many_obstacles = ev.run_config(_settings(C.PRESETS["Viele Hindernisse (kleinere Lücke im Mittel)"]))
    assert open_field["gap"] > many_obstacles["gap"] + 3.0


def test_large_grid_preset_has_a_clearly_larger_expansion_ratio():
    small = ev.run_config(_settings(C.PRESETS["Standardfall (Voreinstellung)"]))
    large = ev.run_config(_settings(C.PRESETS["Großes Raster (Effizienzvorteil)"]))
    assert large["ratio"] > small["ratio"]


def test_trap_preset_shows_a_real_gap():
    a = ev.analyse(_settings(C.PRESETS["Handgebaute Heuristik-Falle"]))
    assert a.gap > 5.0


def test_bounds_and_permalink_constants():
    assert P.bounds("side_slider") == (C.SIDE_MIN, C.SIDE_MAX)
    assert P.bounds("seed_input") == (0, C.SEED_MAX)
    assert len({spec.url_param for spec in P.SETTING_SPECS.values()}) == len(P.SETTING_SPECS)


def test_network_permalink_roundtrip():
    assert P._network_from_str("trap") == "trap"
    with pytest.raises(ValueError):
        P._network_from_str("nope")
