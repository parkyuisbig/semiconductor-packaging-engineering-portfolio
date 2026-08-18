"""Attach physics-informed project-scenario responses to the STEP 3 DOE.

Coefficients are intentionally project-specific and must not be represented as fab
recipe values or material constants.  Published models support causal direction;
actual coefficients would require DSC, rheology, wetting and shear measurements.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20260818


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sigmoid(x: float) -> float:
    return float(1.0 / (1.0 + np.exp(-x)))


def simulate_row(row: pd.Series, rng: np.random.Generator) -> dict:
    suspect_material = int(row["emc_lot"] == "M03")
    textured = int(row["film_roughness_class"] == "Textured")

    vacuum = float(row["vacuum_base_kpa_abs"] + rng.normal(0, 0.10))
    zone = float(row["zone_range_c"] + rng.normal(0, 0.09))
    speed = float(row["closing_speed_mm_s"] + rng.normal(0, 0.012))
    ra = float(row["film_Ra_um_project_scenario"] + rng.normal(0, 0.025))
    rz = float(5.1 * ra + rng.normal(0, 0.12))

    viscosity_index = 1.00 + 0.13 * suspect_material + rng.normal(0, 0.012)
    gel_time_s = 27.2 - 1.55 * (zone - 1.5) - 2.0 * suspect_material + rng.normal(0, 0.22)
    vacuum_time_s = 5.0 + 0.82 * (vacuum - 4.5) + rng.normal(0, 0.12)
    fill_time_s = 8.0 + 3.0 * (viscosity_index - 1.0) - 1.0 * (speed - 1.0) + rng.normal(0, 0.10)
    process_margin_s = gel_time_s - vacuum_time_s - fill_time_s
    cure_flow_risk = sigmoid(0.82 * (10.6 - process_margin_s))

    # Project-scenario interface proxies: texture improves shear holding but can
    # worsen apparent wetting/thermal contact. Direction is deliberately a trade-off.
    contact_angle_deg = 62.0 + 13.0 * textured + 3.5 * suspect_material + rng.normal(0, 1.2)
    interface_shear_mpa = 6.5 + 2.1 * textured - 0.35 * suspect_material + rng.normal(0, 0.20)
    thermal_contact_penalty_c = 0.15 + 0.55 * textured + 0.18 * suspect_material

    wetting_penalty = max(contact_angle_deg - 60.0, 0.0) / 20.0
    edge_void_pct = (
        0.18
        + 2.10 * cure_flow_risk
        + 0.42 * wetting_penalty
        + 0.28 * (speed - 0.85) / 0.30
        + 0.20 * cure_flow_risk * textured
        + rng.normal(0, 0.075)
    )
    edge_void_pct = max(edge_void_pct, 0.05)

    flow_load_index = (
        14.0
        + 10.0 * cure_flow_risk
        + 12.0 * (speed - 0.85)
        + 2.0 * (zone - 1.5)
        + 2.5 * suspect_material
    )
    shift_safety_factor = interface_shear_mpa * 4.8 / flow_load_index
    chip_offset_p95_um = 5.0 + 6.0 * flow_load_index / interface_shear_mpa + rng.normal(0, 1.1)

    warpage_um = (
        650.0
        + 60.0 * (zone - 1.5)
        + 38.0 * suspect_material
        + 32.0 * thermal_contact_penalty_c
        + 18.0 * cure_flow_risk
        + rng.normal(0, 17.0)
    )
    cycle_time_index = (
        100.0
        + 2.0 * (5.5 - vacuum)
        + 2.0 * (1.0 - speed) / 0.15
        + rng.normal(0, 0.45)
    )

    return {
        "actual_vacuum_base_kpa_abs": vacuum,
        "actual_zone_range_c": zone,
        "actual_closing_speed_mm_s": speed,
        "measured_Ra_um": ra,
        "measured_Rz_um": rz,
        "contact_angle_deg": contact_angle_deg,
        "interface_shear_mpa": interface_shear_mpa,
        "viscosity_index": viscosity_index,
        "gel_time_s": gel_time_s,
        "vacuum_time_s": vacuum_time_s,
        "fill_time_s": fill_time_s,
        "process_margin_s": process_margin_s,
        "cure_flow_risk": cure_flow_risk,
        "flow_load_index": flow_load_index,
        "shift_safety_factor": shift_safety_factor,
        "edge_void_pct": edge_void_pct,
        "chip_offset_p95_um": chip_offset_p95_um,
        "warpage_um": warpage_um,
        "cycle_time_index": cycle_time_index,
    }


def main() -> None:
    root = project_root()
    source = pd.read_csv(root / "results" / "doe_run_matrix.csv")
    rng = np.random.default_rng(SEED)
    simulated = pd.DataFrame([simulate_row(row, rng) for _, row in source.iterrows()])
    drop_placeholders = ["edge_void_pct", "chip_offset_p95_um", "warpage_um", "cycle_time_s"]
    result = pd.concat([source.drop(columns=drop_placeholders), simulated], axis=1)
    result.to_csv(root / "data" / "processed" / "doe_results.csv", index=False)
    print(f"simulated DOE responses for {len(result)} runs")


if __name__ == "__main__":
    main()

