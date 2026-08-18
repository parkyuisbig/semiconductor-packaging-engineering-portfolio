# PROJECT 1 · STEP 4 — 물리식·논문·공개 데이터 근거

## 1. 근거 사용 원칙

이 프로젝트는 출처를 세 종류로 구분한다.

1. **Peer-reviewed paper:** 물리 메커니즘과 governing equation의 근거
2. **Kaggle/UCI public dataset:** 데이터 구조와 분석법의 외부 benchmark
3. **GitHub implementation:** 재현 가능한 coding pattern 참고

Kaggle·GitHub 결과를 물리적 root cause의 근거로 사용하지 않는다. 논문 식도 material parameter를 실측하지 않은 상태에서는 절대값 예측식이 아니라 causal direction 또는 model structure로만 사용한다.

---

## 2. Compression molding과 die shift

### 2.1 반경 방향 유속 증가

Bu et al.은 wafer compression molding의 축대칭 질량보존 관계를 다음과 같이 전개했다.

`V₁A₁ = V₂A₂`

`A₁ = πr²`, `A₂ = 2πrh`이면

`V₂ = (r / 2h) V₁`

- `V₁`: mold/platen 방향 속도
- `V₂`: 반경 방향 EMC 속도
- `r`: 현재 flow radius
- `h`: 유동 gap

`r`이 커지고 `h`가 작아질수록 edge 방향 유속과 drag가 증가할 수 있다는 점이 edge die shift의 기계공학적 근거다. 논문은 filling speed 감소 등으로 drag를 줄이는 방안을 제시한다. [Bu et al., IEEE TCPMT, 2013](https://doi.org/10.1109/TCPMT.2013.2268192)

### 2.2 Die에 작용하는 유동 하중

본 프로젝트는 die의 합력을 다음 control-volume 형태로 해석한다.

`F_flow = ∫A (−p n + τ) dA`

단순 screening에는

`F_drag ≈ Δp·A_projected + τ·A_wetted`

를 사용한다. 이는 본 프로젝트의 축약식이며 절대 shift 예측식이 아니다. Yeon et al.은 molding, thermal expansion/contraction, warpage에 의한 die movement를 구분해 flow-drag 성분을 평가했다. [Yeon et al., Micromachines, 2016](https://doi.org/10.3390/mi7060095) 최근 panel-level 연구도 cavity floor와 die sidewall의 local shear stress를 적분해 resultant force를 계산한다. [Journal of Mechanics, die-shift prediction methodology](https://doi.org/10.1093/jom/ufaf044)

### 2.3 열변형과 유동변형의 분리

Die shift에는 flow-induced movement뿐 아니라 CTE expansion/contraction과 debond 이후 warpage-induced apparent movement가 포함된다. 따라서 좌표는 최소한 placement 후, mold 후, debond 후에 측정해야 한다. Flow와 thermo-mechanical mechanism을 함께 고려해야 한다는 근거는 12-inch FOWLP 연구에서도 제시된다. [Han et al., ECTC 2016](https://doi.org/10.1109/ECTC.2016.46)

---

## 3. EMC 열경화 kinetics와 점도

### 3.1 Kamal–Sourour autocatalytic cure model

대표적인 형태는 다음과 같다.

`dα/dt = (k₁ + k₂ αᵐ)(1−α)ⁿ`

`kᵢ(T) = Aᵢ exp(−Eᵢ/RT)`

- `α`: degree of cure
- `m, n`: reaction order
- `Aᵢ`: pre-exponential factor
- `Eᵢ`: activation energy
- `R`: gas constant
- `T`: absolute temperature

EMC에 대해 DSC/DEA 기반으로 Kamal–Sourour와 isoconversional model을 비교한 연구는 temperature와 cure conversion의 결합을 뒷받침한다. [Franieck et al., Polymers, 2021](https://doi.org/10.3390/polym13111734)

**본 프로젝트 적용:** `t_gel`이 온도와 소재 lot에 따라 달라진다는 causal structure에 사용한다.

**한계:** 실제 `A, E, m, n`을 DSC/DEA로 fitting하지 않았으므로 synthetic coefficient를 EMC material constant로 표현하지 않는다.

### 3.2 Cross–Castro–Macosko 계열 점도 model

EMC mold-flow 연구에서 viscosity는 shear rate, temperature와 cure conversion의 함수로 다뤄진다.

`η = η(γ̇, T, α)`

대표 구조는 다음처럼 정리할 수 있다.

`η(γ̇,T,α) = η₀(T,α) / [1 + (η₀γ̇/τ*)^(1−n)]`

`η₀(T,α) = B exp(Tb/T) [αg/(αg−α)]^(c₁+c₂α)`

- `γ̇`: shear rate
- `τ*`: critical stress parameter
- `n`: shear-thinning index
- `αg`: gel conversion

Cross–Macosko viscosity와 Kamal cure kinetics를 결합한 packaging mold-flow 사례가 보고되어 있다. [Moldflow simulation of an exposed-pad package](https://doi.org/10.4071/isom-2015-TP65)

**본 프로젝트 적용:** 온도 상승 초기의 viscosity 감소와 cure 진행에 따른 viscosity divergence가 경쟁한다는 논리에 사용한다.

**한계:** 계수와 gel conversion은 소재별 rheometer/DSC fitting이 필요하다.

### 3.3 Project process margin

위 두 model에서 포트폴리오용으로 파생한 screening 지표다.

`M_process = t_gel − t_vac − t_fill`

이 식은 문헌의 표준식이 아니라 **본 프로젝트가 제안한 engineering KPI**다. 물리적 의미는 명확하지만 실제 사용 전 short-shot, rheology와 inline trace로 calibration해야 한다.

---

## 4. Vacuum과 void

### 4.1 포획 기체 압축

1차 screening에는 등온 이상기체 가정을 사용한다.

`P₁V₁ = P₂V₂`

Vacuum이 충분하지 않으면 초기 `P₁`이 높아 동일 molding pressure에서 더 큰 residual gas volume이 남을 수 있다. 실제 EMC에는 leak, volatile, outgassing과 gas dissolution이 있어 이 관계만으로 void 크기를 계산하지 않는다.

Molded underfill 실험에서는 material마다 필요한 진공 수준이 다를 수 있지만 air pocket 제거에 충분한 vacuum quality가 필요하다고 보고했다. [Guo & Young, Microelectronics Reliability, 2015](https://doi.org/10.1016/j.microrel.2014.12.001)

### 4.2 Flow-front merging

서로 다른 flow front가 합쳐질 때 배출 경로가 닫히면 기체가 포획될 수 있다. Compression molding에서 geometry, vent와 vacuum을 포함해 void 위치를 분석한 사례가 있다. [Hsu et al., Polymers, 2025](https://doi.org/10.3390/polym17101301)

**프로젝트 signature:** edge-localized void, vent 방향 비대칭, pump-down/leak-up drift와 PM 후 회복.

---

## 5. 표면거칠기·젖음·기체 포획

### 5.1 Young과 Wenzel relation

평탄하고 이상적인 표면의 Young relation은

`γSV − γSL = γLV cosθY`

로 쓸 수 있다. 균질한 rough surface가 완전히 젖는 Wenzel state에서는

`cosθ* = r cosθY`

- `r`: true area / projected area, `r ≥ 1`
- `θY`: ideal Young contact angle
- `θ*`: apparent contact angle

Wenzel의 원 논문은 roughness와 apparent contact angle 관계를 제시했다. [Wenzel, 1949](https://doi.org/10.1021/j150474a015) 후속 이론 연구는 drop 크기가 roughness scale보다 충분히 큰 등의 조건에서만 단순 Wenzel 식이 성립하며 항상 global free-energy minimum을 주지는 않는다고 지적한다. [Wolansky & Marmur, 1999](https://doi.org/10.1016/S0927-7757(99)00098-9)

**본 프로젝트 적용:** Ra 증가가 wetting을 자동으로 개선한다고 가정하지 않고 contact angle을 직접 측정한다.

### 5.2 Capillary pressure

곡률을 가진 계면의 Young–Laplace relation은

`ΔPcap = γ(1/R₁ + 1/R₂)`

단순 cylindrical pore에서는

`ΔPcap ≈ 2γ cosθ / r_pore`

로 표현할 수 있다. Roughness valley의 크기, wetting과 gas path가 void 포획에 영향을 줄 수 있지만 실제 filler-rich EMC는 단순 Newtonian liquid나 단일 pore가 아니므로 방향성 model로만 사용한다.

### 5.3 Adhesion과 roughness의 비단조성

Roughness는 mechanical interlocking을 높일 수 있지만 불완전 wetting, void, stress concentration과 real contact loss를 만들 수도 있다. Adhesive thickness 대비 roughness scale에 따라 adhesion energy가 달라질 수 있다는 실험/해석 연구가 있다. [Adherend surface roughness effect on adhesive joints](https://doi.org/10.1016/j.ijadhadh.2020.102779)

**필요 실험:** Ra, Rz, skewness/texture, contact angle, die shear strength와 failure mode를 함께 측정한다.

---

## 6. 표면거칠기와 열접촉저항

### 6.1 CMY thermal contact conductance

Rough conforming solid contact의 대표적인 Cooper–Mikic–Yovanovich 형태는 다음과 같다.

`h_c ≈ 1.25 k_s (m/σ) (P/H_c)^0.95`

- `h_c`: thermal contact conductance
- `k_s`: 두 재료 열전도율의 harmonic mean
- `m`: asperity slope
- `σ`: effective RMS roughness
- `P`: apparent contact pressure
- `H_c`: softer material의 microhardness

원 모델은 random rough surface의 접촉 열전달을 다룬다. [Cooper, Mikic & Yovanovich, 1969](https://doi.org/10.1016/0017-9310(69)90011-8)

**본 프로젝트 적용:** roughness 증가 또는 contact pressure 감소가 package 근처 실제 temperature와 heater setting의 차이를 만들 수 있다는 가설에 사용한다.

**중요 한계:** CMY는 주로 dry solid contact와 특정 deformation 가정을 둔다. Polymer film/adhesive가 존재하는 본 계면에는 그대로 대입하지 않고 calibration coupon으로 `R_contact = ΔT/q`를 실측한다.

---

## 7. Chip holding과 기계적 safety factor

본 프로젝트의 힘 평형 기반 screening KPI는 다음과 같다.

`SF_shift = F_hold / (F_drag + F_film + F_pressure_asymmetry)`

- `F_hold`: die backside–tape shear/adhesion proxy
- `F_drag`: EMC pressure+shear resultant
- `F_film`: release-film tension imbalance
- `F_pressure_asymmetry`: platen/vent/charge 비대칭

이는 표준문헌식이 아니라 자유물체도에서 파생한 **본 프로젝트 식**이다. `SF_shift < 1`은 slip 위험 방향을 뜻하지만 실제 threshold는 dynamic shear test로 보정해야 한다.

방향 판별에는 offset vector의 기준좌표계를 이용한다.

- wafer radial을 추종 → radial mold flow 가능성
- vent/equipment 좌표를 추종 → 설비 geometry 가능성
- film machine direction을 추종 → texture/tension 가능성
- debond 후에만 증가 → thermal/warpage apparent shift 가능성

---

## 8. 공개 데이터와 코드 자원의 올바른 사용

| Resource | 무엇을 참고하는가 | 이 프로젝트에서 하지 않을 주장 |
|---|---|---|
| [Kaggle WM-811K](https://www.kaggle.com/datasets/qingyi/wm811k-wafer-map) | Edge-Ring/Edge-Loc 등 공간 pattern representation과 class imbalance | Front-end wafer map pattern이 package molding root cause를 직접 증명한다고 하지 않음 |
| [GitHub WM811K industrial dataset note](https://github.com/kweyuchesa/industrial-datasets/blob/master/markdown/wm811k_wafer_maps.md) | 2D die-map encoding, lot/wafer field와 공개 benchmark provenance | GitHub 설명을 물리 논문 대신 인용하지 않음 |
| [AWS WM811K analysis example](https://github.com/aws-samples/amazon-ec2-nice-dcv-semiconductor-wafer-data) | 재현 가능한 wafer-map loading/visualization workflow | 분류 정확도를 root-cause 성능으로 표현하지 않음 |
| [Kaggle UCI SECOM](https://www.kaggle.com/datasets/paresh2047/uci-semcom) | 다변량 sensor, missingness, rare fail, timestamp 분석 구조 | 익명 sensor importance를 특정 vacuum/temperature 원인으로 명명하지 않음 |
| [GitHub SECOM data note](https://github.com/Be1an001/semiconductor-pass-fail-prediction-python/blob/main/data/README.md) | 590 anonymous sensor + label/timestamp ingestion pattern | anonymous feature를 물리적으로 해석하지 않음 |
| [GitHub SECOM imbalance example](https://github.com/Meena-Mani/SECOM_class_imbalance) | rare failure, feature selection, imbalance 처리 참고 | 높은 분류성능을 공정 개선 근거로 사용하지 않음 |

WM-811K는 811,457개의 실제 wafer map과 9개 pattern class를 포함하는 공간 분석 benchmark로 소개되어 있다. 그러나 본 프로젝트는 package-level synthetic map이므로 dataset을 섞지 않고 **시각화·pattern taxonomy 참고**로만 사용한다. UCI SECOM도 public sensor benchmark지만 feature가 익명이므로 **pipeline robustness 참고**로만 사용한다.

---

## 9. 포트폴리오 Evidence Chain

| Claim | Literature | Project data signature | Verification experiment | Action |
|---|---|---|---|---|
| Thermal/cure margin이 void를 악화 | Kamal–Sourour, Cross–Macosko | margin–void correlation, A×B interaction | DSC/DEA + short-shot + DOE | zone matching, vacuum-ready interlock |
| Vacuum/vent가 air pocket을 남김 | vacuum molded-underfill paper | pump-down/PM-age/edge pattern | leak test, vent-clean split | condition PM, actual-vacuum lock |
| Flow drag가 die shift를 유발 | Yeon/Bu/Han studies | radial vector, speed effect | stage-wise coordinates, speed DOE | staged/slow closing, alignment compensation |
| Roughness가 wetting/holding을 바꿈 | Wenzel/adhesion/contact literature | contact angle–void, shear–offset trade-off | profilometry, contact angle, coupon shear | surface window, cleaning/tension control |
| Roughness가 thermal boundary를 바꿈 | CMY contact conductance | zone setting vs local coupon ΔT | thermal coupon calibration | pressure/flatness/surface control |

최종 결론은 `문헌 Mechanism + 공간/시간 데이터 + 통계 interaction + 반증 실험`이 동시에 맞을 때만 Root Cause로 승격한다.
