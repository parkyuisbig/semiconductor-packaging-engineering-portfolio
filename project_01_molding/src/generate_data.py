"""Generate a physics-informed synthetic compression-molding dataset.

The generated records are a project scenario, not real fab data.  Causal links are
explicitly encoded so that engineering hypotheses can be challenged with EDA.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20260818
N_SHOTS = 72
WAFER_RADIUS_MM = 145.0
DIE_PITCH_MM = 14.0


def sigmoid(x: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-x))


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def make_material_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"emc_lot": "M01", "viscosity_index": 0.98, "gel_shift_s": 0.4, "moisture_index": 0.96},
            {"emc_lot": "M02", "viscosity_index": 1.00, "gel_shift_s": 0.0, "moisture_index": 1.00},
            {"emc_lot": "M03", "viscosity_index": 1.13, "gel_shift_s": -1.8, "moisture_index": 1.10},
            {"emc_lot": "M04", "viscosity_index": 1.04, "gel_shift_s": -0.5, "moisture_index": 1.03},
        ]
    )


def die_grid() -> pd.DataFrame:
    coords = np.arange(-140.0, 140.1, DIE_PITCH_MM)
    xx, yy = np.meshgrid(coords, coords)
    grid = pd.DataFrame({"x_mm": xx.ravel(), "y_mm": yy.ravel()})
    grid["radius_mm"] = np.hypot(grid["x_mm"], grid["y_mm"])
    grid = grid.loc[grid["radius_mm"] <= WAFER_RADIUS_MM].copy().reset_index(drop=True)
    grid["die_id"] = [f"D{i:03d}" for i in range(len(grid))]
    grid["radial_norm"] = grid["radius_mm"] / WAFER_RADIUS_MM
    grid["edge_distance_mm"] = WAFER_RADIUS_MM - grid["radius_mm"]
    grid["theta_rad"] = np.arctan2(grid["y_mm"], grid["x_mm"])
    return grid


def make_shot_summary(rng: np.random.Generator, material: pd.DataFrame) -> pd.DataFrame:
    chambers = ["EQ01_C1", "EQ01_C2", "EQ02_C1", "EQ02_C2"]
    material_map = material.set_index("emc_lot").to_dict("index")
    chamber_counts = {name: 0 for name in chambers}
    rows: list[dict] = []

    start = pd.Timestamp("2026-03-02 08:00:00")
    for i in range(N_SHOTS):
        lot_no = i // 6 + 1
        wafer_no = i % 6 + 1
        chamber = chambers[(i + lot_no) % len(chambers)]
        chamber_counts[chamber] += 1
        local_age = chamber_counts[chamber]
        pm_event = int(local_age == 15)
        vent_pm_age = local_age if local_age < 15 else local_age - 14

        emc_lot = ["M01", "M02", "M03", "M04"][(lot_no + wafer_no) % 4]
        mat = material_map[emc_lot]
        floor_time_h = float(np.clip(rng.normal(10.0 + 12.0 * (emc_lot == "M03"), 5.0), 2.0, 38.0))
        exposure_effect = max(floor_time_h - 20.0, 0.0) / 40.0
        viscosity_index = mat["viscosity_index"] + exposure_effect + rng.normal(0, 0.018)

        suspect_chamber = chamber == "EQ02_C2"
        pump_down_time_s = (
            5.2
            + 0.085 * vent_pm_age
            + 0.85 * suspect_chamber
            + 0.25 * (chamber == "EQ01_C2")
            + rng.normal(0, 0.22)
        )
        vacuum_base_kpa_abs = (
            4.2
            + 0.10 * vent_pm_age
            + 0.75 * suspect_chamber
            + 0.22 * (mat["moisture_index"] - 1.0) * 10
            + rng.normal(0, 0.18)
        )
        center_temp_c = 173.0 + rng.normal(0, 0.45)
        zone_range_c = (
            1.4
            + 0.065 * vent_pm_age
            + 1.15 * suspect_chamber
            + rng.normal(0, 0.25)
        )
        zone_range_c = max(zone_range_c, 0.5)
        edge_temp_c = center_temp_c + 0.55 * zone_range_c + rng.normal(0, 0.20)
        closing_speed_mm_s = [0.85, 1.00, 1.15][i % 3]
        gel_time_s = 28.0 - 1.45 * (edge_temp_c - 173.0) + mat["gel_shift_s"] - 0.7 * exposure_effect
        fill_time_s = 8.2 + 4.0 * (viscosity_index - 1.0) - 1.1 * (closing_speed_mm_s - 1.0)
        process_margin_s = gel_time_s - pump_down_time_s - fill_time_s
        film_tension_delta_n = rng.normal(0.25 if chamber == "EQ01_C2" else 0.0, 0.34)
        cycle_time_s = 96.0 + pump_down_time_s + 2.2 / closing_speed_mm_s + rng.normal(0, 0.8)
        warpage_um = (
            740.0
            + 38.0 * zone_range_c
            + 80.0 * (viscosity_index - 1.0)
            + 25.0 * abs(film_tension_delta_n)
            + rng.normal(0, 48.0)
        )

        rows.append(
            {
                "shot_id": f"S{i+1:03d}",
                "timestamp": start + pd.Timedelta(hours=2 * i),
                "lot": f"L{lot_no:02d}",
                "wafer": f"W{wafer_no:02d}",
                "equipment": chamber.split("_")[0],
                "chamber": chamber,
                "emc_lot": emc_lot,
                "floor_time_h": floor_time_h,
                "viscosity_index": viscosity_index,
                "vent_pm_age": vent_pm_age,
                "pm_event": pm_event,
                "pump_down_time_s": pump_down_time_s,
                "vacuum_base_kpa_abs": vacuum_base_kpa_abs,
                "center_temp_c": center_temp_c,
                "edge_temp_c": edge_temp_c,
                "zone_range_c": zone_range_c,
                "closing_speed_mm_s": closing_speed_mm_s,
                "gel_time_s": gel_time_s,
                "fill_time_s": fill_time_s,
                "process_margin_s": process_margin_s,
                "film_tension_delta_n": film_tension_delta_n,
                "cycle_time_s": cycle_time_s,
                "warpage_um": warpage_um,
            }
        )
    return pd.DataFrame(rows)


def make_inspection(rng: np.random.Generator, shots: pd.DataFrame) -> pd.DataFrame:
    grid = die_grid()
    rows: list[pd.DataFrame] = []
    flow_angles = {"EQ01_C1": 0.20, "EQ01_C2": 1.55, "EQ02_C1": 3.15, "EQ02_C2": -0.55}

    for shot in shots.itertuples(index=False):
        d = grid.copy()
        edge = np.clip((d["radial_norm"].to_numpy() - 0.72) / 0.28, 0.0, 1.0)
        theta = d["theta_rad"].to_numpy()
        flow_angle = flow_angles[shot.chamber] + 0.16 * shot.film_tension_delta_n
        directional = np.clip(np.cos(theta - flow_angle), -1.0, 1.0)
        margin_deficit = max(8.3 - shot.process_margin_s, 0.0)
        coupled_risk = sigmoid(
            -1.55
            + 0.58 * margin_deficit
            + 0.24 * (shot.zone_range_c - 2.0)
            + 0.14 * (shot.pump_down_time_s - 6.0) * (shot.zone_range_c - 1.5)
        )
        equipment_risk = 0.018 * shot.vent_pm_age + 0.10 * (shot.chamber == "EQ02_C2")
        material_risk = 0.52 * max(shot.viscosity_index - 1.0, 0.0)

        spatial_multiplier = np.clip(1.0 + 0.34 * directional, 0.45, 1.55)
        mean_void_pct = (
            0.025
            + edge**2.2
            * spatial_multiplier
            * (0.84 + 5.45 * coupled_risk + 2.5 * equipment_risk + 1.7 * material_risk)
        )
        void_noise = rng.gamma(shape=1.6, scale=0.055, size=len(d))
        d["void_area_ratio_pct"] = np.clip(mean_void_pct + void_noise, 0, 5.0)
        d["void_flag"] = (d["void_area_ratio_pct"] > 1.0).astype(int)

        radial_force = edge * (20.0 + 74.0 * coupled_risk + 26.0 * material_risk)
        directional_force = edge * (11.0 + 26.0 * coupled_risk + 15.0 * equipment_risk)
        dx = radial_force * np.cos(theta) + directional_force * np.cos(flow_angle)
        dy = radial_force * np.sin(theta) + directional_force * np.sin(flow_angle)
        dx += 10.0 * shot.film_tension_delta_n + rng.normal(0, 3.5, len(d))
        dy += rng.normal(0, 3.5, len(d))
        d["dx_um"] = dx
        d["dy_um"] = dy
        d["rotation_mdeg"] = rng.normal(0, 8.0 + 10.0 * edge, len(d))
        d["shot_id"] = shot.shot_id
        rows.append(d)

    return pd.concat(rows, ignore_index=True)


def make_sensor_trace(rng: np.random.Generator, shots: pd.DataFrame) -> pd.DataFrame:
    records: list[dict] = []
    time_s = np.linspace(0, 30, 61)
    for shot in shots.itertuples(index=False):
        tau = max(shot.pump_down_time_s / 3.0, 0.8)
        for t in time_s:
            vacuum = shot.vacuum_base_kpa_abs + (101.3 - shot.vacuum_base_kpa_abs) * np.exp(-t / tau)
            vacuum += rng.normal(0, 0.18)
            edge_temp = 165.0 + (shot.edge_temp_c - 165.0) * (1 - np.exp(-t / 5.5)) + rng.normal(0, 0.07)
            center_temp = 165.0 + (shot.center_temp_c - 165.0) * (1 - np.exp(-t / 5.8)) + rng.normal(0, 0.07)
            pressure = max(0.0, 8.5 * (t - 8.0) / 4.0) if 8.0 <= t <= 12.0 else (8.5 if t > 12.0 else 0.0)
            position = min(max((t - 8.0) * shot.closing_speed_mm_s, 0.0), 5.0)
            records.append(
                {
                    "shot_id": shot.shot_id,
                    "elapsed_s": t,
                    "vacuum_kpa_abs": vacuum,
                    "edge_temp_c": edge_temp,
                    "center_temp_c": center_temp,
                    "press_pressure_mpa": pressure,
                    "platen_position_mm": position,
                }
            )
    return pd.DataFrame(records)


def main() -> None:
    rng = np.random.default_rng(SEED)
    root = project_root()
    raw = root / "data" / "raw"
    raw.mkdir(parents=True, exist_ok=True)

    material = make_material_table()
    shots = make_shot_summary(rng, material)
    inspection = make_inspection(rng, shots)
    trace = make_sensor_trace(rng, shots)

    material.to_csv(raw / "material_genealogy.csv", index=False)
    shots.to_csv(raw / "process_summary.csv", index=False)
    inspection.to_csv(raw / "inspection_raw.csv", index=False)
    trace.to_csv(raw / "sensor_trace.csv", index=False)
    print(f"generated shots={len(shots)}, dies={len(inspection)}, trace_rows={len(trace)}")


if __name__ == "__main__":
    main()
