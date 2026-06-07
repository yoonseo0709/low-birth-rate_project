# 👶 저출산의 사회구조적 요인 분석

> **소득만이 아닌 교육경쟁 · 주거불안정 · 통근부담이 출산율 하락을 이끈다**

---

## 📌 프로젝트 개요

정부의 저출산 예산이 꾸준히 증가했음에도 합계출산율(TFR)은 역대 최저치를 경신하고 있다.
이 프로젝트는 **사교육비 부담**, **주택가격 상승**, **통근 시간 증가**, **사회신뢰 수준** 등
사회구조적 요인이 출산율 하락에 미치는 영향을 데이터로 분석하고 시각화한다.

---

## 🗄️ DB 구조 (`fertility.db`)

| 테이블 | 컬럼 | 설명 |
|---|---|---|
| `tb_tfr` | sido, year, tfr | 시도별 연도별 합계출산율 |
| `tb_edu` | sido, year, edu_cost_per_student | 학생 1인당 사교육비(만원) |
| `tb_academy` | sido, year, academy_per_1000 | 인구 1,000명당 학원 수 |
| `tb_house` | sido, year, house_price_index | 주택매매가격지수 |
| `tb_commute` | sido, move_2019_week, move_2024_week | 주평균 이동시간(분) |
| `tb_intl` | country, trust_year, trust_pct, tfr | OECD 사회신뢰도 × 출산율 |
| `tb_budget` | year, budget_trillion, is_confirmed | 정부 저출산 예산(조원) |

---

## 📊 앱 구성

| 파트 | 제목 | 주요 차트 |
|---|---|---|
| 01 | 정책 예산의 역설 | 이중축 막대+꺾은선 차트 |
| 02 | 교육경쟁 압박 | 산점도(OLS 추세선) + 시계열 |
| 03 | 주거 불안정 | 시도별 상관계수 수평 막대 + 이중축 시계열 |
| 04 | 통근 부담 | 산점도 + 상위/하위 3개 시도 |
| 05 | 사회 신뢰 국제 비교 | OECD 산점도 |
| 06 | 종합 | 요약 카드 + 레이더 차트 |

---

## 🚀 로컬 실행 방법

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 앱 실행 (fertility.db와 같은 디렉터리에서)
streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

---

## ☁️ Streamlit Cloud 배포 방법

1. GitHub 저장소에 `app.py`, `requirements.txt`, `fertility.db`, `README.md` 업로드
2. [https://streamlit.io/cloud](https://streamlit.io/cloud) 접속 후 GitHub 계정 연동
3. **New app** → 저장소·브랜치·`app.py` 선택 → **Deploy**
4. 배포 완료 후 공개 URL 자동 생성

> ⚠️ `fertility.db` 파일이 저장소에 포함되어야 합니다.

---

## 🛠️ 기술 스택

- **Streamlit** — 웹 앱 프레임워크
- **Plotly** — 인터랙티브 차트 (Express + Graph Objects)
- **Pandas** — 데이터 처리 및 SQL 쿼리
- **SciPy** — 피어슨 상관계수 계산
- **SQLite** — 경량 DB (fertility.db)

---

## 📁 파일 목록

```
📦 project/
├── app.py            # Streamlit 앱 메인 파일
├── fertility.db      # SQLite 데이터베이스
├── requirements.txt  # Python 의존성
└── README.md         # 프로젝트 문서
```

---

## 📎 데이터 출처

- 통계청 인구동향조사 · 사교육비조사 · 생활시간조사
- 한국부동산원 주택매매가격지수
- OECD Family Database
- Integrated Values Survey / UN World Population Prospects
