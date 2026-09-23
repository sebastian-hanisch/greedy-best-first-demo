# Greedy Best-First Search – schnell, aber nicht optimal – Streamlit-Demo

Erstes Stück (Wurzel) einer neuen **Heuristische-Baumsuche-Linie** der "Konzepte"-Reihe für die Website "Sebastian Hanisch – Operations Research und Machine Learning" - eine dritte, eigenständige Such-Säule des Portfolios neben der exakten Baumsuche ([branch-bound-demo](../branch-bound-demo)-Familie: vollständig, schrankenbasiertes Pruning) und der populationsbasierten lokalen Verbesserung ([hill-climbing-demo](../hill-climbing-demo)-Familie: vollständige Lösungen werden gestört/rekombiniert): **systematische konstruktive Suche** - Teillösungen werden Schritt für Schritt aufgebaut, informiert durch eine Heuristik, Vollständigkeit bewusst gegen Geschwindigkeit getauscht.

**Einordnung in die Linie:** **Greedy Best-First Search (GBFS)** expandiert in jedem Schritt den einen Knoten, der laut geradliniger Entfernung zum Ziel **h(n)** am vielversprechendsten aussieht - der bislang aufgelaufene Pfadwert **g(n)** fließt NICHT in die Wahl ein, und ein einmal expandierter Knoten wird nie wieder aufgegriffen (kein Backtracking). Vergleichsgröße: **Uniform-Cost-Search** (Dijkstra, Priorität = g(n)) als exakte Referenz - derselbe Suchkern (`_search`), nur eine andere Prioritätsformel, legt die Grundlage für das spätere A*-Stück (Priorität = g(n)+h(n)).

```
Greedy Best-First Search (Wurzel: expandiert IMMER den einen vielversprechendsten Knoten allein nach h(n),
     kein Backtracking - ein einziger irreführender Heuristikwert führt in eine Sackgasse ohne Weg zurück)
                                                                                            [DIESES STÜCK]
 ├─ Beam Search → {Diverse Beam Search, Monobeam}                                          [nicht gebaut]
 ├─ A* → Iterative Deepening A* (IDA*)                                                      [nicht gebaut]
 └─ Monte Carlo Tree Search (MCTS)                                                          [nicht gebaut]
Beam Search + A* → Beam Stack Search (Konvergenzpunkt)                                      [nicht gebaut]
```

Ergebnis in Kürze: **GBFS ist klar effizienter** - im Mittel nur ein Fünftel so viele Knoten-Expansionen wie die optimale Referenz (Effizienzverhältnis 4.99x beim Standardfall, bis 9.72x bei größeren Rastern) - und in über 400 getesteten Instanzen NIE weniger effizient. Aber **die Vorab-Vermutung "mehr Hindernisse = größere Optimalitätslücke" ist FALSCH** - gemessen ist es genau umgekehrt: die Lücke ist am GRÖSSTEN auf offenem Feld (22.1 % im Mittel bei 0 % Hindernissen) und sinkt mit mehr Hindernissen (4.1 % bei 40 %) - weniger Routen-Alternativen lassen GBFS schlicht weniger Gelegenheit, sich für die falsche Abzweigung zu entscheiden.

| Frage | Ergebnis (Rastergröße 12, Hindernisdichte 15 %, sofern nicht anders angegeben; Mittel über 5 feste Instanzen, Seeds 100000–100004; vollständig deterministisch, kein Ketten-Mittel nötig) |
|---|---|
| Standardfall | Optimalitätslücke **16.52 %**, Effizienzverhältnis **4.99x** (24 gegen 121 Expansionen) |
| **Hindernisdichte-Sweep (0/10/20/30/40 %)** | ⚠️ Lücke **22.1/11.3/12.2/9.9/4.1 %** - SINKT mit mehr Hindernissen, nicht umgekehrt |
| **Effizienzverhältnis über denselben Sweep** | ⚠️ **6.26/5.58/4.55/3.21/1.92x** - sinkt ebenfalls |
| **Rastergrößen-Sweep (6/10/14/18/22)** | ✅ Effizienzverhältnis wächst klar: **2.8/4.1/6.0/7.7/8.5x** |
| **Expandiert GBFS wirklich IMMER weniger Knoten?** | ✅ In über 400 Zufallsinstanzen + der handgebauten Falle: KEIN einziger Gegenbeispiel |
| **Handgebaute Heuristik-Falle** | ⚠️ GBFS-Pfad **7.47 %** länger als optimal - konkretes Gegenbeispiel, kein Sweep-Mittel |

## Was die Demo zeigt

1. **GBFS in Aktion** (Schritt-Slider): **Instanz** (Raster mit Hindernissen oder die handgebaute Falle) → **Suche in Aktion** (Schritt-Regler über die Expansionsreihenfolge) → **Ergebnis** (GBFS-Pfad und UCS-Pfad überlagert).
2. **Was die Suche gefunden hat:** Optimalitätslücke, Effizienzverhältnis, Pfadlänge.
3. **📐 Sweeps** über Hindernisdichte und Rastergröße (5 feste Instanzen ab Seed 100000).
4. **🔬 Experiment:** "Expandiert GBFS wirklich IMMER weniger Knoten als UCS?" - direkt geprüft, nicht angenommen.
5. **🚧 Grenzen:** Tabelle "Annahme – was passiert – wer setzt an" (Hindernisdichte-Überraschung, offene Effizienzfrage, fehlende Optimalitätsgarantie, kein Speicherlimit).

Regler: Instanz (Raster / handgebaute Heuristik-Falle), Rastergröße (5–25), Hindernisdichte (0–40 %), Seed der Instanz (+ 🎲). **Kein Bewertungsbudget** (GBFS/UCS laufen bis zum Ziel oder bis die Warteschlange leer ist, kein anytime-Verbesserungs-Sweep wie in der Trajektorien-Metaheuristiken-Linie) und **kein Ketten-Seed** (vollständig deterministisch - kein Zufall im Suchkern selbst, nur in der Instanz-Erzeugung).

## Modell und Verfahren

- **Instanz** (`gbfs_scenario.py`): ein gestörtes Raster (Lagerhaus-/Straßennetz), Start unten links, Ziel oben rechts, Vierer-Nachbarschaft, Kantengewicht = echter euklidischer Abstand der (leicht verschobenen) Zellmittelpunkte - das hält die Heuristik AUTOMATISCH zulässig (Dreiecksungleichung), unabhängig von Hindernissen. Start/Ziel bleiben immer verbunden (bei Bedarf werden einzelne Wände geöffnet, wie bei `dijkstra-demo`s Labyrinth). Zusätzlich eine handgebaute 8-Knoten-Falle (`trap_instance`).
- **Suchkern** (`gbfs_algorithm.py`): EIN gemeinsamer `_search(graph, start, goal, priority_fn, relax)`, daraus `greedy_best_first` (Priorität h(n), `relax=False` - ein Knoten behält für immer seinen ERSTEN gefundenen Elternknoten, echtes "kein Backtracking") und `uniform_cost_search` (Priorität g(n), `relax=True` - klassische Dijkstra-Relaxation, nötig für Optimalität).
- **Auswertung** (`gbfs_evaluation.py`): Optimalitätslücke, Effizienzverhältnis, Sweeps, die "expandiert GBFS immer weniger?"-Prüfung.

## Was nicht funktioniert hat / Grenzen

- **Vorab-Vermutung "mehr Hindernisse = größere Optimalitätslücke" - WIDERLEGT.** Gemessen ist es umgekehrt: die Lücke ist am größten auf offenem Feld (22.1 % im Mittel), wo es die meisten gleichwertig aussehenden Routen gibt, in denen sich GBFS verlaufen kann - und sinkt mit mehr Hindernissen (4.1 % bei 40 %), die die Zahl echter Alternativrouten reduzieren. Eine plausible, aber NICHT vorab angenommene Erklärung.
- **"GBFS expandiert immer weniger Knoten als UCS" ist gemessen, nicht bewiesen.** In über 400 Zufallsinstanzen (Rastergrößen 12-20, Hindernisdichte 20-40 %) sowie der handgebauten Falle: kein einziger Gegenbeweis - aber ein Graph mit genug ineinander verschachtelten Sackgassen könnte das theoretisch umkehren. Offen benannt, nicht verschwiegen.
- **Keine Optimalitätsgarantie**: GBFS kann - selbst mit einer zulässigen Heuristik - einen beliebig schlechteren Pfad finden als den kürzesten. Die zentrale, absichtlich gezeigte Schwäche dieses Stücks, die das nächste Stück (A\*) beheben wird.
- **Kein Speicherlimit modelliert**: die Warteschlange wächst unbegrenzt - auf echten, riesigen Graphen ein echtes Problem (Beam Search fixt das mit fester Breite).
- **Synthetische Instanzen:** ein Raster mit Jitter, Vierer-Nachbarschaft (keine Diagonalen), keine Zeitfenster, keine gerichteten Kanten.

## Verifikation

- **Uniform-Cost-Search ist wirklich optimal**: auf kleinen Instanzen gegen vollständige Enumeration ALLER einfachen Pfade (Brute-Force-DFS) kreuzgeprüft, nicht nur der Formel vertraut.
- **Greedy Best-First Search liefert immer einen gültigen, zusammenhängenden Pfad** (oder meldet korrekt "kein Pfad" bei getrennten Komponenten) - über viele Zufallsinstanzen geprüft.
- **Zurückgegebene Pfadkosten stimmen mit einer unabhängigen Neuberechnung überein.**
- **Die Heuristik ist auf den Instanzen dieses Stücks tatsächlich zulässig** (h(n) ≤ tatsächlicher Restweg) - gegen UCS-Distanzen von jedem Knoten zum Ziel geprüft.
- **Die handgebaute Heuristik-Falle zeigt NACHWEISLICH einen echten Qualitätsunterschied** (GBFS-Pfad strikt länger als der UCS-Pfad) - ein konkretes, durchgerechnetes Gegenbeispiel, keine Vermutung.
- **GBFS findet nie einen kürzeren Pfad als UCS** (UCS ist per Definition optimal) - als Regressionstest über viele Instanzen abgesichert.
- **Determinismus**: derselbe Lauf liefert immer dasselbe Ergebnis (fester Tie-Break über einen monoton steigenden Einfüge-Zähler).
- **Alle Zahlen der App-Texte sind als Tests hinterlegt**, über dieselben Auswertungsfunktionen wie die App selbst (`ev.run_config`/`ev.sweep`/`ev.worse_expansion_share`), NIE über ein Ad-hoc-Skript mit abweichender Zufalls-Bindung; AppTest-Rauchtests (Voreinstellung, jedes Preset, jeder Schritt, beide Instanz-Typen, Extremwerte, Würfel-Knopf, Permalink-Grenzen, ausgeblendete Regler bei der Falle, Sweeps/Experimente auf Abruf, Footer).

## Dateistruktur

| Datei | Zweck |
|---|---|
| `app.py` | Streamlit-App: Instanz-Umschalter, Schritte, Ergebnis, 📐 Sweeps, 🔬 Experiment, 🚧 Grenzen, Mathe |
| `gbfs_algorithm.py` | Gemeinsamer Suchkern, GBFS + UCS als Wrapper mit unterschiedlicher Priorität |
| `gbfs_graph.py` | Schlanke eigene Graph-Repräsentation (Adjazenzlisten + Koordinaten) |
| `gbfs_scenario.py` | Raster-Instanz (mit Hindernissen) + handgebaute Heuristik-Falle |
| `gbfs_constants.py` | Konstanten, Presets, gemessene Werte |
| `gbfs_evaluation.py` | Kennzahlen, Sweeps, "expandiert GBFS immer weniger?"-Prüfung |
| `gbfs_presets.py`, `gbfs_visualization.py` | Permalink/Presets, Plotly-Figuren (Rasterkarte, Schritt-Animation, Pfad-Überlagerung) |
| `tests/` | Zentrale Korrektheitskette (Brute-Force-Kreuzprüfung, Zulässigkeit, Falle), Szenario/Auswertung, Aussagen der App, Presets, AppTest |

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

---

Teil des [Operations-Research-Demo-Portfolios](https://sebastianhanisch.net/demos.html) von
[Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning.
Interesse an einer maßgeschneiderten Lösung? [Kontakt aufnehmen](https://sebastianhanisch.net/kontakt.html).
