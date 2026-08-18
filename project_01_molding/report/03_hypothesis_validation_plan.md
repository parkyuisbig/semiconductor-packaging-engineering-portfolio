# PROJECT 1 · STEP 3 — 열역학·표면거칠기·기계공학 기반 가설 검증

## 1. 추천 통합 Engineering Model

가장 추천하는 문제 연결은 다음 두 조건을 동시에 보는 것이다.

### 조건 A — Void: evacuation/filling/cure time-scale 경쟁

```text
Heater-zone 온도와 EMC 열이력
              ↓
점도 μ(T, α), gel time, wetting 변화
              ↓
t_vac + t_fill 과 t_gel의 경쟁
              ↓
잔류 기체 배출 전 flow-front closure
              ↓
Edge void
```

1차 공정 margin은 다음처럼 정의한다.

`M_process = t_gel − t_vac − t_fill`

`M_process`가 작아질수록 충전 가능한 시간이 부족하다. 온도는 점도를 낮춰 유동을 돕기도 하지만 경화를 가속해 gel time을 줄이기도 하므로 단조 관계로 가정하지 않는다.

### 조건 B — Chip Offset: 유동 하중과 계면 holding force의 경쟁

`Safety Factor_shift = F_hold / (F_drag + F_film + F_pressure_asymmetry)`

- `F_drag ≈ Δp·A_projected + τ·A_wetted`
- `F_hold`: tape/die 계면의 접착·마찰·실접촉면적에 의한 저항
- `F_film`: release-film tension imbalance에 의한 횡력
- `F_pressure_asymmetry`: platen/vent/charge 비대칭에 의한 합력

`Safety Factor_shift < 1`이면 die가 미끄러질 가능성이 커진다. 이 식의 목적은 정확한 절대 하중 예측보다 **어떤 힘과 경계조건을 측정해야 하는지 결정하는 것**이다.

### 통합 판정

| Process margin | Shift safety factor | 예상 현상 | 우선 조치 |
|---|---|---|---|
| 충분 | 충분 | 정상 | 유지·SPC |
| 부족 | 충분 | Void 중심 | vacuum/온도/flow window |
| 충분 | 부족 | Offset 중심 | adhesion/roughness/tension |
| 부족 | 부족 | Void + Offset 동시 | coupled recipe + interface 개선 |

이 2×2 구조는 void와 offset을 무조건 같은 원인으로 묶는 오류를 방지한다.

---

## 2. 열역학적 관점

### 2.1 EMC 온도–점도–경화의 이중 효과

EMC 점도는 온도 상승 초기에는 낮아질 수 있지만 cure conversion `α`가 증가하면 빠르게 상승한다. 개념 모델은 다음처럼 둔다.

`μ = μ(T, α)`

`dα/dt = k(T)·f(α)`, `k(T) = A exp(−Ea/RT)`

따라서 평균 mold temperature만으로 분석하지 않고 다음 waveform feature를 사용한다.

- edge/center zone range
- heating rate와 overshoot
- vacuum 완료 시점의 EMC temperature
- compression 시작부터 pressure plateau까지의 시간
- gel-time proxy 대비 evacuation+fill time

### 2.2 포획 기체와 압력

단순 점검에는 `P₁V₁ ≈ P₂V₂`를 사용해 잔류 기체 압축 가능성을 본다. 실제로는 leak, outgassing, EMC volatile, gas dissolution 때문에 이상기체 단독 모델로 void 크기를 예측하지 않는다.

### 2.3 열전달 경계조건

표면거칠기와 실제 접촉면적은 계면 열접촉저항 `R_contact`를 바꿀 수 있다.

`q = ΔT / R_contact`

동일 heater setting에서도 carrier/tape/film 접촉상태가 다르면 die 주변 실제 열이력이 달라질 수 있다. 따라서 장비 zone sensor와 실제 package 근처 온도가 같다고 가정하지 않고 thin thermocouple 또는 calibration coupon으로 확인한다.

### 열역학 검증 시도

1. Edge/center calibration coupon의 실측 thermal lag 비교
2. 동일 평균온도에서 zone range만 변화시킨 DOE
3. Vacuum 완료 시점과 compression 시작 시점의 temperature overlay
4. DSC/gel-time 또는 간이 rheology proxy와 공정 trace 결합
5. `M_process`와 Edge Void의 dose-response 및 threshold 확인

---

## 3. 표면거칠기와 계면 관점

### 3.1 왜 Ra 하나만 보면 안 되는가

동일 Ra라도 peak/valley 형상과 방향성이 다를 수 있다. 최소한 다음을 함께 본다.

- `Ra`: 평균 거칠기
- `Rz`: peak-to-valley 성격
- skewness 또는 texture 방향
- contact angle: EMC/표면 젖음성 proxy
- 표면 오염과 surface energy
- coupon shear/pull strength: 실제 holding force proxy

거칠기가 증가하면 mechanical interlocking과 실효 마찰이 커질 수 있지만, 동시에 valley에 기체·오염을 가두거나 실접촉면적과 열전달을 악화시킬 수도 있다. 따라서 “거칠수록 좋다/나쁘다”라고 선결론을 두지 않고 **최적 window가 존재하는지** 검증한다.

### 3.2 두 개의 표면을 분리한다

| Interface | 주요 역할 | 불량 연결 | 필요한 측정 |
|---|---|---|---|
| Die backside–adhesive tape | die holding | chip slip/rotation | Ra/Rz, 오염, tack, die shear |
| EMC–release film/mold surface | wetting·gas path·demold | void, imprint, demold stress | Ra/Rz, contact angle, film tension, surface defect |

### 3.3 표면가설 검증 시도

1. 위치별 optical profilometer 측정: center/edge, MD/TD 방향
2. 동일 표면 3회 반복 측정으로 profiler repeatability 확인
3. Contact-angle coupon으로 cleaning/plasma 전후 surface energy 변화 비교
4. Roughness class별 die shear test와 열노출 후 strength retention 비교
5. 동일 EMC·chamber·recipe에서 roughness class만 바꾼 split run
6. Offset 방향이 texture 또는 film machine direction과 정렬되는지 circular/vector analysis

### 개선 후보

- 단일 최대/최소가 아니라 Ra–Rz–contact angle–shear strength의 관리 window
- Cleaning 또는 plasma 조건 lock과 대기시간 관리
- Film roll/wafer position별 surface metrology sampling
- Incoming roughness와 contact-angle reference coupon
- Interface shear strength가 flow load보다 충분한 safety factor를 갖도록 specification 설정

프로젝트의 `Ra = 0.25/0.65 μm`는 DOE 구조를 표현하기 위한 Engineering Scenario이며 산업 표준값이 아니다.

---

## 4. 기계공학적 관점

### 4.1 압력 구배와 점성 drag

EMC의 비대칭 유동은 die 전후의 pressure difference와 surface shear를 만든다. Chip offset magnitude만 보지 않고 `(dx, dy)` vector가 radial direction, vent direction, film direction 중 무엇과 정렬되는지 확인한다.

### 4.2 Release-film tension

Left/right tension 차이는 film 변형과 횡력을 만들 수 있다. **Tension reversal test**에서 offset 방향이 함께 반전되면 H4 evidence가 강해진다. 방향이 유지되면 vent/charge/platen geometry를 우선한다.

### 4.3 Platen parallelism·Chuck flatness·Pressure uniformity

평행도와 평탄도 불량은 cavity gap, local flow resistance와 pressure distribution을 바꾼다.

- pressure-sensitive film 또는 calibration wafer map
- platen gap/parallelism 측정
- chuck ID 및 radial position 반복성
- 장비 회전 또는 wafer orientation reversal test

설비 좌표계를 따라가면 equipment geometry, wafer 좌표계를 따라가면 material/layout, film 방향을 따라가면 tension/texture 가능성이 높다.

### 4.4 Warpage side effect

온도와 압력을 바꾸면 CTE mismatch, cure shrinkage와 잔류응력이 달라진다. Void/offset 개선 조건도 Warpage P95가 Engineering Target을 벗어나면 채택하지 않는다.

---

## 5. 경쟁 가설과 판별 실험

| Hypothesis | 예상 signature | 결정적 판별 시도 | 맞다면 개선 | 기각 기준 |
|---|---|---|---|---|
| H1 열–유동–경화×진공 | edge threshold, margin dose-response, interaction | short-shot + process DOE | vacuum-ready interlock, staged closing, zone matching | block 후 margin 효과 재현 안 됨 |
| H2 Vacuum/Vent 열화 | chamber/PM age, leak/pump-down drift | chamber swap + PM 전후 + leak test | condition PM, actual trace interlock | 소재를 따라가고 chamber trace 정상 |
| H3 Roughness/Wetting/Adhesion | Ra/Rz/contact angle/shear와 offset | roughness split + coupon shear | surface window, cleaning, adhesion margin | flow load 일치 시 roughness 효과 없음 |
| H4 Tension/Parallelism | offset 방향이 설비/film 좌표와 정렬 | tension·orientation reversal | tension matching, platen/chuck PM | 방향 반전·좌표 고정성 없음 |
| H5 EMC 소재 이력 | lot genealogy, viscosity/gel dose-response | normal/suspect lot cross split | storage/floor-life/incoming control | material swap 후 chamber만 추종 |
| H6 Measurement | repeat scan/tool/recipe 의존 | blind repeat + cross-tool study | threshold/registration lock | 반복성 양호, physical signature 유지 |

전체 상세 matrix는 `results/hypothesis_validation_matrix.csv`에 저장한다.

---

## 6. 36-run Split-plot DOE

### 설계 이유

EMC lot과 release-film roughness는 run마다 쉽게 바꾸기 어려운 hard-to-change 요인이다. 이를 whole-plot factor로 두고 각 block 안에서 공정인자 3개를 무작위화한다.

### Whole-plot factor

- EMC lot: baseline `M02`, suspect `M03`
- Film roughness class: Smooth/Texture, project scenario `Ra 0.25/0.65 μm`

### Sub-plot process factor

| Factor | Low (−1) | Center (0) | High (+1) | 해석 주의 |
|---|---:|---:|---:|---|
| A. Vacuum base pressure | 4.5 kPa abs | 5.5 | 6.5 | 낮을수록 더 강한 vacuum |
| B. Heater zone range | 1.5 °C | 2.5 | 3.5 | 평균온도가 아니라 zone 편차 |
| C. Closing speed | 0.85 mm/s | 1.00 | 1.15 | project scenario 값 |

각 whole plot에 `2³ = 8` factorial run과 center point 1개를 배치한다. 총 `4 × 9 = 36 runs`이다.

### Response

- Primary: Edge Void Area Ratio, Chip Offset P95
- Secondary: Warpage, Cycle Time
- Mechanism response: pump-down time, actual zone range, process margin
- Surface response: Ra/Rz, contact angle, interface shear strength

### 분석 model

`Y ~ A*B*C + EMC + Roughness + EMC:Roughness + Roughness:B + whole_plot(random)`

Split-plot error structure를 무시하면 hard-to-change factor의 유의성을 과대평가할 수 있다. p-value와 함께 effect size, confidence interval, residual pattern과 engineering significance를 본다.

### Run acceptance

- actual vacuum/temperature/speed가 설정 허용범위 안에 들어온 run만 DOE model에 사용
- alarm, loading error, measurement failure는 삭제하지 않고 deviation으로 기록
- run 순서와 timestamp를 보존해 warm-up/time drift를 확인
- center point curvature가 확인되면 RSM 단계로 확장

실행표: `results/doe_run_matrix.csv`

---

## 7. Measurement Gate

DOE 전에 다음을 통과해야 한다.

1. Void 검사: 동일 sample 반복 scan, threshold sensitivity, cross-tool comparison
2. Offset: coordinate registration residual과 stage drift
3. Roughness: 5개 coupon × 3 반복 × 위치/방향, profiler resolution 확인
4. Contact angle: droplet volume, 측정시간, 표면 대기시간 표준화
5. Shear strength: fixture alignment, loading rate, 파괴모드 기록

거칠기 값이 같아도 파괴가 adhesive/cohesive 중 어디에서 일어나는지 다르면 holding mechanism이 다르므로 failure surface를 함께 기록한다.

---

## 8. 개선 의사결정 규칙

1. H1 interaction이 재현되고 H3가 약하면 recipe/설비 window를 우선 조정한다.
2. H3 roughness×temperature 또는 shear safety factor가 강하면 표면 specification과 cleaning을 함께 변경한다.
3. H4 tension reversal이 확인되면 recipe보다 tension/parallelism calibration을 우선한다.
4. H5가 chamber를 넘어 재현되면 material hold와 genealogy rule을 우선 적용한다.
5. 어떤 조건도 Void만 좋아지고 Warpage 또는 Cycle Time이 기준을 벗어나면 채택하지 않는다.

현재 단계의 결론은 **H1 우선 검증, H2 병렬 설비 확인, H3를 신규 핵심 경계조건으로 승격**하는 것이다.

---

## 9. 자기소개서용 연결 문장

> Compression molding의 edge void와 chip offset을 열–유동 문제로만 보지 않고, `t_gel−t_vac−t_fill` 공정 margin과 `계면 holding force/유동 하중`의 두 경쟁조건으로 재정의했습니다. 특히 die backside와 release film의 표면거칠기가 접착력·젖음성·열접촉저항을 동시에 바꿀 수 있다는 가설을 추가해 Ra뿐 아니라 Rz, 접촉각, 전단강도를 검증하도록 설계했습니다. 또한 EMC lot과 film roughness를 whole-plot factor로, vacuum·heater-zone 편차·closing speed를 sub-plot factor로 둔 36-run DOE를 구성해 실제 양산 장비의 조건 변경 제약까지 반영했습니다.

