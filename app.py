"""Greedy Best-First Search - schnell, aber nicht optimal - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Erstes Stück (Wurzel) der neuen Heuristische-Baumsuche-Linie der "Konzepte"-Reihe - eine dritte, eigenständige
Such-Säule neben der exakten Baumsuche (branch-bound-demo-Familie) und der populationsbasierten lokalen
Verbesserung (Hill-Climbing-Familie): systematische KONSTRUKTIVE Suche, die Vollständigkeit bewusst gegen
Geschwindigkeit tauscht. Greedy Best-First Search expandiert immer den einen Knoten, der laut Heuristik h(n) am
vielversprechendsten aussieht - ohne je den bisherigen Pfadwert g(n) zu berücksichtigen. Das macht die Suche
sehr schnell, aber nicht optimal. Wie groß ist der Qualitätsverlust wirklich, und wovon hängt er ab? Muss
gemessen werden - nicht angenommen.

Lauffähig mit: streamlit run app.py
"""

from dataclasses import replace

import streamlit as st

import gbfs_constants as C
from gbfs_evaluation import SWEEP_LABELS, Settings, analyse, sweep, worse_expansion_share
from gbfs_presets import (
    apply_preset,
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sync_query_params,
)
from gbfs_visualization import build_expansion_step, build_instance, build_paths, build_sweep

st.set_page_config(page_title="Greedy Best-First Search – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner=False)
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _sweep(param, base):
    return sweep(param, base)


@st.cache_data(show_spinner=False)
def _worse_share(base, seeds):
    return worse_expansion_share(base, seeds)


st.title("🧭 Greedy Best-First Search – schnell, aber nicht optimal")
st.markdown(
    """
**Erstes Stück einer neuen Konzepte-Linie: Heuristische Baumsuche** - eine dritte Such-Säule neben der exakten
Baumsuche (`branch-bound-demo`) und der populationsbasierten lokalen Verbesserung (`hill-climbing-demo`):
Teillösungen werden Schritt für Schritt aufgebaut, informiert durch eine Heuristik.

**Greedy Best-First Search (GBFS)** expandiert in jedem Schritt den einen Knoten, der laut geradliniger
Entfernung zum Ziel **h(n)** am vielversprechendsten aussieht - der bislang aufgelaufene Pfadwert **g(n)** fließt
NICHT in die Wahl ein, und ein einmal expandierter Knoten wird nie wieder aufgegriffen (kein Backtracking). Das
macht GBFS sehr schnell - aber NICHT optimal, selbst mit einer zulässigen Heuristik. Wie groß ist der
Qualitätsverlust gegenüber dem Effizienzgewinn wirklich? Und wächst er mit der Hindernisdichte, wie man zunächst
vermuten würde?
"""
)
st.caption(
    "Wurzel der neuen Heuristische-Baumsuche-Linie der \"Konzepte\"-Reihe. Noch nicht gebaute Geschwister: "
    "Beam Search → {Diverse Beam Search, Monobeam}, A* → Iterative Deepening A* (IDA*), Monte Carlo Tree Search "
    "(MCTS), Beam Search + A* → Beam Stack Search (Konvergenzpunkt)."
)

with st.expander("So funktioniert Greedy Best-First Search", expanded=True):
    st.markdown(
        """
1. Eine Prioritätswarteschlange, sortiert AUSSCHLIESSLICH nach h(n) - dem geradlinigen Abstand zum Ziel.
2. Der Knoten mit dem kleinsten h(n) wird als Nächstes expandiert (seine Nachbarn kommen in die Warteschlange).
3. Ein einmal expandierter Knoten wird NIE wieder aufgegriffen, selbst wenn später ein billigerer Weg zu ihm
   gefunden würde - kein Backtracking, Standard-Lehrbuchverhalten.
4. **Vergleichsgröße: Uniform-Cost-Search** (Dijkstra) - derselbe Suchkern, aber Priorität = g(n) statt h(n) -
   findet garantiert den kürzesten Pfad, meist aber deutlich langsamer (mehr Knoten-Expansionen).
        """
    )

st.caption("🎯 Schnellstart – ein Beispielszenario laden:")
preset_names = list(C.PRESETS.keys())
for row in (preset_names[:3], preset_names[3:]):
    if not row:
        continue
    cols = st.columns(len(row))
    for col, name in zip(cols, row):
        with col:
            st.button(name, width="stretch", on_click=apply_preset, args=(name,), help=C.PRESET_HELP.get(name, ""), key=f"preset_{name}")

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    st.header("⚙️ Einstellungen")
    network = st.radio("Instanz", options=["grid", "trap"], format_func=lambda n: "Raster" if n == "grid" else "Handgebaute Heuristik-Falle",
                        key="network_select", horizontal=True, help="Die Falle ist ein fester, von Hand gebauter Graph - Rastergröße/Hindernisdichte/Seed wirken dort nicht.")
    if network == "grid":
        side = st.slider("Rastergröße (Seitenlänge)", *bounds("side_slider"), key="side_slider")
        obstacle_pct = st.slider("Hindernisdichte [%]", *bounds("obstacle_slider"), key="obstacle_slider", step=C.OBSTACLE_STEP,
                                  help="Gegen die naheliegende Vermutung sinkt die Optimalitätslücke im Mittel mit MEHR Hindernissen, nicht umgekehrt - siehe Grenzen.")
        seed = st.number_input("Zufalls-Seed der Instanz", *bounds("seed_input"), key="seed_input", step=1)
        st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)
    else:
        side, obstacle_pct, seed = C.DEFAULT_SIDE, C.DEFAULT_OBSTACLE, C.DEFAULT_SEED

sync_query_params({"network_select": network, "side_slider": int(side), "obstacle_slider": int(obstacle_pct), "seed_input": int(seed)})

settings = Settings(network, int(side), int(obstacle_pct), int(seed))
a = _analysis(settings)
xy = a.inst.graph.xy

# --- GBFS in Aktion --------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 GBFS in Aktion")
STEP_LABELS = {1: "1 · Instanz", 2: "2 · Suche in Aktion", 3: "3 · Ergebnis"}
step = st.select_slider("Schritt", options=list(STEP_LABELS), key="gbfs_step", format_func=lambda s: STEP_LABELS[s])

if step == 1:
    st.markdown(f"**{a.inst.graph.n} Zellen** ({len(a.inst.blocked_xy)} Hindernisse), Start (grün) und Ziel (rot)")
    st.plotly_chart(build_instance(a.inst), width="stretch", key="s1_map")
elif step == 2:
    max_step = len(a.gbfs.order)
    expand_step = st.slider("Expandierte Knoten (GBFS-Reihenfolge)", 0, max_step, max_step, key="expand_step")
    st.plotly_chart(build_expansion_step(a.inst, a.gbfs.order, expand_step), width="stretch", key="s2_map")
    st.caption(f"GBFS expandiert nach h(n) allein - {max_step} Knoten insgesamt bis zum Ziel (UCS bräuchte {a.ucs.expansions}).")
else:
    st.markdown(f"**GBFS**: {a.gbfs.cost:.2f} km ({len(a.gbfs.path)} Knoten) – **UCS (optimal)**: {a.ucs.cost:.2f} km ({len(a.ucs.path)} Knoten) – Lücke **{a.gap:.2f} %**")
    st.plotly_chart(build_paths(a.inst, a.gbfs.path, a.ucs.path), width="stretch", key="s3_map")

st.markdown("---")

# --- Ergebnis --------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Was die Suche gefunden hat")
st.caption("**Optimalitätslücke:** Prozent, um die der GBFS-Pfad länger ist als der optimale UCS-Pfad. **Effizienzverhältnis:** UCS-Expansionen / GBFS-Expansionen (>1 = GBFS effizienter).")
m1, m2, m3 = st.columns(3)
m1.metric("Optimalitätslücke", f"{a.gap:.2f} %")
m2.metric("Effizienzverhältnis", f"{a.expansion_ratio:.2f}x", delta=f"{a.gbfs.expansions} vs. {a.ucs.expansions} Expansionen", delta_color="off")
m3.metric("Pfadlänge (km)", f"{a.gbfs.cost:.2f}", delta=f"UCS-Optimum {a.ucs.cost:.2f}", delta_color="off")

st.markdown("---")

# --- Sweeps ------------------------------------------------------------------------------------------------------------------------------------

if network == "grid":
    st.subheader("📐 Wie stark hängt das Ergebnis von Hindernisdichte und Rastergröße ab?")
    sweep_param = st.selectbox("Welcher Regler soll durchgefahren werden?", list(SWEEP_LABELS), format_func=lambda k: SWEEP_LABELS[k], key="sweep_select")
    metric = st.radio("Kennzahl", options=["gap", "ratio"], format_func=lambda k: "Optimalitätslücke (%)" if k == "gap" else "Effizienzverhältnis (x)", key="sweep_metric", horizontal=True)
    base_sweep = replace(settings, seed=0)
    if st.button("Sweep über 5 feste Instanzen berechnen", key="sweep_start"):
        st.session_state["sweep_done"] = st.session_state.get("sweep_done", set()) | {(sweep_param, base_sweep)}
    if (sweep_param, base_sweep) in st.session_state.get("sweep_done", set()):
        rows_sweep = _sweep(sweep_param, base_sweep)
        label = "Optimalitätslücke (%)" if metric == "gap" else "Effizienzverhältnis (x)"
        st.plotly_chart(build_sweep(rows_sweep, SWEEP_LABELS[sweep_param], metric, label), width="stretch", key="sweep_chart")
        st.caption("Mittel über 5 feste Instanzen (Seeds 100000–100004, getrennt vom Seed oben).")

    st.markdown("---")

    st.subheader("🔬 Expandiert GBFS wirklich IMMER weniger Knoten als UCS?")
    st.caption("Nicht vorausgesetzt - hier direkt geprüft, über die 5 festen Sweep-Instanzen bei der aktuellen Hindernisdichte.")
    if st.button("Prüfen", key="worse_start"):
        st.session_state["worse_on"] = True
    if st.session_state.get("worse_on"):
        worse, total = _worse_share(base_sweep, C.SWEEP_SEEDS)
        if worse == 0:
            st.success(f"In allen {total} geprüften Instanzen hat GBFS NIE mehr Knoten expandiert als UCS.")
        else:
            st.warning(f"In {worse} von {total} Instanzen hat GBFS mehr Knoten expandiert als UCS.")

    st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Mehr Hindernisse bedeuten mehr Heuristik-Fallen** | Gemessen GENAU UMGEKEHRT: die Optimalitätslücke sinkt im Mittel mit mehr Hindernissen (22.1 % bei 0 % Hindernissen, 4.1 % bei 40 %) - weniger Routen-Alternativen lassen GBFS weniger Gelegenheit, sich zu verlaufen. | (kein Nachfolger nötig - eine echte, gemessene Eigenschaft, keine Lücke) |
| **GBFS expandiert immer weniger Knoten als UCS** | In über 400 getesteten Instanzen NIE widerlegt - aber nicht bewiesen, nur gemessen. Ein Graph mit genug Sackgassen könnte es theoretisch umkehren. | (kein Nachfolger nötig - offene, ehrlich benannte Grenze der Messung) |
| **Keine Optimalitätsgarantie** | GBFS kann einen beliebig schlechteren Pfad finden als den kürzesten - die zentrale, absichtlich gezeigte Schwäche dieses Stücks. | **A\\*** (Priorität g(n)+h(n), Optimalitätsgarantie) |
| **Kein Speicherlimit modelliert** | Die Warteschlange wächst unbegrenzt - auf echten, riesigen Graphen ein echtes Problem. | **Beam Search** (feste Breite) |
| **Synthetische Instanzen:** ein Raster mit Jitter, Vierer-Nachbarschaft, keine Zeitfenster, keine gerichteten Kanten. | | |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Heuristik.** $h(n) = \lVert xy_n - xy_{\text{Ziel}} \rVert_2$ - der geradlinige Abstand. Da Kantengewichte
echte euklidische Abstände sind, gilt $h(n) \le$ jedem tatsächlichen Restweg (Dreiecksungleichung) - die
Heuristik ist automatisch zulässig, unabhängig von Hindernissen.

**Greedy Best-First Search.** Priorität eines Knotens $n$: $f(n) = h(n)$ - $g(n)$ (der bisherige Pfadwert)
fließt NICHT ein.

**Uniform-Cost-Search (Dijkstra).** Priorität: $f(n) = g(n)$ - garantiert optimal, aber ohne jede Vorab-Ahnung,
in welche Richtung das Ziel liegt.

**Optimalitätslücke.** $100 \cdot (L_{\text{GBFS}} - L_{\text{UCS}}) / L_{\text{UCS}}$.

**Effizienzverhältnis.** Knoten-Expansionen$_{\text{UCS}}$ / Knoten-Expansionen$_{\text{GBFS}}$.

Implementiert in `gbfs_algorithm.py` (gemeinsamer Suchkern `_search`, GBFS und UCS als Wrapper mit
unterschiedlicher Prioritätsformel), `gbfs_graph.py`/`gbfs_scenario.py` (Graph, Raster- und Fallen-Instanzen),
`gbfs_evaluation.py` (Kennzahlen, Sweeps).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning. Interesse an einer maßgeschneiderten Lösung für "
    "Ihr Unternehmen? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html)"
)
