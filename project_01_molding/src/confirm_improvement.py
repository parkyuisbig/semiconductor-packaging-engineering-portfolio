"""Simulate center/boundary confirmation and create portfolio-level control concepts."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from verify_root_cause import RESPONSES, coefficient_map, predict_row


SEED = 20260820


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def condition_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"condition": "Baseline scenario", "role": "Before", "emc_lot": "M03", "film_roughness_class": "Textured", "vacuum_base_kpa_abs": 5.5, "zone_range_c": 2.5, "closing_speed_mm_s": 1.00},
            {"condition": "Recommended", "role": "Robust candidate", "emc_lot": "M02", "film_roughness_class": "Smooth", "vacuum_base_kpa_abs": 4.5, "zone_range_c": 1.5, "closing_speed_mm_s": 0.85},
            {"condition": "Vacuum boundary", "role": "Robust boundary", "emc_lot": "M02", "film_roughness_class": "Smooth", "vacuum_base_kpa_abs": 4.75, "zone_range_c": 1.5, "closing_speed_mm_s": 0.85},
            {"condition": "Speed boundary", "role": "Robust boundary", "emc_lot": "M02", "film_roughness_class": "Smooth", "vacuum_base_kpa_abs": 4.5, "zone_range_c": 1.5, "closing_speed_mm_s": 0.90},
            {"condition": "Zone outside", "role": "Outside window challenge", "emc_lot": "M02", "film_roughness_class": "Smooth", "vacuum_base_kpa_abs": 4.5, "zone_range_c": 1.75, "closing_speed_mm_s": 0.85},
        ]
    )


def simulate_confirmation(effects: pd.DataFrame, msa: pd.DataFrame) -> pd.DataFrame:
    rng = np.random.default_rng(SEED)
    conditions = condition_table()
    after = msa.loc[msa["phase"] == "After recipe lock"].set_index("metric")
    void_msa = float(after.loc["Edge Void Area Ratio (%)", "sd_grr"])
    offset_msa = float(after.loc["Chip Offset (um)", "sd_grr"])
    rows: list[dict] = []

    for condition in conditions.itertuples(index=False):
        base = pd.Series(condition._asdict())
        if condition.condition == "Baseline scenario":
            means = {"edge_void_pct": 1.75, "chip_offset_p95_um": 41.3, "warpage_um": 921.0, "cycle_time_index": 101.5}
        else:
            means = {response: predict_row(base, coefficient_map(effects, response)) for response in RESPONSES}
        for replicate in range(1, 13):
            void = rng.normal(means["edge_void_pct"], np.hypot(0.055, void_msa))
            offset = rng.normal(means["chip_offset_p95_um"], np.hypot(0.75, offset_msa))
            warpage = rng.normal(means["warpage_um"], 17.0)
            cycle = rng.normal(means["cycle_time_index"], 0.42)
            rows.append(
                {
                    **condition._asdict(),
                    "replicate": replicate,
                    "edge_void_pct": max(void, 0.02),
                    "chip_offset_p95_um": max(offset, 0.1),
                    "warpage_um": warpage,
                    "cycle_time_index": cycle,
                    "all_ctq_pass": bool(void <= 0.50 and offset <= 20.0 and warpage <= 750.0 and cycle <= 105.0),
                }
            )
    return pd.DataFrame(rows)


def summarize(runs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for condition, group in runs.groupby("condition", sort=False):
        row = {"condition": condition, "role": group["role"].iloc[0], "n": len(group)}
        for response in RESPONSES:
            row[f"{response}_mean"] = group[response].mean()
            row[f"{response}_std"] = group[response].std(ddof=1)
            row[f"{response}_p95"] = group[response].quantile(0.95)
        row["all_ctq_pass_rate_pct"] = 100 * group["all_ctq_pass"].mean()
        rows.append(row)
    return pd.DataFrame(rows)


def side_effect_matrix() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"change": "Lower vacuum absolute pressure", "primary_benefit": "residual gas/void risk 감소", "possible_side_effect": "evacuation time, pump load, volatile/outgassing response 변화", "project_check": "Cycle Time Index와 raw vacuum trace 동시 비교", "decision": "Benefit with cycle-time trade-off"},
            {"change": "Smaller heater-zone range", "primary_benefit": "viscosity/cure spatial uniformity 향상", "possible_side_effect": "zone tuning 과정의 thermal lag 또는 local cure 차이", "project_check": "Warpage와 edge/center coupon temperature", "decision": "Preferred; local temperature verification needed"},
            {"change": "Lower closing speed", "primary_benefit": "flow drag와 offset 감소", "possible_side_effect": "takt 증가, 지나치게 느릴 경우 gel margin 감소", "project_check": "Cycle time과 process margin을 함께 확인", "decision": "Use only inside robust combinations"},
            {"change": "Smooth release-film condition", "primary_benefit": "scenario wetting/void 개선", "possible_side_effect": "textured 대비 interface holding shear 감소 가능", "project_check": "Chip Offset P95와 coupon shear", "decision": "Surface window, not universal direction"},
            {"change": "Baseline M03 → M02 scenario", "primary_benefit": "viscosity/gel margin 개선", "possible_side_effect": "material-lot effect와 chamber effect confounding", "project_check": "replicated lot cross-split and rheology", "decision": "Candidate modifier; not a procurement conclusion"},
        ]
    )


def control_concept() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"type": "CTQ", "item": "Edge Void Area Ratio", "engineering_target": "≤0.50%", "why_observe": "evacuation/fill/cure margin의 최종 품질 결과", "evidence_or_signal": "wafer map + edge-distance profile", "portfolio_control_concept": "동일 inspection recipe로 before/after 비교", "real_data_needed": "actual SAM resolution, product spec"},
            {"type": "CTQ", "item": "Chip Offset P95", "engineering_target": "≤20 μm", "why_observe": "flow load와 interface holding의 balance 결과", "evidence_or_signal": "dx/dy vector map + registration residual", "portfolio_control_concept": "mold/debond 단계별 좌표 비교", "real_data_needed": "RDL alignment margin"},
            {"type": "Side CTQ", "item": "Warpage", "engineering_target": "≤750 μm", "why_observe": "thermal/cure 조건 변경의 기계적 side effect", "evidence_or_signal": "global bow/temperature curve", "portfolio_control_concept": "추천·경계 조건 동시 비교", "real_data_needed": "package geometry-specific criterion"},
            {"type": "Side CTQ", "item": "Cycle Time Index", "engineering_target": "≤105", "why_observe": "vacuum/slow closing 개선의 생산성 trade-off", "evidence_or_signal": "sequence timestamp", "portfolio_control_concept": "baseline 대비 index로 비교", "real_data_needed": "equipment takt and capacity"},
            {"type": "CPP", "item": "Actual vacuum base pressure", "engineering_target": "robust combinations 참조", "why_observe": "setpoint보다 cavity evacuation의 실제 결과가 중요", "evidence_or_signal": "pump-down, base pressure, leak-up", "portfolio_control_concept": "raw trace와 CTQ를 shot_id로 연결", "real_data_needed": "sensor accuracy and cavity-specific limit"},
            {"type": "CPP", "item": "Heater-zone range", "engineering_target": "robust combinations 참조", "why_observe": "local viscosity와 gel-time spatial difference를 만듦", "evidence_or_signal": "zone waveform + calibration coupon", "portfolio_control_concept": "평균온도와 range를 분리 분석", "real_data_needed": "local package temperature correlation"},
            {"type": "CPP", "item": "Closing speed", "engineering_target": "robust combinations 참조", "why_observe": "radial flow velocity와 die drag를 바꿈", "evidence_or_signal": "platen position derivative", "portfolio_control_concept": "actual speed와 offset vector 연결", "real_data_needed": "equipment motion accuracy"},
            {"type": "Material/Surface", "item": "EMC rheology + film surface", "engineering_target": "미정", "why_observe": "gel margin, wetting, holding force의 modifier", "evidence_or_signal": "viscosity/gel proxy, Ra/Rz, contact angle, shear", "portfolio_control_concept": "genealogy를 보존하고 block factor로 분석", "real_data_needed": "replicated material/surface lots"},
            {"type": "Measurement", "item": "Reference / requalification", "engineering_target": "운영 기준 미설정", "why_observe": "measurement drift와 process change를 구분하고 조건 변경 전후 비교 가능성을 확인", "evidence_or_signal": "same reference sample result", "portfolio_control_concept": "필요 이유만 문서화", "real_data_needed": "actual tool and method change history"},
        ]
    )


def verification_matrix(summary: pd.DataFrame) -> pd.DataFrame:
    baseline = summary.loc[summary["condition"] == "Baseline scenario"].iloc[0]
    recommended = summary.loc[summary["condition"] == "Recommended"].iloc[0]
    rows = []
    for response, label, target in [
        ("edge_void_pct", "Edge Void", 0.50),
        ("chip_offset_p95_um", "Chip Offset P95", 20.0),
        ("warpage_um", "Warpage", 750.0),
        ("cycle_time_index", "Cycle Time Index", 105.0),
    ]:
        before = baseline[f"{response}_mean"]
        after = recommended[f"{response}_mean"]
        rows.append(
            {
                "ctq": label,
                "before_mean": before,
                "recommended_mean": after,
                "change_pct": 100 * (after - before) / before,
                "engineering_target": target,
                "recommended_p95": recommended[f"{response}_p95"],
                "target_met_by_mean": bool(after <= target),
                "interpretation": "synthetic confirmation only",
            }
        )
    return pd.DataFrame(rows)


def build_report(summary: pd.DataFrame, verification: pd.DataFrame) -> str:
    rec = summary.loc[summary["condition"] == "Recommended"].iloc[0]
    baseline = summary.loc[summary["condition"] == "Baseline scenario"].iloc[0]
    vacuum_b = summary.loc[summary["condition"] == "Vacuum boundary"].iloc[0]
    speed_b = summary.loc[summary["condition"] == "Speed boundary"].iloc[0]
    outside = summary.loc[summary["condition"] == "Zone outside"].iloc[0]
    return f"""# PROJECT 1 · STEP 7 — Improvement Confirmation, Side Effect & Control Concept

> 모든 결과는 12회 반복 synthetic Engineering Scenario다. 실제 생산 개선 실적이나 양산 관리 기준이 아니다.

## 1. Confirmation Result

| Condition | Edge Void mean | Offset P95 mean | Warpage mean | Cycle Index mean | All-CTQ pass rate |
|---|---:|---:|---:|---:|---:|
| Baseline | {baseline['edge_void_pct_mean']:.2f}% | {baseline['chip_offset_p95_um_mean']:.1f} μm | {baseline['warpage_um_mean']:.0f} μm | {baseline['cycle_time_index_mean']:.1f} | {baseline['all_ctq_pass_rate_pct']:.0f}% |
| Recommended | {rec['edge_void_pct_mean']:.2f}% | {rec['chip_offset_p95_um_mean']:.1f} μm | {rec['warpage_um_mean']:.0f} μm | {rec['cycle_time_index_mean']:.1f} | {rec['all_ctq_pass_rate_pct']:.0f}% |
| Vacuum boundary | {vacuum_b['edge_void_pct_mean']:.2f}% | {vacuum_b['chip_offset_p95_um_mean']:.1f} μm | {vacuum_b['warpage_um_mean']:.0f} μm | {vacuum_b['cycle_time_index_mean']:.1f} | {vacuum_b['all_ctq_pass_rate_pct']:.0f}% |
| Speed boundary | {speed_b['edge_void_pct_mean']:.2f}% | {speed_b['chip_offset_p95_um_mean']:.1f} μm | {speed_b['warpage_um_mean']:.0f} μm | {speed_b['cycle_time_index_mean']:.1f} | {speed_b['all_ctq_pass_rate_pct']:.0f}% |
| Zone outside | {outside['edge_void_pct_mean']:.2f}% | {outside['chip_offset_p95_um_mean']:.1f} μm | {outside['warpage_um_mean']:.0f} μm | {outside['cycle_time_index_mean']:.1f} | {outside['all_ctq_pass_rate_pct']:.0f}% |

## 2. Figure 19 — Confirmation Comparison

![Confirmation comparison](../figures/19_confirmation_comparison.svg)

**Observation**  
Recommended condition은 네 CTQ 평균이 Engineering Target 안에 들어온다. Boundary condition은 평균은 만족할 수 있어도 반복 산포를 포함한 all-CTQ pass rate가 낮아질 수 있다.

**Engineering Interpretation**  
최적점 하나보다 boundary challenge를 함께 보여야 공정창의 guard band를 설명할 수 있다.

**Next Action**  
실제 데이터 확보 시 center와 각 boundary를 material/chamber block으로 반복한다.

## 3. Figure 20 — Before/Recommended P95

![Before after verification](../figures/20_before_after_p95.svg)

**Observation**  
Recommended condition은 mean뿐 아니라 P95 기준에서도 개선 방향을 유지한다.

**Engineering Interpretation**  
평균 개선만으로 tail risk가 가려지는 문제를 피했다.

**Next Action**  
실제 portfolio 발표에서는 mean, standard deviation, P95를 함께 제시한다.

## 4. Side Effect Matrix

![Side effect matrix](../figures/21_side_effect_matrix.svg)

핵심 trade-off는 다음과 같다.

- 강한 vacuum: void 개선 ↔ evacuation time/pump load 가능성
- 느린 closing: offset 감소 ↔ takt 증가 및 지나치게 느릴 때 gel margin 감소
- smooth surface: wetting 개선 가능성 ↔ holding shear 감소 가능성
- thermal uniformity 개선: warpage 개선 가능성 ↔ local temperature 검증 필요

자세한 내용은 `results/side_effect_matrix.csv`에 저장한다.

## 5. Portfolio-level Control Concept

현재는 양산 단계가 아니므로 Sampling Frequency, Warning Limit, OCAP 수치를 만들지 않는다. 대신 다음만 정의한다.

1. 무엇을 볼 것인가: Edge Void, Offset, Warpage, Cycle Time, actual vacuum, zone range, actual speed, material/surface genealogy
2. 왜 볼 것인가: 어떤 물리 mechanism과 Root Cause claim을 확인하는지
3. 어떤 데이터가 추가로 필요한가: 실제 sensor accuracy, product spec, chamber/material replicate
4. Reference/requalification이 필요한 이유: measurement drift와 process change를 구분하고 조건 변경 전후 비교 가능성을 확보하기 위해

전체 항목은 `results/control_concept.csv`에 정리한다.

## 6. Improvement Statement

> Synthetic confirmation에서 M02/Smooth, vacuum 4.5 kPa abs, zone range 1.5°C, closing speed 0.85 mm/s 후보는 baseline 대비 Edge Void와 Chip Offset을 동시에 낮추고 Warpage Target을 만족했다. Cycle Time은 증가 방향이어서 단일 품질 최적점이 아닌 다중 CTQ 조건으로 선택했다. Boundary 반복에서는 guard band가 줄어드는 것을 확인해 평균 optimum보다 robust process window를 최종 개선안으로 제시했다.

## 7. Claim Boundary

- 가능한 주장: “물리 기반 synthetic DOE와 confirmation으로 개선 후보와 side effect를 정량 비교했다.”
- 불가능한 주장: “실제 양산 수율을 개선했고 Control Limit을 확정했다.”
"""


def main() -> None:
    root = project_root()
    effects = pd.read_csv(root / "results" / "doe_effects.csv")
    msa = pd.read_csv(root / "results" / "msa_summary.csv")
    runs = simulate_confirmation(effects, msa)
    summary = summarize(runs)
    side = side_effect_matrix()
    control = control_concept()
    verification = verification_matrix(summary)

    runs.to_csv(root / "results" / "confirmation_runs.csv", index=False)
    summary.to_csv(root / "results" / "confirmation_summary.csv", index=False)
    side.to_csv(root / "results" / "side_effect_matrix.csv", index=False)
    control.to_csv(root / "results" / "control_concept.csv", index=False)
    verification.to_csv(root / "results" / "improvement_verification_matrix.csv", index=False)
    (root / "report" / "07_improvement_verification_control_concept.md").write_text(build_report(summary, verification), encoding="utf-8")
    print(summary[["condition", "all_ctq_pass_rate_pct"]].to_string(index=False))


if __name__ == "__main__":
    main()

