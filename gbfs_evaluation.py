"""Auswertung: Greedy Best-First Search (GBFS) gegen Uniform-Cost-Search (UCS, die exakte Referenz) - derselbe
Graph, derselbe Suchkern, nur eine andere Prioritätsformel (siehe `gbfs_algorithm.py`). Zwei Kennzahlen, kein
Bewertungsbudget: **Optimalitätslücke** (Pfadlänge GBFS ggü. UCS, in %) und **Effizienzverhältnis**
(Knoten-Expansionen UCS / GBFS, >1 heißt GBFS effizienter) - ein Zwei-Achsen-Kompromiss, keine
anytime-Budget-Kurve wie in der Trajektorien-Metaheuristiken-Linie. Vollständig deterministisch (kein Zufall im
Suchkern selbst, nur in der Instanz-Erzeugung) - kein Ketten-Seed-Regler."""

from dataclasses import dataclass, replace
from functools import lru_cache

import numpy as np

import gbfs_algorithm as A
import gbfs_constants as C
import gbfs_scenario as S


@dataclass(frozen=True)
class Settings:
    network: str = "grid"           # "grid" oder "trap" (die handgebaute Sackgassen-Instanz)
    side: int = C.DEFAULT_SIDE
    obstacle_pct: int = C.DEFAULT_OBSTACLE
    seed: int = C.DEFAULT_SEED


@lru_cache(maxsize=256)
def instance(side, obstacle_pct, seed):
    return S.grid_instance(side, obstacle_pct, seed)


@dataclass
class Analysis:
    settings: Settings
    inst: object
    gbfs: A.SearchResult
    ucs: A.SearchResult

    @property
    def gap(self):
        """Optimalitätslücke: Prozent, um die der GBFS-Pfad länger ist als der optimale UCS-Pfad."""
        if not self.ucs.path or self.ucs.cost <= 0:
            return 0.0
        return 100.0 * (self.gbfs.cost - self.ucs.cost) / self.ucs.cost

    @property
    def expansion_ratio(self):
        """>1: GBFS expandiert weniger Knoten als UCS (effizienter); <1: umgekehrt."""
        if self.gbfs.expansions <= 0:
            return float("nan")
        return self.ucs.expansions / self.gbfs.expansions


def analyse(settings):
    inst = S.trap_instance() if settings.network == "trap" else instance(settings.side, settings.obstacle_pct, settings.seed)
    gbfs = A.greedy_best_first(inst.graph, inst.start, inst.goal)
    ucs = A.uniform_cost_search(inst.graph, inst.start, inst.goal)
    return Analysis(settings, inst, gbfs, ucs)


# --- Sweeps --------------------------------------------------------------------------------------------------------------------------------------


def run_config(base, seeds=C.SWEEP_SEEDS, **changes):
    s0 = replace(base, **changes)
    rows = [analyse(replace(s0, seed=seed)) for seed in seeds]
    gaps = [r.gap for r in rows]
    ratios = [r.expansion_ratio for r in rows]
    return {
        "gap": float(np.mean(gaps)), "gap_sd": float(np.std(gaps)),
        "ratio": float(np.mean(ratios)), "ratio_sd": float(np.std(ratios)),
        "expansions_gbfs": float(np.mean([r.gbfs.expansions for r in rows])),
        "expansions_ucs": float(np.mean([r.ucs.expansions for r in rows])),
        "n_runs": len(rows),
    }


SWEEP_VALUES = {"obstacle_pct": C.OBSTACLE_SWEEP, "side": C.SCALING_SIDES}
SWEEP_LABELS = {"obstacle_pct": "Hindernisdichte (%)", "side": "Rastergröße (Seitenlänge)"}


def sweep(param, base=Settings(), values=None):
    values = SWEEP_VALUES[param] if values is None else values
    return [{"value": v, **run_config(base, **{param: v})} for v in values]


def worse_expansion_share(base=Settings(), seeds=C.SWEEP_SEEDS):
    """Anteil der Instanzen, in denen GBFS MEHR Knoten expandiert als UCS - die offene Frage aus dem Plan, nicht
    vorausgesetzt: expandiert GBFS wirklich IMMER weniger Knoten? Gibt (Anzahl schlechter, Gesamtzahl) zurück."""
    rows = [analyse(replace(base, seed=seed)) for seed in seeds]
    worse = sum(1 for r in rows if r.gbfs.expansions > r.ucs.expansions)
    return worse, len(rows)
