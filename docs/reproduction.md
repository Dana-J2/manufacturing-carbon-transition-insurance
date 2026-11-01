# 파일 구성과 재현 안내

## 읽는 순서

1. [최종 발표](../presentation/final_presentation.pdf)로 문제·결과를 확인합니다.
2. [통합 모형](../models/insurance_model.xlsx)의 `2. 기초데이터 입력` → `모델 가정` → `3. 분석 및 모델링` → `5-1. 회사별, 연도별` → `5. 통합` 순서로 계산을 추적합니다.
3. `PRF_데이터`, `g_decarb_데이터`의 입력 경로는 아래 노트북과 연결됩니다.
4. [검증 문서](validation.md)에서 버전 차이와 장기 계산식 전환을 확인합니다.

## 파일과 의존성

| 저장 경로 | 원래 역할 | 사용 관계 |
|---|---|---|
| `models/insurance_model.xlsx` | 학술제시트_520_아마최종.xlsx, 내부 521 변경 기록 | 보관용 통합 모형 |
| `data/inputs/model_0517.xlsx` | 학술제시트_517.xlsx | S-curve 노트북 입력 |
| `data/inputs/physical_risk_source.xlsx` | 물리적리스크_기초자료.xlsx | 사업장 기초자료 |
| `data/inputs/physical_risk_factors.xlsx` | 물리적리스크_할인할증.xlsx | 기본 PRF 매핑 자료 |
| `data/inputs/physical_risk_growth.xlsx` | 물리적리스크_PRF_세부증가율_매핑.xlsx | PRF 연도별 노트북 입력 |
| `data/processed/physical_risk_annual.xlsx` | 물리적리스크_PRF_연도별_매핑.xlsx | 저장된 PRF 0–40년 결과 |
| `data/processed/decarbonization_curves.xlsx` | g_decarb_S_curve_결과.xlsx | 당시 저장된 감축 결과 |
| `data/inputs/v2_backtest_data.csv` | 동일 원래 이름 | 사건연구의 가격 데이터 |
| `notebooks/01_physical_risk.ipynb` | 최종 파일 모음 PRF 코드 | 사업장·기업별 연도 경로 생성 |
| `notebooks/02_decarbonization.ipynb` | 최종 파일 모음 S-curve 코드 | 탄소감축 경로·시각화 |
| `notebooks/03_event_study.ipynb` | V2_백테스트_최종_(1).ipynb | 직교화 시장모형·CAR 분석 |

원본 파일의 내용과 저장된 출력은 유지했습니다. 보기 쉬운 저장 경로로 이름을 바꿨으므로, **원본 노트북을 그대로 Run All 하면 입력 경로 때문에 실패할 수 있습니다.** 아래의 경로를 실행용 복사본에서 바꾸세요. 원본 해시를 보존하려면 `reproduced/` 폴더에서 작업하세요.

## 환경 준비

Python 3 환경에서 저장소 루트 기준:

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/verify_archive.py
jupyter notebook
```

`requirements.txt`는 코드의 import를 기준으로 작성한 의존성 목록입니다. 원래 팀 환경의 버전 잠금 파일이 없어 정확한 역사적 버전을 보장하지 않습니다. 패키지·시세 데이터 버전에 따라 결과가 달라질 수 있습니다.

## 1. 물리적 위험

실행용 노트북 복사본에서 첫 셀의 경로를 바꿉니다. Jupyter 작업 디렉터리가 저장소 루트인 경우:

```python
from pathlib import Path
input_path = Path('data/inputs/physical_risk_growth.xlsx')
output_path = Path('reproduced/physical_risk_annual.xlsx')
output_path.parent.mkdir(parents=True, exist_ok=True)
```

원본은 작성자 컴퓨터의 Downloads 절대경로를 사용합니다. `사업장별 PRF`를 읽고 연도별 PRF, 면적가중 기업 PRF, YoY·CAGR, wide/long 테이블을 계산합니다. 출력과 비교할 파일은 `data/processed/physical_risk_annual.xlsx`입니다.

## 2. 탄소감축

원본의 `pd.read_excel('학술제시트_517.xlsx', ...)`를 실행용 복사본에서 아래로 변경합니다.

```python
df = pd.read_excel('data/inputs/model_0517.xlsx', sheet_name='3. 분석 및 모델링')
```

노트북은 0–30년의 `rho_df`, `g_df`, `A_df`와 그래프를 계산합니다. 한글 폰트 `AppleGothic`은 macOS 의존성이 있으므로 다른 운영체제에서는 설치된 폰트로 변경합니다. 원본 코드와 당시 저장 엑셀을 별도로 보관했으며, 동일 이름의 첨부들 사이에 버전 차이가 있어 출력 파일이 해당 코드에서 자동으로 완전히 재생성된다고 보장하지 않습니다.

## 3. 사건연구

원본은 Google Colab의 `files.upload()`를 사용합니다. Colab에서는 `v2_backtest_data.csv`를 업로드하고 실행합니다. 로컬 Jupyter에서는 설치용 `!pip`, Ubuntu 전용 `!apt-get`, `google.colab` 업로드 셀을 실행용 복사본에서 환경에 맞게 대체합니다.

```python
df = pd.read_csv('data/inputs/v2_backtest_data.csv', parse_dates=['Date'])
df = df.set_index('Date').sort_index()
```

코드는 `yfinance`로 `EXH5.DE`, `1617.T`, `IAG.AX`, `SUN.AX`, `MPL.AX` 등의 보험업 대리지수를 추가로 가져옵니다. 따라서 첨부 CSV만으로 전체 사건연구가 오프라인 재현되지는 않습니다. 네트워크·공급자 접근성과 과거 가격 수정에 영향을 받습니다. 원본은 일부 다운로드 실패를 잡지만 이후 `EU_INS`·`JP_INS`를 직접 참조하므로 다운로드 누락 시 중단될 수 있습니다.

## 결과 파일의 의미

- `company_model_cached.csv`: 통합 엑셀의 `3. 분석 및 모델링` 저장값, 합계 행 포함.
- `simulation_cached.csv`: `5. 통합`의 t=0–35 저장값.
- `archive_check.json`: 원본 무결성·47개 기업 t=0 수식 독립 계산·저장 오류값 점검 결과.

CSV와 검증 결과는 이번 정리 과정에서 만든 보조 산출물입니다. 학술제 당시 사용했던 원본 코드나 새로운 전체 모델 실행 결과로 오해하지 않아야 합니다. Excel 원본은 변경하지 않았습니다.
