"""Estimate DOE effects, multi-response desirability and simulated verification."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd


RESPONSES = ["edge_void_pct", "chip_offset_p95_um", "warpage_um", "cycle_time_index"]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def fit_effects(factorial: pd.DataFrame) -> pd.DataFrame:
    coded = pd.DataFrame(
        {
            "A_vacuum": factorial["A_vacuum_code"].astype(float),
            "B_zone_range": factorial["B_zone_range_code"].astype(float),
            "C_closing_speed": factorial["C_closing_speed_code"].astype(float),
            "D_material_M03": np.where(factorial["emc_lot"] == "M03", 1.0, -1.0),
            "E_textured": np.where(factorial["film_roughness_class"] == "Textured", 1.0, -1.0),
        }
    )
    for left, right in [
        ("A_vacuum", "B_zone_range"),
        ("A_vacuum", "C_closing_speed"),
        ("B_zone_range", "C_closing_speed"),
        ("B_zone_range", "E_textured"),
        ("D_material_M03", "E_textured"),
    ]:
        coded[f"{left}:{right}"] = coded[left] * coded[right]

    x = np.column_stack([np.ones(len(coded)), coded.to_numpy()])
    rows: list[dict] = []
    for response in RESPONSES:
        y = factorial[response].to_numpy(float)
        coef, *_ = np.linalg.lstsq(x, y, rcond=None)
        pred = x @ coef
        r2 = 1.0 - float(np.sum((y - pred) ** 2) / np.sum((y - y.mean()) ** 2))
        for term, beta in zip(["intercept", *coded.columns], coef):
            rows.append(
                {
                    "response": response,
                    "term": term,
                    "coefficient": beta,
                    "high_minus_low_effect": np.nan if term == "intercept" else 2 * beta,
                    "model_r2": r2,
                    "inference_note": "whole-plot effects D/E are exploratory; only four whole plots",
                }
            )
    return pd.DataFrame(rows)


def desirability(frame: pd.DataFrame) -> pd.DataFrame:
    out = frame.copy()

    def smaller_better(series: pd.Series, target: float, reject: float) -> pd.Series:
        return np.clip((reject - series) / (reject - target), 0, 1)

    # Engineering targets remain pass/fail gates; stricter ideal points preserve
    # continuous ranking among conditions that all pass those gates.
    out["d_void"] = smaller_better(out["edge_void_pct"], 0.25, 2.50)
    out["d_offset"] = smaller_better(out["chip_offset_p95_um"], 12.0, 45.0)
    out["d_warpage"] = smaller_better(out["warpage_um"], 620.0, 1000.0)
    out["d_cycle"] = smaller_better(out["cycle_time_index"], 100.0, 110.0)
    # Primary CTQs receive twice the exponent weight of side-effect CTQs.
    out["overall_desirability"] = (
        out["d_void"] ** 2 * out["d_offset"] ** 2 * out["d_warpage"] * out["d_cycle"]
    ) ** (1 / 6)
    return out


def simulated_verification(best: pd.Series, rng: np.random.Generator) -> pd.DataFrame:
    before = pd.DataFrame(
        {
            "phase": "Before synthetic baseline",
            "edge_void_pct": rng.normal(1.75, 0.20, 12),
            "chip_offset_p95_um": rng.normal(41.3, 3.2, 12),
            "warpage_um": rng.normal(921, 45, 12),
            "cycle_time_index": rng.normal(101.5, 0.8, 12),
        }
    )
    after = pd.DataFrame(
        {
            "phase": "After simulated confirmation",
            "edge_void_pct": rng.normal(best["edge_void_pct"], 0.08, 12),
            "chip_offset_p95_um": rng.normal(best["chip_offset_p95_um"], 1.4, 12),
            "warpage_um": rng.normal(best["warpage_um"], 22, 12),
            "cycle_time_index": rng.normal(best["cycle_time_index"], 0.55, 12),
        }
    )
    return pd.concat([before, after], ignore_index=True)


def build_report(summary: dict) -> str:
    return f"""# PROJECT 1 · STEP 4 — Physics-informed DOE 결과

> 본 결과는 문헌이 지지하는 인과 방향을 바탕으로 만든 **synthetic Engineering Scenario**이다. 수치 계수와 최적 recipe는 실제 Fab 조건, SK하이닉스 조건 또는 업계 표준이 아니다.

## 1. 결론부터

36-run split-plot DOE에서 가장 높은 multi-response desirability를 보인 project condition은 다음과 같다.

| Parameter | Selected project condition |
|---|---:|
| EMC lot | {summary['best_emc']} |
| Film roughness | {summary['best_roughness']} |
| Vacuum base pressure | {summary['best_vacuum']:.1f} kPa abs |
| Heater zone range | {summary['best_zone']:.1f} °C |
| Closing speed | {summary['best_speed']:.2f} mm/s |
| Overall desirability | {summary['best_desirability']:.3f} |

낮은 absolute pressure, 작은 zone 편차, 낮은 closing speed가 process margin을 확보했다. Smooth film은 이 scenario에서 wetting 측면이 유리했고 Textured film은 holding shear를 높여 offset을 낮추는 방향이었으나 void trade-off가 발생했다.

## 2. Figure 9 — DOE Main Effects

![DOE main effects](../figures/09_doe_main_effects.svg)

**Observation**  
Vacuum base pressure와 heater-zone range가 높아질수록 Edge Void가 증가한다. Closing speed는 void와 offset을 모두 악화시키는 방향이다.

**Engineering Interpretation**  
진공·온도·속도는 독립 knob가 아니라 `M_process = t_gel−t_vac−t_fill`과 flow load를 동시에 바꾼다.

**Next Action**  
Actual waveform이 설정 수준을 재현하는지 확인하고 H1의 A×B interaction을 confirmation run에서 반복한다.

## 3. Figure 10 — Vacuum × Zone Interaction

![Vacuum zone interaction](../figures/10_vacuum_zone_interaction.svg)

**Observation**  
Zone range가 큰 조건에서 vacuum base pressure 악화의 void penalty가 더 커진다.

**Engineering Interpretation**  
열경화가 usable flow time을 줄인 상태에서는 evacuation margin 감소에 더 민감해진다는 H1 signature다.

**Next Action**  
Short-shot flow front와 vacuum 완료 시점의 edge temperature를 직접 측정한다.

## 4. Figure 11 — Roughness Trade-off

![Roughness trade-off](../figures/11_roughness_tradeoff.svg)

**Observation**  
Textured surface는 interface shear를 높여 offset을 낮추지만, 높은 contact-angle proxy로 void가 증가하는 trade-off가 있다.

**Engineering Interpretation**  
Ra 증가를 일률적으로 좋거나 나쁘다고 정의할 수 없다. holding, wetting, thermal contact를 함께 관리해야 한다.

**Next Action**  
Ra/Rz–contact angle–die shear 실험으로 synthetic 방향을 검증하고 intermediate roughness center level을 추가한다.

## 5. Figure 12 — Multi-response Window

![DOE desirability](../figures/12_doe_desirability.svg)

**Observation**  
Void 단독 최적점과 offset 단독 최적점이 완전히 같지 않으며 side-effect를 포함한 종합점수로 condition을 선택해야 한다.

**Engineering Interpretation**  
양산 recipe 선택은 단일 Y 최소화가 아니라 품질·warpage·takt의 제약 최적화 문제다.

**Next Action**  
상위 3개 condition을 다른 chamber와 material lot에서 confirmation한다.

## 6. Projected Before / After

| Metric | Before synthetic mean | After simulated mean | Change |
|---|---:|---:|---:|
| Edge Void | {summary['before_void']:.2f}% | {summary['after_void']:.2f}% | {summary['void_change_pct']:.1f}% |
| Chip Offset P95 | {summary['before_offset']:.1f} μm | {summary['after_offset']:.1f} μm | {summary['offset_change_pct']:.1f}% |
| Warpage | {summary['before_warpage']:.0f} μm | {summary['after_warpage']:.0f} μm | {summary['warpage_change_pct']:.1f}% |
| Cycle Time Index | {summary['before_cycle']:.1f} | {summary['after_cycle']:.1f} | {summary['cycle_change_pct']:.1f}% |

이는 실제 개선 실적이 아니라 **DOE 결과로부터 생성한 simulated confirmation**이다. 자기소개서에는 “개선했다”가 아니라 “개선 가능성을 정량 검증했다”로 표현한다.

## 7. Root Cause Update

- H1 Thermo-rheology × evacuation margin: synthetic DOE에서 interaction 재현 → **Strong**
- H2 Vacuum/Vent equipment: 실제 leak/PM split 미실시 → **Medium-Strong 유지**
- H3 Roughness/Wetting/Adhesion: response trade-off 재현, 실측 coupon 미실시 → **Medium**
- H4 Tension/Parallelism: reversal test 미실시 → **Weak-Medium**
- H5 EMC rheology: material whole-plot effect 존재, whole plot 수가 적음 → **Medium**
- H6 Measurement: repeatability study 전 → **Unverified**

## 8. 통계 해석 주의

EMC와 roughness는 hard-to-change whole-plot factor이며 whole plot이 4개뿐이다. 따라서 해당 계수의 p-value를 강한 인과 증거로 사용하지 않는다. Process factor effect와 physical signature를 우선하고, material/roughness는 추가 whole-plot replicate로 검증한다.
"""


def main() -> None:
    root = project_root()
    data = pd.read_csv(root / "data" / "processed" / "doe_results.csv")
    factorial = data.loc[data["is_center"] == 0].copy()
    effects = fit_effects(factorial)
    ranked = desirability(data).sort_values("overall_desirability", ascending=False).reset_index(drop=True)
    best = ranked.iloc[0]
    verification = simulated_verification(best, np.random.default_rng(20260819))

    means = verification.groupby("phase")[RESPONSES].mean()
    before = means.loc["Before synthetic baseline"]
    after = means.loc["After simulated confirmation"]
    change = (after - before) / before * 100
    summary = {
        "best_emc": str(best["emc_lot"]),
        "best_roughness": str(best["film_roughness_class"]),
        "best_vacuum": float(best["vacuum_base_kpa_abs"]),
        "best_zone": float(best["zone_range_c"]),
        "best_speed": float(best["closing_speed_mm_s"]),
        "best_desirability": float(best["overall_desirability"]),
        "before_void": float(before["edge_void_pct"]),
        "after_void": float(after["edge_void_pct"]),
        "void_change_pct": float(change["edge_void_pct"]),
        "before_offset": float(before["chip_offset_p95_um"]),
        "after_offset": float(after["chip_offset_p95_um"]),
        "offset_change_pct": float(change["chip_offset_p95_um"]),
        "before_warpage": float(before["warpage_um"]),
        "after_warpage": float(after["warpage_um"]),
        "warpage_change_pct": float(change["warpage_um"]),
        "before_cycle": float(before["cycle_time_index"]),
        "after_cycle": float(after["cycle_time_index"]),
        "cycle_change_pct": float(change["cycle_time_index"]),
    }

    effects.to_csv(root / "results" / "doe_effects.csv", index=False)
    ranked.to_csv(root / "results" / "doe_ranked_conditions.csv", index=False)
    verification.to_csv(root / "results" / "simulated_verification.csv", index=False)
    (root / "results" / "doe_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "report" / "04_doe_results.md").write_text(build_report(summary), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
