"""Bootstrap DOE effects and derive an MSA-guarded robust process window."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


SEED = 20260818
RESPONSES = ["edge_void_pct", "chip_offset_p95_um", "warpage_um", "cycle_time_index"]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def within_whole_plot_effects(data: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []
    definitions = {
        "A_vacuum": data["A_vacuum_code"],
        "B_zone_range": data["B_zone_range_code"],
        "C_closing_speed": data["C_closing_speed_code"],
        "A_vacuum:B_zone_range": data["A_vacuum_code"] * data["B_zone_range_code"],
    }
    for whole_plot, group in data.groupby("whole_plot"):
        idx = group.index
        for term, codes in definitions.items():
            local_codes = codes.loc[idx]
            for response in RESPONSES:
                high = group.loc[local_codes == 1, response].mean()
                low = group.loc[local_codes == -1, response].mean()
                rows.append({"whole_plot": whole_plot, "term": term, "response": response, "effect": high - low})
    return pd.DataFrame(rows)


def bootstrap_effects(data: pd.DataFrame, n_boot: int = 10000) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    wp_effects = within_whole_plot_effects(data)
    rows: list[dict] = []
    for (term, response), group in wp_effects.groupby(["term", "response"]):
        values = group["effect"].to_numpy(float)
        boot = rng.choice(values, size=(n_boot, len(values)), replace=True).mean(axis=1)
        lo, hi = np.quantile(boot, [0.025, 0.975])
        rows.append(
            {
                "term": term,
                "response": response,
                "mean_effect": values.mean(),
                "ci95_low": lo,
                "ci95_high": hi,
                "whole_plot_effects_n": len(values),
                "direction_stable": bool(lo > 0 or hi < 0),
                "note": "whole-plot bootstrap; n=4 blocks, uncertainty remains large",
            }
        )
    return pd.DataFrame(rows)


def coefficient_map(effects: pd.DataFrame, response: str) -> dict[str, float]:
    sub = effects.loc[effects["response"] == response]
    return dict(zip(sub["term"], sub["coefficient"].astype(float)))


def predict_row(row: pd.Series, coefs: dict[str, float]) -> float:
    a = (row["vacuum_base_kpa_abs"] - 5.5) / 1.0
    b = (row["zone_range_c"] - 2.5) / 1.0
    c = (row["closing_speed_mm_s"] - 1.00) / 0.15
    d = 1.0 if row["emc_lot"] == "M03" else -1.0
    e = 1.0 if row["film_roughness_class"] == "Textured" else -1.0
    values = {
        "intercept": 1.0,
        "A_vacuum": a,
        "B_zone_range": b,
        "C_closing_speed": c,
        "D_material_M03": d,
        "E_textured": e,
        "A_vacuum:B_zone_range": a * b,
        "A_vacuum:C_closing_speed": a * c,
        "B_zone_range:C_closing_speed": b * c,
        "B_zone_range:E_textured": b * e,
        "D_material_M03:E_textured": d * e,
    }
    return float(sum(coefs.get(term, 0.0) * value for term, value in values.items()))


def make_process_window(effects: pd.DataFrame, msa: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for emc in ["M02", "M03"]:
        for roughness in ["Smooth", "Textured"]:
            for vacuum in np.round(np.arange(4.5, 6.5001, 0.25), 2):
                for zone in np.round(np.arange(1.5, 3.5001, 0.25), 2):
                    for speed in np.round(np.arange(0.85, 1.1501, 0.05), 2):
                        rows.append(
                            {
                                "emc_lot": emc,
                                "film_roughness_class": roughness,
                                "vacuum_base_kpa_abs": vacuum,
                                "zone_range_c": zone,
                                "closing_speed_mm_s": speed,
                            }
                        )
    grid = pd.DataFrame(rows)
    for response in RESPONSES:
        coefs = coefficient_map(effects, response)
        grid[response] = grid.apply(lambda row: predict_row(row, coefs), axis=1)

    after = msa.loc[msa["phase"] == "After recipe lock"].set_index("metric")
    void_sigma = float(after.loc["Edge Void Area Ratio (%)", "sd_grr"])
    offset_sigma = float(after.loc["Chip Offset (um)", "sd_grr"])
    grid["void_upper_3sigma_msa"] = grid["edge_void_pct"] + 3 * void_sigma
    grid["offset_upper_3sigma_msa"] = grid["chip_offset_p95_um"] + 3 * offset_sigma
    grid["robust_pass"] = (
        (grid["void_upper_3sigma_msa"] <= 0.50)
        & (grid["offset_upper_3sigma_msa"] <= 20.0)
        & (grid["warpage_um"] <= 750.0)
        & (grid["cycle_time_index"] <= 105.0)
    )
    grid["primary_margin"] = np.minimum(
        0.50 - grid["void_upper_3sigma_msa"],
        (20.0 - grid["offset_upper_3sigma_msa"]) / 20.0,
    )
    return grid


def evidence_tables(boot: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    void = boot.loc[boot["response"] == "edge_void_pct"].set_index("term")
    verification = pd.DataFrame(
        [
            {
                "claim": "H1 evacuation/cure margin controls Edge Void",
                "statistical_evidence": f"A={void.loc['A_vacuum','mean_effect']:.2f}, B={void.loc['B_zone_range','mean_effect']:.2f}, A×B={void.loc['A_vacuum:B_zone_range','mean_effect']:.2f} %-point",
                "physical_evidence": "t_vac + t_fill competes with t_gel; edge pattern and short-shot prediction",
                "decision": "Confirmed within synthetic scenario",
                "remaining_real_test": "DSC/DEA calibration + short-shot + actual trace DOE",
            },
            {
                "claim": "H2 Vacuum/Vent equipment degradation",
                "statistical_evidence": "chamber/PM-age association in STEP 2; vent condition not manipulated in DOE",
                "physical_evidence": "pump-down/leak-up and edge air-pocket mechanism",
                "decision": "Supported, not causally isolated",
                "remaining_real_test": "vent clean before/after + leak test + chamber split",
            },
            {
                "claim": "H3 Roughness/wetting/adhesion",
                "statistical_evidence": "roughness is an unreplicated whole-plot factor",
                "physical_evidence": "contact-angle versus holding-shear trade-off",
                "decision": "Mechanistically plausible, not verified",
                "remaining_real_test": "Ra/Rz/contact angle/coupon shear with replicated surface lots",
            },
            {
                "claim": "H4 Film tension/platen mechanics",
                "statistical_evidence": "not manipulated in current DOE",
                "physical_evidence": "force direction and coordinate-system signature defined",
                "decision": "Open hypothesis",
                "remaining_real_test": "tension/orientation reversal + pressure/parallelism map",
            },
            {
                "claim": "H5 EMC material history",
                "statistical_evidence": "M02/M03 whole-plot contrast without replicate whole plots",
                "physical_evidence": "viscosity/gel-time shift reduces process margin",
                "decision": "Modifier supported, causal strength limited",
                "remaining_real_test": "replicated material-lot cross split + rheology",
            },
            {
                "claim": "H6 Measurement bias",
                "statistical_evidence": "recipe lock reduces Void GRR 45.9%→12.2% tolerance",
                "physical_evidence": "threshold/registration/profilometer method can shift measured CTQ",
                "decision": "Confounding reduced, not eliminated",
                "remaining_real_test": "reference-based comparison if measurement setup changes",
            },
        ]
    )
    evidence = pd.DataFrame(
        [
            {"rank": 1, "cause": "Thermo-rheology × evacuation margin", "level": "Strong", "scope": "Confirmed only in synthetic DOE"},
            {"rank": 2, "cause": "Vacuum/Vent equipment degradation", "level": "Medium-Strong", "scope": "Associative evidence; split test pending"},
            {"rank": 3, "cause": "EMC rheology/storage modifier", "level": "Medium", "scope": "Whole-plot replication pending"},
            {"rank": 4, "cause": "Roughness/wetting/adhesion", "level": "Medium", "scope": "Mechanistic trade-off; coupon test pending"},
            {"rank": 5, "cause": "Film tension/platen mechanics", "level": "Weak-Medium", "scope": "Reversal test pending"},
            {"rank": 6, "cause": "Measurement bias", "level": "Reduced", "scope": "After-lock data only"},
        ]
    )
    return verification, evidence


def build_report(summary: dict) -> str:
    return f"""# PROJECT 1 · STEP 6 — Root Cause Verification & Robust Process Window

> 모든 수치와 Root Cause 판정은 synthetic Engineering Scenario 내부의 결과다. 실제 Fab Root Cause 또는 SK하이닉스 공정 조건으로 표현하지 않는다.

## 1. 최종 판단

현재 가장 강한 설명은 **열–유동–경화 margin 감소**다. Vacuum base pressure 악화와 heater-zone range 증가는 Edge Void를 증가시켰다. 두 요인의 interaction 평균도 악화 방향이었지만 bootstrap 95% CI가 0을 포함해 안정적인 effect로 확정하지 않는다. Closing speed는 void보다 chip drag/offset에 더 직접적인 영향을 보였다.

다만 원인 판정 범위는 다음처럼 제한한다.

- H1: synthetic DOE에서 조작·재현됨 → Strong
- H2: chamber/time/PM signature는 있으나 vent를 직접 조작하지 않음 → Medium-Strong
- H3/H5: whole-plot 반복 부족 → causal confirmation 불가
- H4: 현재 DOE에서 미조작 → open hypothesis
- H6: recipe lock으로 confounding 감소, 완전 제거는 아님

## 2. Bootstrap Effect

![Bootstrap effects](../figures/16_bootstrap_effects.svg)

**Observation**  
Edge Void high-minus-low effect는 Vacuum {summary['void_effect_a']:.2f}, Zone range {summary['void_effect_b']:.2f}, A×B {summary['void_effect_ab']:.2f} percentage-point다. A×B의 bootstrap 95% CI는 {summary['void_ab_ci_low']:.2f}–{summary['void_ab_ci_high']:.2f}로 0을 포함한다. 각 effect는 4개 whole plot 내부 contrast에서 계산했다.

**Engineering Interpretation**  
Zone range가 가장 큰 process lever이며 vacuum 악화와 결합하면 margin penalty가 커진다. 단, whole plot 수가 4개뿐이므로 CI는 탐색적이다.

**Next Action**  
실제 검증에서는 material/chamber block을 추가하고 같은 contrast 방향이 재현되는지 확인한다.

## 3. MSA-guarded Robust Process Window

![Robust process window](../figures/17_robust_process_window.svg)

Robust pass 조건은 다음과 같다.

- `Predicted Void + 3σ_GRR ≤ 0.50%`
- `Predicted Offset + 3σ_GRR ≤ 20 μm`
- `Warpage ≤ 750 μm`
- `Cycle Time Index ≤ 105`

M02/Smooth 조합의 탐색 grid {summary['selected_grid_total']}개 중 {summary['selected_grid_pass']}개가 robust pass다. 단순 범위로 표현하면 vacuum {summary['vacuum_min']:.2f}–{summary['vacuum_max']:.2f} kPa abs, zone range {summary['zone_min']:.2f}–{summary['zone_max']:.2f}°C, closing speed {summary['speed_min']:.2f}–{summary['speed_max']:.2f} mm/s다.

**주의:** 이 min/max를 독립 허용범위로 조합하면 안 된다. Interaction 때문에 반드시 Figure와 `robust_process_window.csv`의 동시 조합을 사용한다.

**Observation**  
낮은 zone range와 낮은 absolute vacuum pressure 쪽에 robust region이 형성된다. Closing speed가 높아지면 offset guard band가 먼저 사라진다.

**Engineering Interpretation**  
Average optimum보다 measurement uncertainty를 포함한 공정창이 더 좁다. 이는 MSA를 recipe 판단에 반영한 결과다.

**Next Action**  
실제 장비에서는 selected window의 center와 boundary에서 confirmation run을 수행한다.

## 4. Root Cause Evidence Ladder

![Root cause evidence ladder](../figures/18_root_cause_evidence_ladder.svg)

**Observation**  
H1만 조작 DOE evidence를 갖고, H2는 associative, H3~H5는 제한된 evidence다.

**Engineering Interpretation**  
물리적으로 그럴듯하다는 사실과 실험으로 원인을 규명했다는 주장을 분리해야 한다.

**Next Action**  
포트폴리오에서는 H1을 주원인, H2를 설비 악화요인, H3/H5를 modifier, H4를 배제되지 않은 대안으로 표현한다.

## 5. 최종 Root Cause Statement

> 본 synthetic project에서 Edge Void의 주원인은 heater-zone 불균일과 vacuum evacuation margin 감소가 EMC의 usable flow window를 축소한 것이다. 같은 조건에서 증가한 pressure/viscous load가 chip offset을 악화시켰다. Vacuum/Vent 열화는 이 margin을 악화시키는 설비 요인으로 지지되었지만 직접 split test는 수행하지 않았다. EMC 소재와 surface roughness는 rheology, wetting과 holding force를 바꾸는 modifier이며 whole-plot 반복 부족으로 독립 root cause로 확정하지 않았다. Measurement recipe lock을 통해 측정기인 confounding은 줄였다.

## 6. 면접에서 지켜야 할 표현

- 가능: “Synthetic DOE에서 H1 interaction을 재현하고 robust process window를 도출했다.”
- 가능: “H2는 설비 signature가 있었지만 직접 조작하지 않아 원인 확정을 보류했다.”
- 금지: “실제 Fab의 edge void를 75% 개선했다.”
- 금지: “표면거칠기가 원인임을 증명했다.”
"""


def main() -> None:
    root = project_root()
    doe = pd.read_csv(root / "data" / "processed" / "doe_results.csv")
    factorial = doe.loc[doe["is_center"] == 0].copy()
    effects = pd.read_csv(root / "results" / "doe_effects.csv")
    msa = pd.read_csv(root / "results" / "msa_summary.csv")

    boot = bootstrap_effects(factorial)
    window = make_process_window(effects, msa)
    verification, evidence = evidence_tables(boot)
    selected = window.loc[(window["emc_lot"] == "M02") & (window["film_roughness_class"] == "Smooth")]
    passed = selected.loc[selected["robust_pass"]]
    if passed.empty:
        raise RuntimeError("No robust process-window cells found")

    void_boot = boot.loc[boot["response"] == "edge_void_pct"].set_index("term")
    summary = {
        "void_effect_a": float(void_boot.loc["A_vacuum", "mean_effect"]),
        "void_effect_b": float(void_boot.loc["B_zone_range", "mean_effect"]),
        "void_effect_ab": float(void_boot.loc["A_vacuum:B_zone_range", "mean_effect"]),
        "void_ab_ci_low": float(void_boot.loc["A_vacuum:B_zone_range", "ci95_low"]),
        "void_ab_ci_high": float(void_boot.loc["A_vacuum:B_zone_range", "ci95_high"]),
        "selected_grid_total": int(len(selected)),
        "selected_grid_pass": int(len(passed)),
        "vacuum_min": float(passed["vacuum_base_kpa_abs"].min()),
        "vacuum_max": float(passed["vacuum_base_kpa_abs"].max()),
        "zone_min": float(passed["zone_range_c"].min()),
        "zone_max": float(passed["zone_range_c"].max()),
        "speed_min": float(passed["closing_speed_mm_s"].min()),
        "speed_max": float(passed["closing_speed_mm_s"].max()),
    }

    boot.to_csv(root / "results" / "bootstrap_effects.csv", index=False)
    window.to_csv(root / "results" / "robust_process_window.csv", index=False)
    verification.to_csv(root / "results" / "root_cause_verification_matrix.csv", index=False)
    evidence.to_csv(root / "results" / "final_root_cause_evidence.csv", index=False)
    (root / "results" / "verification_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "report" / "06_root_cause_verification.md").write_text(build_report(summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
