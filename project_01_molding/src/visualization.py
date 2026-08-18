"""Create dependency-light SVG figures for hypothesis-oriented EDA."""

from __future__ import annotations

from html import escape
from pathlib import Path

import numpy as np
import pandas as pd


W, H = 1000, 650
M = {"left": 105, "right": 55, "top": 75, "bottom": 85}
COLORS = {"blue": "#2563EB", "red": "#DC2626", "orange": "#F59E0B", "green": "#059669", "gray": "#64748B", "ink": "#172033"}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def svg_start(title: str, subtitle: str = "") -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<rect width="100%" height="100%" fill="#FFFFFF"/>',
        '<style>text{font-family:Segoe UI,Arial,sans-serif;fill:#172033}.axis{stroke:#94A3B8;stroke-width:1}.grid{stroke:#E2E8F0;stroke-width:1}.small{font-size:13px}.tick{font-size:12px;fill:#475569}.label{font-size:15px;font-weight:600}.title{font-size:24px;font-weight:700}.subtitle{font-size:13px;fill:#64748B}</style>',
        f'<text class="title" x="{M["left"]}" y="38">{escape(title)}</text>',
        f'<text class="subtitle" x="{M["left"]}" y="59">{escape(subtitle)}</text>',
    ]


def finish(parts: list[str], path: Path) -> None:
    parts.append('</svg>')
    path.write_text("\n".join(parts), encoding="utf-8")


def scale(value: float, lo: float, hi: float, a: float, b: float) -> float:
    if hi == lo:
        return (a + b) / 2
    return a + (value - lo) / (hi - lo) * (b - a)


def color_ramp(value: float, lo: float, hi: float) -> str:
    t = float(np.clip((value - lo) / max(hi - lo, 1e-12), 0, 1))
    stops = [(37, 99, 235), (250, 204, 21), (220, 38, 38)]
    if t < 0.5:
        q = t * 2
        c0, c1 = stops[0], stops[1]
    else:
        q = (t - 0.5) * 2
        c0, c1 = stops[1], stops[2]
    rgb = tuple(round(a + q * (b - a)) for a, b in zip(c0, c1))
    return f"rgb{rgb}"


def axes(parts: list[str], xmin: float, xmax: float, ymin: float, ymax: float, xlabel: str, ylabel: str) -> tuple:
    x0, x1 = M["left"], W - M["right"]
    y0, y1 = H - M["bottom"], M["top"]
    parts += [f'<line class="axis" x1="{x0}" y1="{y0}" x2="{x1}" y2="{y0}"/>', f'<line class="axis" x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}"/>']
    for value in np.linspace(ymin, ymax, 6):
        y = scale(value, ymin, ymax, y0, y1)
        parts.append(f'<line class="grid" x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}"/>')
        parts.append(f'<text class="tick" x="{x0-10}" y="{y+4:.1f}" text-anchor="end">{value:.2g}</text>')
    for value in np.linspace(xmin, xmax, 6):
        x = scale(value, xmin, xmax, x0, x1)
        parts.append(f'<text class="tick" x="{x:.1f}" y="{y0+23}" text-anchor="middle">{value:.2g}</text>')
    parts.append(f'<text class="label" x="{(x0+x1)/2}" y="{H-25}" text-anchor="middle">{escape(xlabel)}</text>')
    parts.append(f'<text class="label" transform="translate(27 {(y0+y1)/2}) rotate(-90)" text-anchor="middle">{escape(ylabel)}</text>')
    return x0, x1, y0, y1


def wafer_maps(die: pd.DataFrame, shots: pd.DataFrame, out: Path) -> None:
    worst_id = shots.sort_values("edge_void_pct", ascending=False).iloc[0]["shot_id"]
    d = die.loc[die["shot_id"] == worst_id].copy()
    cx, cy, radius = 500, 342, 250
    lo, hi = 0.0, max(2.5, float(d["void_area_ratio_pct"].quantile(0.98)))
    parts = svg_start("Worst-shot edge void wafer map", f"{worst_id} | color = void area ratio (%)")
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="#F8FAFC" stroke="#334155" stroke-width="2"/>')
    for row in d.itertuples(index=False):
        x = cx + row.x_mm / 145 * radius
        y = cy - row.y_mm / 145 * radius
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6.2" fill="{color_ramp(row.void_area_ratio_pct,lo,hi)}" opacity="0.90"/>')
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{0.9*radius}" fill="none" stroke="#64748B" stroke-dasharray="6 5"/>')
    for j, val in enumerate(np.linspace(lo, hi, 6)):
        x = 780 + j * 28
        parts.append(f'<rect x="{x}" y="585" width="29" height="14" fill="{color_ramp(val,lo,hi)}"/>')
        if j in (0, 5):
            parts.append(f'<text class="tick" x="{x}" y="620">{val:.1f}%</text>')
    finish(parts, out / "01_worst_shot_void_map.svg")

    parts = svg_start("Chip offset vector map", f"{worst_id} | arrow length scaled for visibility")
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="#F8FAFC" stroke="#334155" stroke-width="2"/>')
    vector_scale = 0.55
    for row in d.itertuples(index=False):
        x = cx + row.x_mm / 145 * radius
        y = cy - row.y_mm / 145 * radius
        x2 = x + row.dx_um * vector_scale
        y2 = y - row.dy_um * vector_scale
        color = COLORS["red"] if row.radial_norm >= 0.9 else COLORS["blue"]
        parts.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" stroke-width="1.5" opacity="0.8"/>')
        parts.append(f'<circle cx="{x2:.1f}" cy="{y2:.1f}" r="1.8" fill="{color}"/>')
    parts.append('<text class="small" x="760" y="590" fill="#DC2626">Red: outer 10% edge band</text>')
    finish(parts, out / "02_chip_offset_vector_map.svg")


def radial_profile(die: pd.DataFrame, out: Path) -> None:
    agg = die.groupby("radial_bin", observed=True, as_index=False).agg(void=("void_area_ratio_pct", "mean"), offset=("chip_offset_um", "mean"), radial=("radial_norm", "mean"))
    parts = svg_start("Radial CTQ profile", "Mean by normalized wafer radius; series normalized to own maximum")
    x0, x1, y0, y1 = axes(parts, 0, 1, 0, 1.05, "Normalized radius", "Normalized response")
    for col, color, label in [("void", COLORS["red"], "Void ratio"), ("offset", COLORS["blue"], "Chip offset")]:
        values = agg[col] / agg[col].max()
        points = []
        for xval, yval in zip(agg["radial"], values):
            x, y = scale(xval, 0, 1, x0, x1), scale(yval, 0, 1.05, y0, y1)
            points.append(f"{x:.1f},{y:.1f}")
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="{color}"/>')
        parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="3"/>')
        lx = 700 if col == "void" else 820
        parts.append(f'<line x1="{lx}" y1="55" x2="{lx+25}" y2="55" stroke="{color}" stroke-width="3"/><text class="small" x="{lx+31}" y="60">{label}</text>')
    finish(parts, out / "03_radial_profile.svg")


def boxplot(frame: pd.DataFrame, group: str, value: str, title: str, subtitle: str, filename: str, out: Path) -> None:
    groups = sorted(frame[group].unique())
    ymin, ymax = float(frame[value].min()) * 0.9, float(frame[value].max()) * 1.05
    parts = svg_start(title, subtitle)
    x0, x1, y0, y1 = axes(parts, 0, len(groups) + 1, ymin, ymax, "", value.replace("_", " "))
    for i, name in enumerate(groups, start=1):
        vals = frame.loc[frame[group] == name, value]
        q1, med, q3 = vals.quantile([0.25, 0.5, 0.75])
        low, high = vals.quantile([0.05, 0.95])
        x = scale(i, 0, len(groups) + 1, x0, x1)
        yy = lambda v: scale(float(v), ymin, ymax, y0, y1)
        parts.append(f'<line x1="{x}" y1="{yy(low)}" x2="{x}" y2="{yy(high)}" stroke="#475569"/>')
        parts.append(f'<rect x="{x-35}" y="{yy(q3)}" width="70" height="{yy(q1)-yy(q3)}" fill="#DBEAFE" stroke="{COLORS["blue"]}" stroke-width="2"/>')
        parts.append(f'<line x1="{x-35}" y1="{yy(med)}" x2="{x+35}" y2="{yy(med)}" stroke="{COLORS["red"]}" stroke-width="3"/>')
        parts.append(f'<text class="tick" x="{x}" y="{y0+45}" text-anchor="middle">{escape(str(name))}</text>')
    finish(parts, out / filename)


def time_trend(shots: pd.DataFrame, out: Path) -> None:
    d = shots.loc[shots["chamber"] == "EQ02_C2"].sort_values("timestamp").reset_index(drop=True)
    parts = svg_start("Suspect chamber time / PM-age trend", "EQ02_C2; each series normalized to 0–1")
    x0, x1, y0, y1 = axes(parts, 1, len(d), 0, 1.05, "Sequential shot in chamber", "Normalized response")
    for col, color, label in [("edge_void_pct", COLORS["red"], "Edge void"), ("pump_down_time_s", COLORS["blue"], "Pump-down"), ("vent_pm_age", COLORS["orange"], "PM age")]:
        vals = d[col]
        norm = (vals - vals.min()) / max(vals.max() - vals.min(), 1e-9)
        points = []
        for i, val in enumerate(norm, start=1):
            points.append(f"{scale(i,1,len(d),x0,x1):.1f},{scale(val,0,1.05,y0,y1):.1f}")
        parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="3"/>')
        lx = 600 + [("edge_void_pct", 0), ("pump_down_time_s", 115), ("vent_pm_age", 245)][[x[0] for x in [("edge_void_pct",0),("pump_down_time_s",115),("vent_pm_age",245)]].index(col)][1]
        parts.append(f'<line x1="{lx}" y1="55" x2="{lx+22}" y2="55" stroke="{color}" stroke-width="3"/><text class="small" x="{lx+27}" y="60">{label}</text>')
    finish(parts, out / "05_time_trend.svg")


def interaction_scatter(shots: pd.DataFrame, out: Path) -> None:
    xmin, xmax = shots["pump_down_time_s"].min() * 0.97, shots["pump_down_time_s"].max() * 1.03
    ymin, ymax = 0.0, shots["edge_void_pct"].max() * 1.12
    parts = svg_start("Vacuum × thermal interaction", "Color = heater zone range (°C)")
    x0, x1, y0, y1 = axes(parts, xmin, xmax, ymin, ymax, "Pump-down time (s)", "Edge void area ratio (%)")
    clo, chi = shots["zone_range_c"].min(), shots["zone_range_c"].max()
    for row in shots.itertuples(index=False):
        x, y = scale(row.pump_down_time_s, xmin, xmax, x0, x1), scale(row.edge_void_pct, ymin, ymax, y0, y1)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{color_ramp(row.zone_range_c,clo,chi)}" opacity="0.78" stroke="#FFFFFF"/>')
    parts.append(f'<text class="small" x="700" y="58">Zone range: {clo:.1f} → {chi:.1f} °C</text>')
    finish(parts, out / "06_vacuum_thermal_interaction.svg")


def evidence_chart(out: Path) -> None:
    labels = ["H1 Thermo-rheology × vacuum", "H2 Vacuum/Vent equipment", "H3 EMC material history", "Measurement confounder"]
    scores = [4.0, 3.2, 2.3, 1.0]
    parts = svg_start("Root cause evidence ranking", "EDA evidence only — causal verification is still required")
    x0, x1 = 330, 910
    for i, (label, score) in enumerate(zip(labels, scores)):
        y = 130 + i * 105
        parts.append(f'<text class="label" x="{x0-18}" y="{y+21}" text-anchor="end">{escape(label)}</text>')
        parts.append(f'<rect x="{x0}" y="{y}" width="{(x1-x0)*score/4.2:.1f}" height="36" rx="5" fill="{[COLORS["red"],COLORS["orange"],COLORS["blue"],COLORS["gray"]][i]}"/>')
        parts.append(f'<text class="label" x="{x0+(x1-x0)*score/4.2+10:.1f}" y="{y+24}">{score:.1f}</text>')
    parts.append('<text class="subtitle" x="330" y="585">Scale: 1 Unverified · 2 Weak/Medium · 3 Medium-Strong · 4 Strong</text>')
    finish(parts, out / "08_evidence_ranking.svg")


def main() -> None:
    root = project_root()
    processed = root / "data" / "processed"
    out = root / "figures"
    out.mkdir(parents=True, exist_ok=True)
    die = pd.read_csv(processed / "die_level.csv")
    shots = pd.read_csv(processed / "shot_level.csv", parse_dates=["timestamp"])
    wafer_maps(die, shots, out)
    radial_profile(die, out)
    boxplot(shots, "chamber", "edge_void_pct", "Chamber comparison", "Distribution of shot-level edge void", "04_chamber_boxplot.svg", out)
    time_trend(shots, out)
    interaction_scatter(shots, out)
    boxplot(shots, "emc_lot", "edge_void_pct", "EMC material-lot comparison", "Material genealogy effect", "07_material_lot_boxplot.svg", out)
    evidence_chart(out)
    print("generated 8 SVG figures")


if __name__ == "__main__":
    main()

