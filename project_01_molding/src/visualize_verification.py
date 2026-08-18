"""Create STEP 6 bootstrap, robust-window and evidence SVG figures."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from visualization import COLORS, H, W, axes, color_ramp, finish, scale, svg_start


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def effect_ci(boot: pd.DataFrame, out: Path) -> None:
    terms = ["A_vacuum", "B_zone_range", "C_closing_speed", "A_vacuum:B_zone_range"]
    labels = ["Vacuum base P", "Zone range", "Closing speed", "Vacuum × Zone"]
    d = boot.loc[(boot["response"] == "edge_void_pct") & boot["term"].isin(terms)].set_index("term")
    xmin = min(-0.15, float(d["ci95_low"].min()) - 0.05)
    xmax = float(d["ci95_high"].max()) + 0.12
    parts = svg_start("Bootstrap process effects on Edge Void", "High − Low effect; 95% whole-plot bootstrap interval")
    x0, x1, y0, y1 = axes(parts, xmin, xmax, 0, 5, "Effect on Edge Void (percentage-point)", "")
    zero = scale(0, xmin, xmax, x0, x1)
    parts.append(f'<line x1="{zero}" y1="{y1}" x2="{zero}" y2="{y0}" stroke="#334155" stroke-width="2" stroke-dasharray="7 5"/>')
    for i, (term, label) in enumerate(zip(terms, labels), start=1):
        row = d.loc[term]
        y = scale(i, 0, 5, y1, y0)
        lo, hi = scale(row.ci95_low, xmin, xmax, x0, x1), scale(row.ci95_high, xmin, xmax, x0, x1)
        mean = scale(row.mean_effect, xmin, xmax, x0, x1)
        color = COLORS["blue"] if row.direction_stable else COLORS["orange"]
        parts.append(f'<text class="label" x="{x0+5}" y="{y-14}">{label}</text>')
        parts.append(f'<line x1="{lo}" y1="{y}" x2="{hi}" y2="{y}" stroke="{color}" stroke-width="5"/>')
        parts.append(f'<line x1="{lo}" y1="{y-9}" x2="{lo}" y2="{y+9}" stroke="{color}" stroke-width="2"/>')
        parts.append(f'<line x1="{hi}" y1="{y-9}" x2="{hi}" y2="{y+9}" stroke="{color}" stroke-width="2"/>')
        parts.append(f'<circle cx="{mean}" cy="{y}" r="8" fill="{color}"/>')
    finish(parts, out / "16_bootstrap_effects.svg")


def robust_window(window: pd.DataFrame, out: Path) -> None:
    d = window.loc[
        (window["emc_lot"] == "M02")
        & (window["film_roughness_class"] == "Smooth")
        & (window["closing_speed_mm_s"] == 0.85)
    ].copy()
    vacs = sorted(d["vacuum_base_kpa_abs"].unique())
    zones = sorted(d["zone_range_c"].unique())
    parts = svg_start("MSA-guarded robust process window", "M02 / Smooth / closing speed 0.85 mm/s; green outline = robust pass")
    x0, x1, y0, y1 = 145, 900, 555, 85
    cw, ch = (x1 - x0) / len(vacs), (y0 - y1) / len(zones)
    lo, hi = float(d["primary_margin"].min()), float(d["primary_margin"].max())
    for ix, vacuum in enumerate(vacs):
        for iy, zone in enumerate(zones):
            row = d.loc[(d["vacuum_base_kpa_abs"] == vacuum) & (d["zone_range_c"] == zone)].iloc[0]
            x = x0 + ix * cw
            y = y0 - (iy + 1) * ch
            fill = color_ramp(row["primary_margin"], lo, hi)
            stroke = "#059669" if row["robust_pass"] else "#FFFFFF"
            sw = 4 if row["robust_pass"] else 1
            parts.append(f'<rect x="{x}" y="{y}" width="{cw}" height="{ch}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
    for ix, vacuum in enumerate(vacs):
        if ix % 2 == 0:
            parts.append(f'<text class="tick" x="{x0+(ix+0.5)*cw}" y="{y0+23}" text-anchor="middle">{vacuum:.2f}</text>')
    for iy, zone in enumerate(zones):
        if iy % 2 == 0:
            parts.append(f'<text class="tick" x="{x0-10}" y="{y0-(iy+0.5)*ch+4}" text-anchor="end">{zone:.2f}</text>')
    parts.append(f'<text class="label" x="{(x0+x1)/2}" y="610" text-anchor="middle">Vacuum base pressure (kPa abs)</text>')
    parts.append(f'<text class="label" transform="translate(35 {(y0+y1)/2}) rotate(-90)" text-anchor="middle">Heater zone range (°C)</text>')
    parts.append('<text class="small" x="690" y="64">Color = primary CTQ guard-band margin</text>')
    finish(parts, out / "17_robust_process_window.svg")


def evidence_ladder(evidence: pd.DataFrame, out: Path) -> None:
    scores = {"Strong": 4.0, "Medium-Strong": 3.2, "Medium": 2.4, "Weak-Medium": 1.7, "Reduced": 1.2}
    colors = [COLORS["red"], COLORS["orange"], COLORS["blue"], "#7C3AED", COLORS["gray"], COLORS["green"]]
    parts = svg_start("Root cause evidence ladder", "Strength reflects current synthetic project evidence, not real-fab confirmation")
    x0, x1 = 350, 900
    for i, row in enumerate(evidence.itertuples(index=False)):
        y = 90 + i * 82
        score = scores[row.level]
        width = (x1 - x0) * score / 4.2
        parts.append(f'<text class="label" x="{x0-16}" y="{y+20}" text-anchor="end">#{int(row.rank)} {row.cause}</text>')
        parts.append(f'<rect x="{x0}" y="{y}" width="{width}" height="32" rx="5" fill="{colors[i]}" opacity="0.86"/>')
        parts.append(f'<text class="small" x="{x0+width+8}" y="{y+21}">{row.level}</text>')
        parts.append(f'<text class="tick" x="{x0}" y="{y+49}">{row.scope}</text>')
    finish(parts, out / "18_root_cause_evidence_ladder.svg")


def main() -> None:
    root = project_root()
    boot = pd.read_csv(root / "results" / "bootstrap_effects.csv")
    window = pd.read_csv(root / "results" / "robust_process_window.csv")
    evidence = pd.read_csv(root / "results" / "final_root_cause_evidence.csv")
    out = root / "figures"
    effect_ci(boot, out)
    robust_window(window, out)
    evidence_ladder(evidence, out)
    print("generated 3 STEP 6 SVG figures")


if __name__ == "__main__":
    main()
