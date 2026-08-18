# PROJECT 1 — Compression Molding Edge Void & Chip Offset 개선

> 현재 상태: **PROJECT 1 포트폴리오 패키지 완료 — physics-informed synthetic study**

## 프로젝트 목적

재구성 웨이퍼(reconstituted wafer)의 compression molding 공정에서 wafer edge에 집중되는 void와 chip offset을 공간·시간·설비·소재 관점으로 분해하고, 원인 가설을 검증한 뒤 recipe 수준의 개선안과 포트폴리오 수준 Control Concept을 제시한다.

이 프로젝트의 분석 범위는 **chip-first wafer-level compression molding**을 가정한 project scenario이다. 특정 회사의 실제 recipe, 설비 사양 또는 품질 규격을 재현하지 않는다.

## 데이터 고지

> 본 데이터는 공개 문헌과 공정 메커니즘을 참고하여 프로젝트 검증 목적으로 생성한 synthetic engineering dataset이다.

생성 데이터는 단순 random noise가 아니라 진공, 수지 유동, 온도, vent, film tension과 CTQ 사이의 명시적 인과 구조를 포함한다. 실제 SK하이닉스/Fab 데이터와 생산 recipe는 사용하지 않았다.

## 문제 해결 흐름

1. STEP 0 — 공정·장비·입출력·4M+Measurement 이해 **(완료)**
2. STEP 1 — 현상과 Y/CTQ, Engineering Target 정의 **(완료)**
3. STEP 2 — wafer/lot/equipment/time pattern 시각화 **(완료)**
4. STEP 3 — 공학 가설과 반증 기준 수립 **(완료)**
5. STEP 4 — physics-informed synthetic data와 DOE 분석 **(완료)**
6. STEP 5 — 측정시스템 확인 **(완료)**
7. STEP 6 — 통계·DOE uncertainty·Root Cause 판정 **(완료)**
8. STEP 7 — 개선 검증·Side Effect·포트폴리오 수준 Control Concept **(완료)**
9. FINAL — A3, 면접 답변, 자기소개서 Summary, GitHub 공개 가이드 **(완료)**

## 최종 포트폴리오 바로가기

- [`report/A3_report.md`](report/A3_report.md): 현상–가설–물리식–검증–개선–한계를 한 장 흐름으로 정리
- [`report/interview_summary.md`](report/interview_summary.md): 1분/3분 설명과 SK하이닉스 P&T 예상 질문 12개
- [`report/cover_letter_summaries.md`](report/cover_letter_summaries.md): 자기소개서 약 100·300·500자 버전
- [`report/github_beginner_guide.md`](report/github_beginner_guide.md): GitHub Desktop 및 PowerShell 첫 업로드 가이드

## 전체 산출물

- [`notebooks/01_process_understanding.ipynb`](notebooks/01_process_understanding.ipynb): 공정 목적, 장비 구조, sequence, parameter, CTQ, failure mode, sensor, 4M+Measurement
- [`report/01_problem_definition.md`](report/01_problem_definition.md): 열–유동–경화 중심의 문제 제기, 경쟁 가설 2개, 판별 실험과 개선 시도
- [`notebooks/02_eda.ipynb`](notebooks/02_eda.ipynb): 공간·설비·시간·소재 관점 EDA 재현 notebook
- [`report/02_eda_findings.md`](report/02_eda_findings.md): 8개 Figure의 Observation / Engineering Interpretation / Next Action
- [`results/root_cause_evidence.csv`](results/root_cause_evidence.csv): H1~H3와 측정기인 Evidence Level
- [`report/03_hypothesis_validation_plan.md`](report/03_hypothesis_validation_plan.md): 열역학·표면거칠기·기계공학 통합 모델과 판별 실험
- [`notebooks/03_hypothesis_test.ipynb`](notebooks/03_hypothesis_test.ipynb): 6개 경쟁 가설과 DOE 검토 notebook
- [`results/hypothesis_validation_matrix.csv`](results/hypothesis_validation_matrix.csv): 예상 signature, 판별법, 개선안, 반증 기준
- [`results/doe_run_matrix.csv`](results/doe_run_matrix.csv): 4 whole plots × 9 runs의 36-run split-plot DOE
- [`notebooks/04_modeling.ipynb`](notebooks/04_modeling.ipynb): 물리 feature, DOE effect, multi-response optimization
- [`report/04_doe_results.md`](report/04_doe_results.md): 주효과·교호작용·표면 trade-off·simulated confirmation
- [`report/04_engineering_literature_basis.md`](report/04_engineering_literature_basis.md): 물리식, peer-reviewed 논문, Kaggle/GitHub 활용 경계
- [`data/DATA_SOURCES.md`](data/DATA_SOURCES.md): synthetic/public data provenance와 사용 제한
- [`results/doe_effects.csv`](results/doe_effects.csv): high-minus-low effect와 model R²
- [`results/doe_ranked_conditions.csv`](results/doe_ranked_conditions.csv): multi-response desirability 순위
- [`notebooks/05_measurement_system.ipynb`](notebooks/05_measurement_system.ipynb): crossed ANOVA GR&R와 operator bias 분석
- [`report/05_measurement_system_analysis.md`](report/05_measurement_system_analysis.md): Void/Offset/Ra 측정시스템 개선 전후 판정과 reference/requalification 필요성
- [`results/msa_summary.csv`](results/msa_summary.csv): repeatability, reproducibility, %Tolerance, ndc
- [`notebooks/05_optimization.ipynb`](notebooks/05_optimization.ipynb): bootstrap effect와 MSA-guarded robust optimization
- [`report/06_root_cause_verification.md`](report/06_root_cause_verification.md): 최종 causal claim boundary와 robust process window
- [`results/bootstrap_effects.csv`](results/bootstrap_effects.csv): 4개 whole-plot contrast의 bootstrap CI
- [`results/robust_process_window.csv`](results/robust_process_window.csv): MSA +3σ와 4개 CTQ 제약을 만족하는 조건 grid
- [`results/root_cause_verification_matrix.csv`](results/root_cause_verification_matrix.csv): 주장별 근거·판정·남은 실제 실험
- [`notebooks/06_confirmation.ipynb`](notebooks/06_confirmation.ipynb): 추천·경계·창 밖 조건의 12회 반복 비교
- [`report/07_improvement_verification_control_concept.md`](report/07_improvement_verification_control_concept.md): confirmation, side effect와 관리 개념
- [`results/confirmation_summary.csv`](results/confirmation_summary.csv): mean/std/P95/all-CTQ pass rate
- [`results/side_effect_matrix.csv`](results/side_effect_matrix.csv): 개선 parameter별 benefit와 trade-off
- [`results/control_concept.csv`](results/control_concept.csv): 무엇을 왜 확인하고 어떤 실제 데이터가 필요한지

## STEP 2 주요 결과

- Synthetic baseline: Edge Void 1.75%, Chip Offset P95 41.3 μm, Warpage P95 921 μm
- Edge/Center void ratio: 7.6배 → random보다 공간 pattern
- Worst chamber: `EQ02_C2`; chamber η² = 0.38
- Worst material genealogy: `M03`
- Process margin과 Edge Void 상관: -0.78
- 최종 evidence: H1 Strong, H2 Medium-Strong, H3 Medium; measurement confounding은 recipe lock 후 감소했으나 완전히 제거됐다고 주장하지 않음

이 결과는 synthetic causal structure에 대한 EDA이며 실제 생산 인과관계나 SK하이닉스 공정 성능을 의미하지 않는다.

## STEP 3 핵심 공학 모델

- Void: `M_process = t_gel − t_vac − t_fill`
- Chip shift: `SF_shift = F_hold / (F_drag + F_film + F_pressure_asymmetry)`
- Surface: Ra 단독이 아니라 Rz, texture, contact angle, 열접촉저항과 interface shear strength를 함께 평가
- DOE: EMC lot·film roughness를 hard-to-change whole-plot factor로, vacuum·zone range·closing speed를 sub-plot factor로 설계

## STEP 4 Project Scenario 결과

- 선택 조건: M02 / Smooth / 4.5 kPa abs / zone range 1.5 °C / closing 0.85 mm/s
- Overall desirability: 0.829
- Simulated confirmation: Edge Void 1.68 → 0.41%, Chip Offset P95 40.6 → 17.0 μm
- Side effect: Warpage 931 → 674 μm, Cycle Time Index 101.7 → 103.8 (+2.1%)
- 결과는 실제 개선 실적이 아니라 physics-informed synthetic confirmation이다.

## STEP 5 MSA 결과

- Edge Void: %Tolerance 45.9 → 12.2%, Not capable → Conditional
- Chip Offset: 23.1 → 10.1%, Conditional
- Surface Ra: 18.4 → 5.9%, Capable
- DOE와 optimization에는 검사 recipe lock 이후 데이터만 사용한다.

## STEP 6 Root Cause Verification

- Edge Void effect: Vacuum +0.48%p, Zone range +0.99%p, Closing speed +0.24%p
- Vacuum×Zone interaction 평균은 +0.12%p이나 bootstrap CI가 0을 포함해 확정하지 않음
- M02/Smooth grid 567개 중 MSA +3σ까지 만족한 robust pass는 3개 조합
- Robust 조합 범위: vacuum 4.50–4.75 kPa abs, zone range 1.50°C, speed 0.85–0.90 mm/s
- H1만 synthetic 조작 evidence를 가지며 H2~H5는 주장 강도를 제한함

## STEP 7 Confirmation & Side Effect

- Recommended, vacuum boundary, speed boundary, zone-outside 조건을 각 12회 반복
- Recommended synthetic result: Edge Void 0.40%, Offset P95 16.7 μm, Warpage 656 μm, Cycle Index 104.1
- Recommended all-CTQ pass rate 100%; zone-outside challenge 91.7%
- 핵심 trade-off: vacuum/slow closing 개선 대비 cycle time 증가 가능성
- 실제 sampling frequency, warning/control limit, OCAP은 설정하지 않음

## 재현 방법

프로젝트 루트에서 다음 순서로 실행한다.

```bash
python src/generate_data.py
python src/preprocess.py
python src/analysis.py
python src/visualization.py
```

## 다음 의사결정 게이트

다음 단계에서는 GitHub README, A3 report, 1분 면접 설명, 자기소개서 100/300/500자와 SK하이닉스 연결 질문 답변을 묶어 최종 포트폴리오 패키지를 완성한다.

## 공개 근거

- Yeon et al., *Compensation Method for Die Shift Caused by Flow Drag Force in Wafer-Level Molding Process* (2016): https://doi.org/10.3390/mi7060095
- Guo and Young, *Vacuum effect on the void formation of the molded underfill process in flip chip packaging* (2015): https://doi.org/10.1016/j.microrel.2014.12.001
- Hsu et al., *Compression Molding Flow Behavior and Void Optimization of an Integrated Circuit Package with Shielding-Metal-Frame* (2025): https://doi.org/10.3390/polym17101301
