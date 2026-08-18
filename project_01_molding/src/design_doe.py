"""Create the STEP 3 hypothesis matrix and split-plot DOE run order."""

from __future__ import annotations

from itertools import product
from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20260818


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def hypothesis_matrix() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "hypothesis": "H1 Thermo-rheology × evacuation margin",
                "cause_class": "Method + Machine",
                "mechanism": "t_vac + t_fill approaches t_gel; non-isothermal viscosity/cure closes flow window",
                "expected_signature": "edge threshold; margin dose-response; vacuum×zone interaction; vector/void spatial coupling",
                "primary_test": "short-shot + 2^3 process DOE with center points",
                "improve_if_true": "vacuum-ready interlock; staged closing; heater-zone matching; cure-window recipe",
                "reject_if": "margin and interactions do not reproduce after material/chamber blocking",
                "pretest_evidence": "Strong",
            },
            {
                "hypothesis": "H2 Vacuum/Vent equipment degradation",
                "cause_class": "Machine",
                "mechanism": "leak/conductance loss retains gas and creates asymmetric pressure distribution",
                "expected_signature": "chamber + PM-age dependency; pump-down/leak-up drift; PM recovery",
                "primary_test": "chamber swap + leak test + vent clean before/after",
                "improve_if_true": "condition-based PM; actual-vacuum interlock; chamber matching",
                "reject_if": "defect follows material across chambers while vacuum traces remain matched",
                "pretest_evidence": "Medium-Strong",
            },
            {
                "hypothesis": "H3 Interface roughness / wetting / adhesion",
                "cause_class": "Material + Surface",
                "mechanism": "roughness and contamination alter real contact area, wetting, thermal contact and holding shear force",
                "expected_signature": "Ra/Rz/contact-angle/shear-strength dependency; slip when F_drag/F_hold > 1",
                "primary_test": "surface metrology + contact angle + coupon shear + roughness whole-plot DOE",
                "improve_if_true": "surface spec window; cleaning/plasma control; incoming metrology; adhesion margin",
                "reject_if": "roughness/wetting/shear changes do not alter offset under matched flow load",
                "pretest_evidence": "Unverified",
            },
            {
                "hypothesis": "H4 Film tension / platen parallelism",
                "cause_class": "Machine + Mechanics",
                "mechanism": "lateral film force or pressure nonuniformity adds die force and asymmetric flow",
                "expected_signature": "offset direction follows tension sign; cavity map repeats; parallelism/pressure correlation",
                "primary_test": "tension reversal + pressure film/map + platen/chuck metrology",
                "improve_if_true": "left-right tension matching; parallelism calibration; chuck flatness PM",
                "reject_if": "direction does not reverse or remain tied to equipment geometry",
                "pretest_evidence": "Weak-Medium",
            },
            {
                "hypothesis": "H5 EMC rheology / storage history",
                "cause_class": "Material",
                "mechanism": "viscosity and gel-time shift reduce fill margin and increase drag",
                "expected_signature": "material genealogy across chambers; viscosity/gel proxy dose-response",
                "primary_test": "normal/suspect material split + rheology proxy + blocked DOE",
                "improve_if_true": "storage/floor-life genealogy; incoming proxy; FEFO; lot hold rule",
                "reject_if": "same chamber remains bad across material swap with matched properties",
                "pretest_evidence": "Medium",
            },
            {
                "hypothesis": "H6 Metrology bias",
                "cause_class": "Measurement",
                "mechanism": "edge threshold/registration drift inflates void or apparent offset",
                "expected_signature": "repeat scan/tool/recipe dependency without physical trace signature",
                "primary_test": "blind repeat scan + cross-tool registration study",
                "improve_if_true": "threshold lock; reference artifact; calibration and requalification",
                "reject_if": "repeatability is adequate and physical signatures remain",
                "pretest_evidence": "Unverified",
            },
        ]
    )


def make_doe() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    whole_plots = [
        ("M02", "Smooth", 0.25),
        ("M02", "Textured", 0.65),
        ("M03", "Smooth", 0.25),
        ("M03", "Textured", 0.65),
    ]
    rng.shuffle(whole_plots)
    rows: list[dict] = []
    run_order = 1

    for whole_plot_no, (emc_lot, roughness_class, ra_um) in enumerate(whole_plots, start=1):
        sub_runs = []
        for a, b, c in product([-1, 1], repeat=3):
            sub_runs.append(
                {
                    "is_center": 0,
                    "A_vacuum_code": a,
                    "B_zone_range_code": b,
                    "C_closing_speed_code": c,
                    "vacuum_base_kpa_abs": 4.5 if a == -1 else 6.5,
                    "zone_range_c": 1.5 if b == -1 else 3.5,
                    "closing_speed_mm_s": 0.85 if c == -1 else 1.15,
                }
            )
        sub_runs.append(
            {
                "is_center": 1,
                "A_vacuum_code": 0,
                "B_zone_range_code": 0,
                "C_closing_speed_code": 0,
                "vacuum_base_kpa_abs": 5.5,
                "zone_range_c": 2.5,
                "closing_speed_mm_s": 1.00,
            }
        )
        rng.shuffle(sub_runs)
        for sub in sub_runs:
            rows.append(
                {
                    "run_order": run_order,
                    "whole_plot": f"WP{whole_plot_no}",
                    "emc_lot": emc_lot,
                    "film_roughness_class": roughness_class,
                    "film_Ra_um_project_scenario": ra_um,
                    **sub,
                    "edge_void_pct": np.nan,
                    "chip_offset_p95_um": np.nan,
                    "warpage_um": np.nan,
                    "cycle_time_s": np.nan,
                    "notes": "",
                }
            )
            run_order += 1
    return pd.DataFrame(rows)


def main() -> None:
    results = project_root() / "results"
    results.mkdir(parents=True, exist_ok=True)
    matrix = hypothesis_matrix()
    doe = make_doe()
    matrix.to_csv(results / "hypothesis_validation_matrix.csv", index=False)
    doe.to_csv(results / "doe_run_matrix.csv", index=False)
    print(f"hypotheses={len(matrix)}, doe_runs={len(doe)}, whole_plots={doe['whole_plot'].nunique()}")


if __name__ == "__main__":
    main()

