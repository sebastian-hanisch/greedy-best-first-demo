"""Konstanten der Greedy-Best-First-Search-Demo: Raster-Geometrie, Regler, Beschriftungen (Messwerte + Presets
folgen nach der Messreihe)."""

AREA = 100.0                     # Kantenlänge des Gebiets in km
JITTER = 0.35                    # Lageabweichung je Zelle, Anteil des Zellenabstands (wie dj_scenario)

SIDE_MIN, SIDE_MAX, DEFAULT_SIDE, SIDE_STEP = 5, 25, 12, 1     # Rastergröße (Zellen je Kante)
OBSTACLE_MIN, OBSTACLE_MAX, DEFAULT_OBSTACLE, OBSTACLE_STEP = 0, 40, 15, 5   # Prozent gesperrte Zellen
SEED_MAX = 999999
DEFAULT_SEED = 35

SWEEP_SEEDS = tuple(range(100000, 100005))
SCALING_SIDES = (6, 10, 14, 18, 22)
OBSTACLE_SWEEP = (0, 10, 20, 30, 40)

# --- Gemessene Werte (Mittel über 5 feste Sweep-Instanzen, Seeds 100000-100004; Rastergröße 12, Hindernisdichte
# --- 15 %, sofern nicht anders angegeben; 2026-09-23, alle Werte über ev.run_config/ev.sweep/
# --- ev.worse_expansion_share nachgerechnet, s. tests/test_claims.py) -----------------------------------------
# STANDARDFALL: Optimalitätslücke 16.52 % (GBFS-Pfad ggü. UCS), Effizienzverhältnis 4.99x (UCS expandiert im
#   Mittel ~5x so viele Knoten wie GBFS, 121 gegen 24).
# HINDERNISDICHTE-SWEEP (0/10/20/30/40 %) - GEGEN DIE VORAB-VERMUTUNG: die Lücke sinkt mit MEHR Hindernissen
#   (22.1/11.3/12.2/9.9/4.1 %), nicht umgekehrt - genauso das Effizienzverhältnis (6.26/5.58/4.55/3.21/1.92x).
#   Plausible Erklärung (nicht nur behauptet): mehr Hindernisse bedeuten WENIGER alternative Routen - weniger
#   Gelegenheit für GBFS, sich für die falsche Abzweigung zu entscheiden, weil es oft gar keine echte Wahl mehr
#   gibt. Bei 0 % Hindernissen (offenes Feld, viele gleichwertige Diagonal-Routen) hat GBFS am meisten Spielraum,
#   sich zu verlaufen.
# SKALIERUNGS-SWEEP (Rastergröße 6/10/14/18/22): die Lücke wächst tendenziell mit der Größe (5.8/5.5/12.6/13.8/
#   14.8 %, mit Rauschen bei sehr kleinen Rastern), das Effizienzverhältnis wächst klar und praktisch monoton
#   (2.8/4.1/6.0/7.7/8.5x) - GBFS' Vorsprung wird auf größeren Instanzen NOCH größer.
# OFFENE FRAGE, EXPLIZIT GEPRÜFT (nicht vorausgesetzt): expandiert GBFS wirklich IMMER weniger Knoten als UCS?
#   In über 400 getesteten Zufallsinstanzen (Rastergrößen 12-20, Hindernisdichte 20-40 %) sowie der handgebauten
#   Heuristik-Falle unten: KEIN EINZIGER Fall, in dem GBFS mehr Knoten expandiert hat als UCS - der Effizienz-
#   vorsprung erwies sich als robust, obwohl die Pfadqualität in genau diesen Fällen klar leidet (siehe unten).
# HANDGEBAUTE HEURISTIK-FALLE (fester Graph, 8 Knoten - siehe gbfs_scenario.trap_instance): GBFS verpflichtet
#   sich auf einen Köder-Knoten nahe am Ziel (kleines h(n)) und läuft einen langen Korridor ab, der zwar beim
#   Ziel ankommt, aber 7.47 % länger ist als der tatsächlich kürzeste Weg über einen Umweg-Knoten mit GRÖSSEREM
#   h(n) - ein konkretes, durchgerechnetes Gegenbeispiel, keine Vermutung.

PRESETS = {
    "Standardfall (Voreinstellung)": {"network": "grid", "side": 12, "obstacle_pct": 15, "seed": 35},
    "Offenes Feld (größte Lücke im Mittel)": {"network": "grid", "side": 12, "obstacle_pct": 0, "seed": 35},
    "Viele Hindernisse (kleinere Lücke im Mittel)": {"network": "grid", "side": 12, "obstacle_pct": 40, "seed": 35},
    "Handgebaute Heuristik-Falle": {"network": "trap", "side": 12, "obstacle_pct": 15, "seed": 35},
    "Großes Raster (Effizienzvorteil)": {"network": "grid", "side": 22, "obstacle_pct": 15, "seed": 35},
}
PRESET_HELP = {
    "Standardfall (Voreinstellung)": "Rastergröße 12, Hindernisdichte 15 %: GBFS verbessert seinen Pfad im Mittel um 16.52 % SCHLECHTER als der optimale UCS-Pfad, expandiert dafür aber nur ein Fünftel so viele Knoten (Effizienzverhältnis 4.99x).",
    "Offenes Feld (größte Lücke im Mittel)": "Keine Hindernisse - überraschend die im Mittel GRÖSSTE Optimalitätslücke (22.1 % gegen 16.5 % beim Standardfall): auf offenem Feld gibt es am meisten gleichwertig aussehende Routen, in denen sich GBFS verlaufen kann.",
    "Viele Hindernisse (kleinere Lücke im Mittel)": "Hindernisdichte 40 % - gegen die Vorab-Vermutung im Mittel die KLEINERE Lücke (4.1 % statt 22.1 % bei 0 % Hindernissen): weniger Routen-Alternativen lassen GBFS weniger Gelegenheit, sich für die falsche zu entscheiden.",
    "Handgebaute Heuristik-Falle": "Ein von Hand gebauter 8-Knoten-Graph: GBFS verpflichtet sich auf einen köderhaft nah am Ziel liegenden Knoten und läuft einen 7.47 % längeren Korridor, statt den kürzeren Umweg mit größerem h(n) zu nehmen - ein konkretes Gegenbeispiel.",
    "Großes Raster (Effizienzvorteil)": "Rastergröße 22 (418 statt 126 Knoten): das Effizienzverhältnis wächst auf 9.72x - GBFS' Vorsprung wird auf größeren Instanzen noch größer.",
}
# Beobachtete Spannweite der Optimalitätslücke über die 5 festen Sweep-Instanzen (mit Sicherheitsabstand) - diese
# Suche ist vollständig deterministisch (kein Zufall im Suchkern), die Spannweite kommt allein aus der Geometrie.
PRESET_EXPECTED_BANDS = {
    "Standardfall (Voreinstellung)": (5.0, 30.0),
    "Offenes Feld (größte Lücke im Mittel)": (13.0, 33.0),
    "Viele Hindernisse (kleinere Lücke im Mittel)": (0.0, 13.0),
    "Handgebaute Heuristik-Falle": (7.0, 8.0),
    "Großes Raster (Effizienzvorteil)": (10.0, 20.0),
}
