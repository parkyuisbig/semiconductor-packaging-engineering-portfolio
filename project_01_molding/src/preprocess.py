"""Validate and join raw project tables into analysis-ready datasets."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> None:
    root = project_root()
    raw = root / "data" / "raw"
    processed = root / "data" / "processed"
    processed.mkdir(parents=True, exist_ok=True)

    shots = pd.read_csv(raw / "process_summary.csv", parse_dates=["timestamp"])
    inspection = pd.read_csv(raw / "inspection_raw.csv")
    trace = pd.read_csv(raw / "sensor_trace.csv")

    if shots["shot_id"].duplicated().any():
        raise ValueError("shot_id must be unique in process_summary")
    if inspection[["shot_id", "die_id"]].duplicated().any():
        raise ValueError("shot_id + die_id must be unique in inspection")
    if not set(inspection["shot_id"]).issubset(set(shots["shot_id"])):
        raise ValueError("inspection contains orphan shot_id")

    inspection["chip_offset_um"] = np.hypot(inspection["dx_um"], inspection["dy_um"])
    inspection["offset_angle_rad"] = np.arctan2(inspection["dy_um"], inspection["dx_um"])
    inspection["edge_band"] = np.where(inspection["radial_norm"] >= 0.90, "Edge", "Center")
    inspection["radial_bin"] = pd.cut(
        inspection["radial_norm"], bins=[0, 0.5, 0.7, 0.8, 0.9, 1.01],
        labels=["0–50%", "50–70%", "70–80%", "80–90%", "90–100%"], include_lowest=True,
    )

    keep = [
        "shot_id", "timestamp", "lot", "wafer", "equipment", "chamber", "emc_lot",
        "floor_time_h", "viscosity_index", "vent_pm_age", "pm_event", "pump_down_time_s",
        "vacuum_base_kpa_abs", "center_temp_c", "edge_temp_c", "zone_range_c",
        "closing_speed_mm_s", "gel_time_s", "fill_time_s", "process_margin_s",
        "film_tension_delta_n", "cycle_time_s", "warpage_um",
    ]
    die_level = inspection.merge(shots[keep], on="shot_id", how="left", validate="many_to_one")

    trace_features = (
        trace.groupby("shot_id", as_index=False)
        .agg(
            trace_vacuum_min_kpa=("vacuum_kpa_abs", "min"),
            trace_temp_range_c=("edge_temp_c", lambda s: float(s.max() - s.min())),
            trace_rows=("elapsed_s", "size"),
        )
    )
    shots = shots.merge(trace_features, on="shot_id", how="left", validate="one_to_one")
    shots["cycle_time_index"] = shots["cycle_time_s"] / shots["cycle_time_s"].median() * 100.0

    shot_ctq = (
        die_level.groupby("shot_id", as_index=False)
        .agg(
            edge_void_pct=("void_area_ratio_pct", lambda s: float(s[die_level.loc[s.index, "edge_band"] == "Edge"].mean())),
            chip_offset_p95_um=("chip_offset_um", lambda s: float(s.quantile(0.95))),
            defect_die_rate_pct=("void_flag", lambda s: float(100 * s.mean())),
        )
    )
    shots = shots.merge(shot_ctq, on="shot_id", how="left", validate="one_to_one")

    die_level.to_csv(processed / "die_level.csv", index=False)
    shots.to_csv(processed / "shot_level.csv", index=False)
    trace.to_csv(processed / "sensor_trace.csv", index=False)
    print(f"processed die_rows={len(die_level)}, shot_rows={len(shots)}")


if __name__ == "__main__":
    main()

