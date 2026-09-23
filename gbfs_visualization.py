"""Plotly-Abbildungen: Rasterkarte (Hindernisse, Start/Ziel), Schritt-Visualisierung der Expansionsreihenfolge,
Pfad-Überlagerung (GBFS gegen UCS), Sweeps. Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen
nicht zoomen."""

import numpy as np
import plotly.graph_objects as go

NODE_COLOR = "#4c78a8"
BLOCKED_COLOR = "#9d755d"
GBFS_COLOR = "#e45756"
UCS_COLOR = "#54a24b"
EXPANDED_COLOR = "#f58518"


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.1), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def _map_layout(fig, xy, height=460):
    pad = max(1.0, (xy[:, 0].max() - xy[:, 0].min()) * 0.06) if len(xy) else 1.0
    fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="y", scaleratio=1)
    fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False)
    return _base(fig, height)


def _start_goal_trace(inst):
    xy = inst.graph.xy
    return [
        go.Scatter(x=[xy[inst.start, 0]], y=[xy[inst.start, 1]], mode="markers", marker=dict(size=16, symbol="star", color="#2ca02c", line=dict(width=1, color="white")), name="Start"),
        go.Scatter(x=[xy[inst.goal, 0]], y=[xy[inst.goal, 1]], mode="markers", marker=dict(size=16, symbol="star", color="#d62728", line=dict(width=1, color="white")), name="Ziel"),
    ]


def build_instance(inst):
    xy = inst.graph.xy
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="markers", marker=dict(size=6, color=NODE_COLOR, line=dict(width=1, color="white")), name="Offene Zellen"))
    if len(inst.blocked_xy):
        fig.add_trace(go.Scatter(x=inst.blocked_xy[:, 0], y=inst.blocked_xy[:, 1], mode="markers", marker=dict(size=6, symbol="square", color=BLOCKED_COLOR), name="Hindernis"))
    fig.add_traces(_start_goal_trace(inst))
    return _map_layout(fig, xy)


def build_expansion_step(inst, order, step):
    xy = inst.graph.xy
    expanded = set(order[:step])
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="markers", marker=dict(size=6, color=NODE_COLOR, line=dict(width=1, color="white")), name="Noch nicht expandiert"))
    if len(inst.blocked_xy):
        fig.add_trace(go.Scatter(x=inst.blocked_xy[:, 0], y=inst.blocked_xy[:, 1], mode="markers", marker=dict(size=6, symbol="square", color=BLOCKED_COLOR), name="Hindernis"))
    if expanded:
        idx = np.array(sorted(expanded))
        fig.add_trace(go.Scatter(x=xy[idx, 0], y=xy[idx, 1], mode="markers", marker=dict(size=8, color=EXPANDED_COLOR, line=dict(width=1, color="white")), name="Bereits expandiert"))
    fig.add_traces(_start_goal_trace(inst))
    return _map_layout(fig, xy)


def build_paths(inst, gbfs_path, ucs_path):
    xy = inst.graph.xy
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xy[:, 0], y=xy[:, 1], mode="markers", marker=dict(size=5, color="rgba(76,120,168,0.35)"), name="Zellen", hoverinfo="skip"))
    if len(inst.blocked_xy):
        fig.add_trace(go.Scatter(x=inst.blocked_xy[:, 0], y=inst.blocked_xy[:, 1], mode="markers", marker=dict(size=6, symbol="square", color=BLOCKED_COLOR), name="Hindernis"))
    if ucs_path:
        p = xy[ucs_path]
        fig.add_trace(go.Scatter(x=p[:, 0], y=p[:, 1], mode="lines+markers", line=dict(color=UCS_COLOR, width=3), marker=dict(size=5, color=UCS_COLOR), name=f"UCS (optimal, {len(ucs_path)} Knoten)"))
    if gbfs_path:
        p = xy[gbfs_path]
        fig.add_trace(go.Scatter(x=p[:, 0], y=p[:, 1], mode="lines+markers", line=dict(color=GBFS_COLOR, width=3, dash="dot"), marker=dict(size=5, color=GBFS_COLOR), name=f"GBFS ({len(gbfs_path)} Knoten)"))
    fig.add_traces(_start_goal_trace(inst))
    return _map_layout(fig, xy)


def build_sweep(rows, param_label, key, y_label, color=GBFS_COLOR):
    xs = [r["value"] for r in rows]
    ys = [r[key] for r in rows]
    sd = [r[f"{key}_sd"] for r in rows]
    upper = [y + s for y, s in zip(ys, sd)]
    lower = [max(0.0, y - s) for y, s in zip(ys, sd)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs + xs[::-1], y=upper + lower[::-1], fill="toself", fillcolor="rgba(228,87,86,0.15)", line=dict(width=0), showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines+markers", line=dict(color=color, width=2.5), name=y_label))
    fig.update_xaxes(title_text=param_label)
    fig.update_yaxes(title_text=y_label)
    return _base(fig, 360)
