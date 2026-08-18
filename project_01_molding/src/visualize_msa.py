"""Create SVG figures for STEP 5 measurement-system analysis."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from visualization import COLORS, H, axes, finish, scale, svg_start


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def grr_bars(summary: pd.DataFrame, out: Path) -> None:
    order = ["Edge Void Area Ratio (%)", "Chip Offset (um)", "Surface Roughness Ra (um)"]
    labels = ["Edge Void", "Chip Offset", "Surface Ra"]
    parts = svg_start("Measurement GR&R before / after recipe lock", "%Tolerance = 6σGRR / Engineering tolerance × 100")
    x0, x1, y0, y1 = axes(parts, 0, 4, 0, 55, "Measurement", "% Engineering tolerance")
    for threshold, color in [(10, "#059669"), (30, "#DC2626")]:
        y = scale(threshold, 0, 55, y0, y1)
        parts.append(f'<line x1="{x0}" y1="{y}" x2="{x1}" y2="{y}" stroke="{color}" stroke-width="2" stroke-dasharray="7 5"/>')
        parts.append(f'<text class="small" x="{x1-5}" y="{y-6}" text-anchor="end">{threshold}% project rule</text>')
    for i, (metric, label) in enumerate(zip(order, labels), start=1):
        x = scale(i, 0, 4, x0, x1)
        for phase, color, shift in [("Before recipe lock", COLORS["gray"], -24), ("After recipe lock", COLORS["blue"], 24)]:
            value = summary.loc[(summary["metric"] == metric) & (summary["phase"] == phase), "pct_tolerance_6sigma"].iloc[0]
            y = scale(value, 0, 55, y0, y1)
            parts.append(f'<rect x="{x+shift-19}" y="{y}" width="38" height="{y0-y}" fill="{color}" opacity="0.88"/>')
            parts.append(f'<text class="tick" x="{x+shift}" y="{y-6}" text-anchor="middle">{value:.1f}</text>')
        parts.append(f'<text class="label" x="{x}" y="{y0+42}" text-anchor="middle">{label}</text>')
    parts.append(f'<rect x="730" y="45" width="16" height="12" fill="{COLORS["gray"]}"/><text class="small" x="752" y="56">Before</text>')
    parts.append(f'<rect x="825" y="45" width="16" height="12" fill="{COLORS["blue"]}"/><text class="small" x="847" y="56">After</text>')
    finish(parts, out / "13_grr_before_after.svg")


def operator_bias(data: pd.DataFrame, out: Path) -> None:
    d = data.copy()
    d["normalized_error_pct_tol"] = 100 * (d["measured_value"] - d["reference_value"]) / d["engineering_tolerance"]
    agg = d.groupby(["phase", "operator"], as_index=False)["normalized_error_pct_tol"].mean()
    parts = svg_start("Operator / recipe normalized bias", "Mean measurement error across three CTQs, normalized by tolerance")
    x0, x1, y0, y1 = axes(parts, 0, 4, -5, 5, "Operator / recipe", "Mean error (% tolerance)")
    zero = scale(0, -5, 5, y0, y1)
    parts.append(f'<line x1="{x0}" y1="{zero}" x2="{x1}" y2="{zero}" stroke="#334155" stroke-width="2"/>')
    for i, op in enumerate(["OP_A", "OP_B", "OP_C"], start=1):
        x = scale(i, 0, 4, x0, x1)
        for phase, color, shift in [("Before recipe lock", COLORS["gray"], -22), ("After recipe lock", COLORS["blue"], 22)]:
            value = agg.loc[(agg["operator"] == op) & (agg["phase"] == phase), "normalized_error_pct_tol"].iloc[0]
            y = scale(value, -5, 5, y0, y1)
            top, height = min(y, zero), abs(zero - y)
            parts.append(f'<rect x="{x+shift-16}" y="{top}" width="32" height="{height}" fill="{color}" opacity="0.88"/>')
        parts.append(f'<text class="label" x="{x}" y="{y0+40}" text-anchor="middle">{op}</text>')
    finish(parts, out / "14_operator_bias.svg")


def void_agreement(data: pd.DataFrame, out: Path) -> None:
    d = data.loc[data["metric"] == "Edge Void Area Ratio (%)"].copy()
    xmin, xmax = 0, 1.2
    ymin, ymax = 0, 1.2
    parts = svg_start("Edge Void measurement agreement", "Reference versus measured value; recipe lock reduces spread")
    x0, x1, y0, y1 = axes(parts, xmin, xmax, ymin, ymax, "Reference void ratio (%)", "Measured void ratio (%)")
    parts.append(f'<line x1="{scale(xmin,xmin,xmax,x0,x1)}" y1="{scale(ymin,ymin,ymax,y0,y1)}" x2="{scale(xmax,xmin,xmax,x0,x1)}" y2="{scale(ymax,ymin,ymax,y0,y1)}" stroke="#334155" stroke-width="2" stroke-dasharray="7 5"/>')
    for row in d.itertuples(index=False):
        color = COLORS["gray"] if row.phase == "Before recipe lock" else COLORS["blue"]
        x = scale(row.reference_value, xmin, xmax, x0, x1)
        y = scale(row.measured_value, ymin, ymax, y0, y1)
        parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}" opacity="0.50"/>')
    parts.append(f'<circle cx="750" cy="53" r="6" fill="{COLORS["gray"]}"/><text class="small" x="763" y="58">Before</text>')
    parts.append(f'<circle cx="840" cy="53" r="6" fill="{COLORS["blue"]}"/><text class="small" x="853" y="58">After</text>')
    finish(parts, out / "15_void_measurement_agreement.svg")


def main() -> None:
    root = project_root()
    data = pd.read_csv(root / "data" / "raw" / "measurement_study.csv")
    summary = pd.read_csv(root / "results" / "msa_summary.csv")
    out = root / "figures"
    grr_bars(summary, out)
    operator_bias(data, out)
    void_agreement(data, out)
    print("generated 3 STEP 5 SVG figures")


if __name__ == "__main__":
    main()

