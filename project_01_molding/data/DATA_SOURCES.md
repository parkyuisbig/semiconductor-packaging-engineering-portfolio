# Data Sources and Provenance

## Project data

현재 `raw/`와 `processed/`의 molding 데이터는 모두 seeded synthetic engineering data다.

> 본 데이터는 공개 문헌과 공정 메커니즘을 참고하여 프로젝트 검증 목적으로 생성한 synthetic engineering dataset이다.

- 실제 SK하이닉스/Fab 데이터: 사용하지 않음
- 실제 생산 recipe/spec: 사용하지 않음
- Generator seed: `20260818`
- Physics structure: thermal/cure/vacuum margin, equipment drift, EMC genealogy, surface/holding trade-off
- Scenario coefficients: 프로젝트용이며 material constant가 아님

## External public resources — not merged into project data

### WM-811K

- Kaggle mirror: https://www.kaggle.com/datasets/qingyi/wm811k-wafer-map
- GitHub dataset description: https://github.com/kweyuchesa/industrial-datasets/blob/master/markdown/wm811k_wafer_maps.md
- Intended use here: spatial wafer-map taxonomy and visualization benchmark only
- Not used for: compression-molding parameter estimation or physical root-cause inference

### UCI SECOM

- Kaggle mirror: https://www.kaggle.com/datasets/paresh2047/uci-semcom
- UCI raw-file documentation example: https://github.com/Be1an001/semiconductor-pass-fail-prediction-python/blob/main/data/README.md
- Intended use here: sensor-table, missing-value, timestamp and rare-fail pipeline reference only
- Limitation: process features are anonymous and cannot be mapped to vacuum, temperature or EMC properties

## Key physical references

- Die shift / flow drag: https://doi.org/10.3390/mi7060095
- Radial compression-flow mechanics: https://doi.org/10.1109/TCPMT.2013.2268192
- EMC cure kinetics: https://doi.org/10.3390/polym13111734
- Vacuum / air pocket: https://doi.org/10.1016/j.microrel.2014.12.001
- Roughness / wetting: https://doi.org/10.1021/j150474a015
- Thermal contact conductance: https://doi.org/10.1016/0017-9310(69)90011-8

