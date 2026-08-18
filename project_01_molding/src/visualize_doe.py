"""Create SVG figures for STEP 4 DOE analysis."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from visualization import COLORS, H, M, W, axes, finish, scale, svg_start


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main_effects(effects: pd.DataFrame, out: Path) -> None:
    terms = ["A_vacuum", "B_zone_range", "C_closing_speed", "D_material_M03", "E_textured"]
    labels = ["Vacuum\nbase P", "Zone\nrange", "Closing\nspeed", "EMC\nM03", "Textured\nsurface"]
    void = effects.loc[(effects["response"] == "edge_void_pct") & effects["term"].isin(terms)].set_index("term")["high_minus_low_effect"]
    offset = effects.loc[(effects["response"] == "chip_offset_p95_um") & effects["term"].isin(terms)].set_index("term")["high_minus_low_effect"]
    v_norm = void / max(void.abs().max(), 1e-9)
    o_norm = offset / max(offset.abs().max(), 1e-9)
    parts = svg_start("DOE main effects", "High − Low effect, normalized within response; positive = worse")
    x0, x1, y0, y1 = axes(parts, 0, 6, -1.1, 1.1, "Factor", "Normalized effect")
    zero = scale(0, -1.1, 1.1, y0, y1)
    parts.append(f'<line x1="{x0}" y1="{zero}" x2="{x1}" y2="{zero}" stroke="#334155" stroke-width="2"/>')
    for i, (term, label) in enumerate(zip(terms, labels), start=1):
        x = scale(i, 0, 6, x0, x1)
        for value, color, shift in [(v_norm[term], COLORS["red"], -19), (o_norm[term], COLORS["blue"], 19)]:
            y = scale(value, -1.1, 1.1, y0, y1)
            top, height = min(y, zero), abs(zero - y)
            parts.append(f'<rect x="{x+shift-15}" y="{top}" width="30" height="{height}" fill="{color}" opacity="0.85"/>')
        lines = label.split("\n")
        parts.append(f'<text class="tick" x="{x}" y="{y0+35}" text-anchor="middle">{lines[0]}</text>')
        parts.append(f'<text class="tick" x="{x}" y="{y0+51}" text-anchor="middle">{lines[1]}</text>')
    parts.append(f'<rect x="720" y="44" width="16" height="12" fill="{COLORS["red"]}"/><text class="small" x="742" y="55">Edge void</text>')
    parts.append(f'<rect x="830" y="44" width="16" height="12" fill="{COLORS["blue"]}"/><text class="small" x="852" y="55">Offset P95</text>')
    finish(parts, out / "09_doe_main_effects.svg")


def interaction(data: pd.DataFrame, out: Path) -> None:
    d = data.loc[data["is_center"] == 0].groupby(["A_vacuum_code", "B_zone_range_code"], as_index=False)["edge_void_pct"].mean()
    parts = svg_start("Vacuum × heater-zone interaction", "Mean edge void across speed/material/roughness")
    ymin, ymax = max(0.0, d["edge_void_pct"].min() * 0.8), d["edge_void_pct"].max() * 1.15
    x0, x1, y0, y1 = axes(parts, -1.2, 1.2, ymin, ymax, "Vacuum base pressure code (−1 better, +1 worse)", "Edge void (%)")
    for zone, color, label in [(-1, COLORS["blue"], "Zone range low"), (1, COLORS["red"], "Zone range high")]:
        z = d.loc[d["B_zone_range_code"] == zone].sort_values("A_vacuum_code")
        points = []
        for row in z.itertuples(index=False):
            x = scale(row.A_vacuum_code, -1.2, 1.2, x0, x1)
            y = scale(row.edge_void_pct, ymin, ymax, y0, y1)
            points.append(f"{x:.1f},{y:.1f}")
            parts.append(f'<circle cx="{x}" cy="{y}" r="7" fill="{color}"/>')
        parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="{color}" stroke-width="4"/>')
        lx = 680 if zone == -1 else 820
        parts.append(f'<line x1="{lx}" y1="55" x2="{lx+23}" y2="55" stroke="{color}" stroke-width="4"/><text class="small" x="{lx+28}" y="60">{label}</text>')
    finish(parts, out / "10_vacuum_zone_interaction.svg")


def roughness_tradeoff(data: pd.DataFrame, out: Path) -> None:
    xmin, xmax = data["chip_offset_p95_um"].min() * 0.9, data["chip_offset_p95_um"].max() * 1.08
    ymin, ymax = 0.0, data["edge_void_pct"].max() * 1.12
    parts = svg_start("Surface roughness trade-off", "Each point is one DOE run")
    x0, x1, y0, y1 = axes(parts, xmin, xmax, ymin, ymax, "Chip offset P95 (μm)", "Edge void (%)")
    for row in data.itertuples(index=False):
        color = COLORS["orange"] if row.film_roughness_class == "Textured" else COLORS["blue"]
        x, y = scale(row.chip_offset_p95_um, xmin, xmax, x0, x1), scale(row.edge_void_pct, ymin, ymax, y0, y1)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{color}" opacity="0.78" stroke="#FFFFFF"/>')
    parts.append(f'<circle cx="720" cy="53" r="7" fill="{COLORS["blue"]}"/><text class="small" x="734" y="58">Smooth</text>')
    parts.append(f'<circle cx="820" cy="53" r="7" fill="{COLORS["orange"]}"/><text class="small" x="834" y="58">Textured</text>')
    finish(parts, out / "11_roughness_tradeoff.svg")


def desirability_chart(ranked: pd.DataFrame, out: Path) -> None:
    top = ranked.head(10).iloc[::-1].copy()
    parts = svg_start("Top multi-response DOE conditions", "Weighted geometric desirability: void/offset ×2, warpage/cycle ×1")
    x0, x1 = 270, 920
    for i, row in enumerate(top.itertuples(index=False)):
        y = 105 + i * 48
        width = (x1 - x0) * row.overall_desirability
        label = f"Run {int(row.run_order):02d} | {row.emc_lot} | {row.film_roughness_class}"
        parts.append(f'<text class="small" x="{x0-12}" y="{y+20}" text-anchor="end">{label}</text>')
        parts.append(f'<rect x="{x0}" y="{y}" width="{width:.1f}" height="28" rx="4" fill="{COLORS["green"]}" opacity="0.84"/>')
        parts.append(f'<text class="small" x="{x0+width+8:.1f}" y="{y+20}">{row.overall_desirability:.3f}</text>')
    finish(parts, out / "12_doe_desirability.svg")


def main() -> None:
    root = project_root()
    out = root / "figures"
    data = pd.read_csv(root / "data" / "processed" / "doe_results.csv")
    effects = pd.read_csv(root / "results" / "doe_effects.csv")
    ranked = pd.read_csv(root / "results" / "doe_ranked_conditions.csv")
    main_effects(effects, out)
    interaction(data, out)
    roughness_tradeoff(data, out)
    desirability_chart(ranked, out)
    print("generated 4 STEP 4 SVG figures")


if __name__ == "__main__":
    main()

