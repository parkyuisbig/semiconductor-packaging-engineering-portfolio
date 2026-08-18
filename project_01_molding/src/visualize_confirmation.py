"""Create STEP 7 confirmation and side-effect SVG figures."""

from __future__ import annotations

from html import escape
from pathlib import Path

import numpy as np
import pandas as pd

from visualization import COLORS, H, W, axes, finish, scale, svg_start


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def confirmation_comparison(summary: pd.DataFrame, out: Path) -> None:
    targets = {"edge_void_pct": 0.50, "chip_offset_p95_um": 20.0, "warpage_um": 750.0, "cycle_time_index": 105.0}
    labels = ["Baseline", "Recommended", "Vacuum boundary", "Speed boundary", "Zone outside"]
    conditions = list(summary["condition"])
    colors = [COLORS["red"], COLORS["blue"], COLORS["orange"], COLORS["green"]]
    parts = svg_start("Confirmation conditions versus Engineering Targets", "Normalized mean: value / target; below 1.0 is preferred")
    x0, x1, y0, y1 = axes(parts, 0, 6, 0, 2.4, "Condition", "Normalized CTQ mean")
    target_y = scale(1.0, 0, 2.4, y0, y1)
    parts.append(f'<line x1="{x0}" y1="{target_y}" x2="{x1}" y2="{target_y}" stroke="#334155" stroke-width="2" stroke-dasharray="7 5"/>')
    for i, condition in enumerate(conditions, start=1):
        row = summary.loc[summary["condition"] == condition].iloc[0]
        x = scale(i, 0, 6, x0, x1)
        for j, (response, target) in enumerate(targets.items()):
            value = row[f"{response}_mean"] / target
            xx = x + (j - 1.5) * 14
            y = scale(value, 0, 2.4, y0, y1)
            parts.append(f'<circle cx="{xx:.1f}" cy="{y:.1f}" r="7" fill="{colors[j]}" opacity="0.88"/>')
        parts.append(f'<text class="tick" x="{x}" y="{y0+34}" text-anchor="middle">{escape(labels[i-1])}</text>')
    legends = [("Void", colors[0]), ("Offset", colors[1]), ("Warpage", colors[2]), ("Cycle", colors[3])]
    for j, (label, color) in enumerate(legends):
        lx = 620 + j * 90
        parts.append(f'<circle cx="{lx}" cy="53" r="6" fill="{color}"/><text class="small" x="{lx+12}" y="58">{label}</text>')
    finish(parts, out / "19_confirmation_comparison.svg")


def before_after_p95(summary: pd.DataFrame, out: Path) -> None:
    targets = [("edge_void_pct", "Void", 0.50), ("chip_offset_p95_um", "Offset", 20.0), ("warpage_um", "Warpage", 750.0), ("cycle_time_index", "Cycle", 105.0)]
    baseline = summary.loc[summary["condition"] == "Baseline scenario"].iloc[0]
    rec = summary.loc[summary["condition"] == "Recommended"].iloc[0]
    parts = svg_start("Before versus Recommended P95", "P95 normalized by Engineering Target")
    x0, x1, y0, y1 = axes(parts, 0, 5, 0, 2.6, "CTQ", "P95 / target")
    target_y = scale(1.0, 0, 2.6, y0, y1)
    parts.append(f'<line x1="{x0}" y1="{target_y}" x2="{x1}" y2="{target_y}" stroke="#334155" stroke-width="2" stroke-dasharray="7 5"/>')
    for i, (response, label, target) in enumerate(targets, start=1):
        x = scale(i, 0, 5, x0, x1)
        for row, color, shift in [(baseline, COLORS["gray"], -22), (rec, COLORS["blue"], 22)]:
            value = row[f"{response}_p95"] / target
            y = scale(value, 0, 2.6, y0, y1)
            parts.append(f'<rect x="{x+shift-17}" y="{y}" width="34" height="{y0-y}" fill="{color}" opacity="0.88"/>')
        parts.append(f'<text class="label" x="{x}" y="{y0+38}" text-anchor="middle">{label}</text>')
    finish(parts, out / "20_before_after_p95.svg")


def side_effect_figure(side: pd.DataFrame, out: Path) -> None:
    parts = svg_start("Improvement versus side-effect matrix", "Engineering trade-offs that remain before real-equipment confirmation")
    headers = [(70, "Change"), (315, "Primary benefit"), (575, "Possible side effect")]
    for x, label in headers:
        parts.append(f'<text class="label" x="{x}" y="90">{label}</text>')
    for i, row in enumerate(side.itertuples(index=False)):
        y = 112 + i * 92
        fill = "#F8FAFC" if i % 2 == 0 else "#EFF6FF"
        parts.append(f'<rect x="55" y="{y}" width="890" height="76" rx="6" fill="{fill}" stroke="#CBD5E1"/>')
        parts.append(f'<text class="small" x="70" y="{y+25}">{escape(row.change[:34])}</text>')
        parts.append(f'<text class="small" x="315" y="{y+25}">{escape(row.primary_benefit[:36])}</text>')
        words = row.possible_side_effect
        parts.append(f'<text class="small" x="575" y="{y+24}">{escape(words[:48])}</text>')
        if len(words) > 48:
            parts.append(f'<text class="small" x="575" y="{y+45}">{escape(words[48:96])}</text>')
        parts.append(f'<text class="tick" x="70" y="{y+55}">Check: {escape(row.project_check[:80])}</text>')
    finish(parts, out / "21_side_effect_matrix.svg")


def main() -> None:
    root = project_root()
    summary = pd.read_csv(root / "results" / "confirmation_summary.csv")
    side = pd.read_csv(root / "results" / "side_effect_matrix.csv")
    out = root / "figures"
    confirmation_comparison(summary, out)
    before_after_p95(summary, out)
    side_effect_figure(side, out)
    print("generated 3 STEP 7 SVG figures")


if __name__ == "__main__":
    main()

