# PROJECT 1 — 면접 설명 및 Package & Test 직무 연결

## 1분 설명

> Compression molding에서 wafer edge void와 방향성 chip offset이 함께 증가하는 문제를 다뤘습니다. 저는 이를 단순 진공 부족이 아니라 EMC의 온도 의존 점도와 경화, 실제 배기 시간, radial flow drag가 결합된 열–유동–경화 margin 문제로 정의했습니다. 먼저 wafer map과 offset vector, chamber·PM·material genealogy를 분석하고, 측정 recipe를 고정한 뒤 zone range·vacuum·closing speed DOE로 가설을 검증했습니다. Synthetic DOE에서는 heater-zone 불균일과 evacuation margin 감소가 가장 강한 원인이었고, vacuum/vent는 설비 악화요인, 표면거칠기는 wetting과 holding force를 바꾸는 후보로 구분했습니다. MSA 오차까지 포함해 3개 robust 조합을 찾았고, 12회 synthetic confirmation에서 void 1.77%를 0.40%, offset P95 41.1 μm를 16.7 μm로 낮추는 개선 후보를 확인했습니다. 다만 실제 양산 결과가 아니므로, 현업 적용 전 chamber·material block 검증과 requalification이 필요하다고 명확히 제한했습니다.

## 3분 설명 구조

1. **현상:** Edge에 집중된 void와 한 방향/radial chip offset이 동시에 발생했다.
2. **문제 재정의:** 두 CTQ가 공통 flow field의 결과일 수 있다고 보고 `M_process = t_gel − t_vac − t_fill`과 die 힘 평형으로 연결했다.
3. **경쟁 가설:** H1 thermo-rheology, H2 vacuum/vent, H3 surface wetting/holding을 주축으로 소재·필름·측정 원인을 함께 열어 두었다.
4. **판별:** wafer/vector map, raw trace feature, material/chamber block, MSA, DOE와 bootstrap effect를 사용했다.
5. **판단:** H1 Strong, H2 Medium–Strong, H3 Medium. 물리적 가능성과 조작 실험 증거를 분리했다.
6. **개선:** zone uniformity, vacuum-ready 상태, staged closing을 다중 CTQ로 최적화했다.
7. **부작용:** vacuum/pump load, closing/takt, smooth surface/holding, thermal uniformity/cure trade-off를 확인했다.
8. **검증 한계:** synthetic 결과이며 실제 적용 전 crossover/split/confirmation과 reference·requalification이 필요하다.

## 예상 질문과 답변

### 1. 발견한 이상 현상은 무엇인가?

Wafer center가 아닌 outer edge에서 void가 급증했고, chip offset vector도 random이 아니라 radial 또는 특정 장비 방향으로 정렬됐습니다. 두 현상을 별개 불량이 아니라 공통의 비대칭 flow/pressure field 가능성으로 묶은 것이 첫 문제 제기였습니다.

### 2. 처음 어떤 원인을 의심했는가?

가장 먼저 열–유동–경화와 진공 timing의 결합을 의심했습니다. 동시에 vacuum/vent 설비 열화, EMC lot·보관 이력, 표면거칠기와 wetting/holding, release-film tension, 측정 recipe도 경쟁 가설로 유지했습니다.

### 3. 데이터 분석 후 가설이 어떻게 좁혀졌는가?

Edge-distance pattern과 zone/vacuum signature가 함께 나타났고 DOE에서 zone range와 vacuum의 main effect가 재현되어 H1을 Strong으로 올렸습니다. Chamber·PM signature가 있는 H2는 직접 vent split이 없어 Medium–Strong으로, 표면 조건은 반복이 부족해 Medium으로 제한했습니다.

### 4. 기계공학 지식을 어디에 사용했는가?

축대칭 질량보존으로 edge radial velocity가 커지는 이유를 설명하고, pressure와 shear를 적분한 flow force와 die holding force의 자유물체도를 만들었습니다. 열역학·열전달 관점에서는 cure kinetics, 온도 의존 점도, 접촉 열저항을 연결했고 표면공학 관점에서는 Wenzel wetting, capillary pressure, roughness–adhesion trade-off를 검토했습니다.

### 5. 통계와 AI는 어디에 사용했는가?

EDA로 공간·시간·chamber·material pattern을 찾고, DOE/OLS/ANOVA와 bootstrap으로 effect와 불확실성을 평가했습니다. 모델은 원인을 결정하는 도구가 아니라 비선형·interaction 후보를 찾고 process window를 탐색하는 보조 도구로 사용했습니다.

### 6. AI가 없었다면 어떻게 분석했을 것인가?

공정 sequence와 자유물체도에서 fishbone을 만들고, one-factor split과 factorial DOE, ANOVA, chamber/material crossover, short-shot과 leak test로 동일하게 접근했을 것입니다. AI가 없어도 핵심 판단 구조는 physics와 실험 설계입니다.

### 7. AI가 엔지니어 판단을 어떻게 보조했는가?

많은 waveform feature와 interaction을 빠르게 순위화하고, 반복 가능한 분석 pipeline과 시각화를 만드는 데 보조했습니다. 다만 feature importance를 인과로 읽지 않았고, 최종 evidence level은 조작 여부·공간/시간 signature·물리 일관성으로 결정했습니다.

### 8. 공정기인과 설비기인을 어떻게 구분했는가?

동일 material/recipe를 정상·의심 chamber에 교차 투입하는 chamber swap, PM 전후 paired comparison, raw pump-down/leak-up trace를 사용합니다. 결함이 chamber와 actual trace를 따라가면 설비기인, 교정된 장비들에서도 recipe 변수 변화에 따라 재현되면 공정기인을 강화합니다.

### 9. 개선 과정의 side effect는 무엇인가?

더 강한 vacuum은 pump load나 cycle을, 느린 closing은 takt와 gel margin을 악화할 수 있습니다. Smooth surface는 wetting에는 유리해도 die holding shear를 낮출 수 있습니다. 따라서 void만 최소화하지 않고 offset, warpage, cycle time을 동시에 제약했습니다.

### 10. 적용 후 무엇을 monitoring해야 하는가?

CTQ인 Edge Void·Offset·Warpage·Cycle Time과 함께 actual vacuum 도달시간/최저압, heater-zone range, actual position/speed waveform, EMC lot·exposure, surface/film genealogy를 같은 wafer/lot ID로 연결해야 합니다. 아직 양산 전이므로 빈도와 limit 숫자는 실제 capability study 후 정해야 합니다.

### 11. 누구와 무엇을 협업해야 하는가?

- Process engineer: recipe와 short-shot/DOE, 다중 CTQ 승인
- Equipment engineer: vacuum line·vent·seal·pump, heater-zone, platen/film trace
- Material/vendor engineer: DSC/DEA, viscosity/gel time, storage/exposure, lot split
- Quality/metrology engineer: SAM recipe, coordinate registration, MSA, reference artifact
- Product/reliability engineer: warpage·adhesion·reliability side effect와 requalification 범위
- Data engineer: timestamp, wafer ID, PM/material genealogy의 traceability

### 12. 실제 Fab 데이터가 주어지면 무엇을 먼저 요청할 것인가?

동일 wafer와 timestamp로 join 가능한 원시 waveform과 genealogy입니다. 구체적으로 zone별 temperature, vacuum/pressure/position trace, chamber·PM 이력, EMC lot·exposure, die별 mold 전후 좌표와 void map을 요청하겠습니다. 집계 평균만으로는 timing과 공간 방향성을 잃기 때문입니다.

## 꼬리 질문 방어

**“왜 실제 개선이라고 말하지 않나요?”**  
공개 문헌 기반 synthetic dataset에서 재현한 project scenario이기 때문입니다. 제 역량은 수치를 과장하는 것이 아니라 검증 가능한 가설과 다음 실험을 설계한 데 있습니다.

**“A×B interaction이 원인인가요?”**  
평균 interaction은 악화 방향이었지만 bootstrap 95% CI가 0을 포함했습니다. 따라서 물리적으로 유력한 검증 대상이지 안정적으로 확정된 통계 효과라고 말하지 않습니다.

**“표면거칠기를 smooth로 만들면 끝인가요?”**  
아닙니다. wetting은 좋아질 수 있지만 holding shear가 낮아질 수 있습니다. Ra 하나가 아니라 texture, contact angle, shear strength, void와 failure mode를 함께 확인해 surface window를 정해야 합니다.
