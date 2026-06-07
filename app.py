
import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="저출산의 사회구조적 요인 분석",
    page_icon="👶",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# 디자인 상수
# ─────────────────────────────────────────────
COLOR_MAIN   = "#e94560"
COLOR_SECOND = "#5b8dee"
COLOR_ACCENT = "#8b7cf8"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="#ffffff",
    plot_bgcolor="#ffffff",
    font=dict(color="#2b2b2b", family="Noto Sans KR"),
    margin=dict(t=40, b=40, l=10, r=10),
)

AXIS_STYLE = dict(
    gridcolor="#ede9e3",
    zerolinecolor="#ede9e3",
    tickfont=dict(color="#888078"),
    showgrid=True,
)

# ─────────────────────────────────────────────
# 커스텀 CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* 전체 배경 */
.stApp {
    background-color: #f0ede8;
}

/* HERO */
.hero {
    background: linear-gradient(135deg, #fef9f0 0%, #f0ede8 50%, #ede8f5 100%);
    padding: 3.5rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    text-align: center;
    border: 1px solid #e8e3dc;
}
.hero h1 {
    font-size: 2.4rem;
    font-weight: 700;
    color: #2b2b2b;
    margin: 0 0 .8rem 0;
}
.hero p {
    font-size: 1.1rem;
    color: #888078;
    margin: 0;
}

/* SECTION HEADER */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 1.2rem 1.5rem;
    background: linear-gradient(135deg, #ffffff, #f7f5f2);
    border-left: 5px solid #e94560;
    border-radius: 8px;
    margin: 2rem 0 1rem;
}
.section-header .num {
    font-size: 2rem;
    font-weight: 700;
    color: #e94560;
    min-width: 48px;
}
.section-header .title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #2b2b2b;
}
.section-header .sub {
    font-size: .85rem;
    color: #888078;
    margin-top: 3px;
}

/* STAT CARD */
.stat-card {
    background: #ffffff;
    border: 1px solid #e8e3dc;
    border-radius: 12px;
    padding: 1.4rem 1.2rem;
    text-align: center;
    height: 100%;
}
.stat-card .val {
    font-size: 2rem;
    font-weight: 700;
    color: #e94560;
}
.stat-card .lbl {
    font-size: .85rem;
    color: #888078;
    margin-top: 4px;
}

/* INSIGHT BOX */
.insight-box {
    background: linear-gradient(135deg, #ffffff, #f7f5f2);
    border: 1px solid #e8e3dc;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-top: .8rem;
}
.insight-box p {
    color: #2b2b2b;
    font-size: .93rem;
    line-height: 1.65;
    margin: 0;
}
.insight-box strong {
    color: #e94560;
}

/* SUMMARY CARD */
.summary-card {
    background: #ffffff;
    border: 1px solid #e8e3dc;
    border-radius: 14px;
    padding: 1.8rem 1.5rem;
    height: 100%;
}
.summary-card .icon {
    font-size: 2.5rem;
}
.summary-card .ctitle {
    font-size: 1.1rem;
    font-weight: 700;
    color: #2b2b2b;
    margin-top: .5rem;
}
.summary-card .corr {
    font-size: 1.5rem;
    font-weight: 700;
    color: #e94560;
    margin: .3rem 0;
}
.summary-card .desc {
    font-size: .85rem;
    color: #888078;
    line-height: 1.6;
}

/* FOOTER */
.footer {
    text-align: center;
    color: #888078;
    font-size: .8rem;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #e8e3dc;
}

/* Streamlit 기본 스타일 오버라이드 */
.stTabs [data-baseweb="tab-list"] {
    background-color: #f7f5f2;
    border-radius: 8px;
    padding: 4px;
    margin-top: 0.6rem;
    margin-bottom: 0.6rem;
}
.stTabs [data-baseweb="tab"] {
    color: #888078;
    padding: 0.3rem 1rem;
}
.stTabs [aria-selected="true"] {
    background-color: #e94560 !important;
    color: #fff !important;
    border-radius: 6px;
}
div[data-testid="stSlider"] label {
    color: #2b2b2b;
}
div[data-testid="stRadio"] label,
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] div[role="radiogroup"] label {
    color: #2b2b2b !important;
}
div[data-testid="stMultiSelect"] label {
    color: #2b2b2b;
}

/* 데이터프레임 */
.stDataFrame {
    background-color: #ffffff;
    border: 1px solid #e8e3dc;
    border-radius: 8px;
}
[data-testid="stDataFrameResizable"] {
    background-color: #ffffff;
}

/* SQL 코드 블록 */
.stCode, .stCodeBlock {
    background-color: #f7f5f2 !important;
    border: 1px solid #e8e3dc !important;
    border-radius: 8px !important;
}
pre {
    background-color: #f7f5f2 !important;
}
pre code,
pre code span,
pre .token,
pre .token.comment,
pre .token.keyword,
pre .token.string,
pre .token.number,
pre .token.operator,
pre .token.punctuation,
[data-testid="stCode"] code,
[data-testid="stCode"] code span,
[data-testid="stCode"] pre {
    color: #2b2b2b !important;
    background-color: #f7f5f2 !important;
}

/* Expander */
[data-testid="stExpander"] {
    border: 1px solid #e8e3dc !important;
    border-radius: 8px !important;
    background-color: #ffffff !important;
}
[data-testid="stExpander"] summary {
    color: #2b2b2b !important;
}

/* 커스텀 HTML 테이블 */
table.styled-table {
    width: 100%;
    border-collapse: collapse;
    background-color: #ffffff;
    border: 1px solid #e8e3dc;
    border-radius: 8px;
    font-size: .88rem;
    margin-top: .4rem;
    overflow: hidden;
}
table.styled-table th {
    background-color: #f7f5f2;
    color: #888078;
    font-weight: 600;
    padding: .55rem .9rem;
    border-bottom: 1px solid #e8e3dc;
    text-align: left;
}
table.styled-table td {
    padding: .5rem .9rem;
    border-bottom: 1px solid #f0ede8;
    color: #2b2b2b;
}
table.styled-table tr:last-child td {
    border-bottom: none;
}
table.styled-table tbody tr:hover td {
    background-color: #f7f5f2;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DB 연결 & 데이터 로드
# ─────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return sqlite3.connect("fertility.db", check_same_thread=False)

# 2015~2024 전국 합계출산율은 DB에 시도별 데이터만 존재 → 공식 전국 수치 보완
# 출처: 통계청 인구동향조사 (KOSIS)
_NATIONAL_TFR_SUPPLEMENT = {
    2015: 1.239, 2016: 1.172, 2017: 1.052, 2018: 0.977,
    2019: 0.918, 2020: 0.837, 2021: 0.808, 2022: 0.778,
    2023: 0.721, 2024: 0.748,
}

@st.cache_data
def load_national_tfr():
    """전국 합계출산율 시계열 반환 (DB 전국값 + 2015~2024 KOSIS 보완)"""
    conn = get_conn()
    # DB에서 sido='전국' 행 (2000~2014, 2025)
    df_db = pd.read_sql(
        "SELECT year, tfr FROM tb_tfr WHERE sido='전국' ORDER BY year", conn
    )
    # 보완 데이터 (2015~2024)
    df_sup = pd.DataFrame(
        list(_NATIONAL_TFR_SUPPLEMENT.items()), columns=["year", "tfr"]
    )
    df = pd.concat([df_db, df_sup]).drop_duplicates("year").sort_values("year").reset_index(drop=True)
    return df

@st.cache_data
def load_budget():
    conn = get_conn()
    df_b = pd.read_sql("SELECT year, budget_trillion FROM tb_budget ORDER BY year", conn)
    df_tfr = load_national_tfr()
    return df_b.merge(df_tfr, on="year", how="left")

@st.cache_data
def load_edu():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT e.sido, e.year, e.edu_cost_per_student, a.academy_per_1000, t.tfr
        FROM tb_edu e
        JOIN tb_tfr t ON e.sido = t.sido AND e.year = t.year
        JOIN tb_academy a ON e.sido = a.sido AND e.year = a.year
    """, conn)
    return df

@st.cache_data
def load_house():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT h.sido, h.year, h.house_price_index, t.tfr
        FROM tb_house h
        JOIN tb_tfr t ON h.sido = t.sido AND h.year = t.year
    """, conn)
    return df

@st.cache_data
def load_commute():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT c.sido, c.move_2019_week, c.move_2024_week, t.tfr
        FROM tb_commute c
        JOIN tb_tfr t ON c.sido = t.sido AND t.year = 2024
    """, conn)
    return df

@st.cache_data
def load_intl():
    conn = get_conn()
    return pd.read_sql("SELECT * FROM tb_intl", conn)

# ─────────────────────────────────────────────
# HERO 배너
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>👶 저출산의 사회구조적 요인 분석</h1>
  <p>소득만이 아닌 교육경쟁 · 주거불안정 · 통근부담이 출산율 하락을 이끈다</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# PART 01 — 정책 예산의 역설
# ═══════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <div class="num">01</div>
  <div>
    <div class="title">정책 예산의 역설</div>
    <div class="sub">정부 저출산 예산 vs 합계출산율 추이 (예산 2006–2023 / TFR 2006–2025)</div>
  </div>
</div>
""", unsafe_allow_html=True)

df_budget = load_budget()

# 전국 TFR — 2006~2025 구간 필터 (예산 시작 연도부터 최신까지)
df_tfr_all = load_national_tfr()
df_tfr_all = df_tfr_all[df_tfr_all["year"] >= 2006].reset_index(drop=True)

fig1 = make_subplots(specs=[[{"secondary_y": True}]])

# ① 예산 막대 — 단일 색상
fig1.add_trace(
    go.Bar(
        x=df_budget["year"],
        y=df_budget["budget_trillion"],
        name="저출산 예산 (조원)",
        marker_color=COLOR_SECOND,
        opacity=0.85,
        hovertemplate="%{y:.1f}조원<extra></extra>",
    ),
    secondary_y=False,
)

# ② TFR 꺾은선 — 2006~2025
fig1.add_trace(
    go.Scatter(
        x=df_tfr_all["year"],
        y=df_tfr_all["tfr"],
        name="합계출산율 (TFR)",
        line=dict(color=COLOR_MAIN, width=3),
        marker=dict(size=7, color=COLOR_MAIN),
        mode="lines+markers",
        hovertemplate="TFR: %{y:.3f}<extra></extra>",
    ),
    secondary_y=True,
)

# ③ 인구유지 대체 출산율 기준선 (TFR = 2.1)
fig1.add_hline(
    y=2.1,
    secondary_y=True,
    line=dict(color="#d97706", width=1.5, dash="dot"),
)

fig1.update_layout(
    **PLOTLY_LAYOUT,
    hovermode="x unified",
    legend=dict(
        orientation="h", y=1.08, x=0.5, xanchor="center",
        font=dict(color="#2b2b2b"),
        bgcolor="#ffffff",
        bordercolor="#e8e3dc",
        borderwidth=1,
    ),
    height=440,
)
fig1.update_xaxes(**AXIS_STYLE, title_text="연도", title_font=dict(color="#888078"),
                  range=[2005.5, 2025.5], dtick=1)
fig1.update_yaxes(**AXIS_STYLE, title_text="예산 (조원)", title_font=dict(color="#888078"), secondary_y=False)
fig1.update_yaxes(**AXIS_STYLE, title_text="합계출산율 (TFR)", title_font=dict(color=COLOR_MAIN),
                  range=[0, 1.5], secondary_y=True)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
<div class="insight-box">
  <p>저출산 예산이 약 25배 급증하는 동안 합계출산율은 2023년 <strong>0.721명</strong>으로 역대 최저까지 떨어졌다.<br>
  2024년부터 소폭 반등했으나 <strong>대체 출산율(2.1명)</strong>과의 격차는 여전히 크다.<br>
  재정 투입만으로는 출산율을 되돌리지 못한다는 사실은,
  <strong>사회구조적 근인에 주목해야 함을 명확히 보여준다.</strong></p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# PART 02 — 교육경쟁 압박
# ═══════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <div class="num">02</div>
  <div>
    <div class="title">교육경쟁 압박</div>
    <div class="sub">사교육비 × 합계출산율 (시도별, 2015–2023)</div>
  </div>
</div>
""", unsafe_allow_html=True)

df_edu = load_edu()

tab_edu1, tab_edu2 = st.tabs(["📊 산점도 & 추세선", "📈 시도별 시계열"])

with tab_edu1:
    year_range = st.slider(
        "연도 범위", 2015, 2023, (2015, 2023), key="edu_year"
    )
    df_edu_f = df_edu[(df_edu["year"] >= year_range[0]) & (df_edu["year"] <= year_range[1])]

    # 상관계수 계산
    r_edu, p_edu = stats.pearsonr(df_edu_f["edu_cost_per_student"], df_edu_f["tfr"])

    # stat cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div class="stat-card">
          <div class="val">r = {r_edu:.3f}</div>
          <div class="lbl">전체 패널 상관계수</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="stat-card">
          <div class="val">β = -0.027***</div>
          <div class="lbl">고정효과 패널 계수</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="stat-card">
          <div class="val">p &lt; .001</div>
          <div class="lbl">유의확률</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:1rem'></div>", unsafe_allow_html=True)

    fig2 = px.scatter(
        df_edu_f, x="edu_cost_per_student", y="tfr",
        color="sido",
        trendline="ols",
        trendline_scope="overall",
        trendline_color_override=COLOR_MAIN,
        color_discrete_sequence=px.colors.qualitative.G10,
        labels={
            "edu_cost_per_student": "학생 1인당 사교육비 (만원)",
            "tfr": "합계출산율",
            "sido": "시도",
        },
        height=480,
    )
    fig2.update_layout(
        **PLOTLY_LAYOUT,
        legend=dict(font=dict(color="#2b2b2b"), bgcolor="#ffffff", bordercolor="#e8e3dc", borderwidth=1),
    )
    fig2.update_xaxes(**AXIS_STYLE, title_font=dict(color="#888078"))
    fig2.update_yaxes(**AXIS_STYLE, title_font=dict(color="#888078"))
    st.plotly_chart(fig2, use_container_width=True)

with tab_edu2:
    sido_list = sorted(df_edu["sido"].unique().tolist())
    default_edu = ["서울특별시", "경기도", "전라남도", "제주특별자치도"]
    sel_edu = st.multiselect(
        "시도 선택", sido_list, default=default_edu, key="edu_sido"
    )
    if sel_edu:
        df_edu_ts = df_edu[df_edu["sido"].isin(sel_edu)]
        fig2b = px.line(
            df_edu_ts, x="year", y="edu_cost_per_student",
            color="sido", markers=True,
            color_discrete_sequence=px.colors.qualitative.G10,
            labels={
                "year": "연도",
                "edu_cost_per_student": "학생 1인당 사교육비 (만원)",
                "sido": "시도",
            },
            height=420,
        )
        fig2b.update_layout(
            **PLOTLY_LAYOUT,
            legend=dict(font=dict(color="#2b2b2b"), bgcolor="#ffffff", bordercolor="#e8e3dc", borderwidth=1),
        )
        fig2b.update_xaxes(**AXIS_STYLE, title_font=dict(color="#888078"))
        fig2b.update_yaxes(**AXIS_STYLE, title_font=dict(color="#888078"))
        st.plotly_chart(fig2b, use_container_width=True)
    else:
        st.info("시도를 한 개 이상 선택해주세요.")

st.markdown("""
<div class="insight-box">
  <p>학생 1인당 사교육비와 합계출산율은 전체 패널 기준 <strong>r = −0.714</strong>의 유의미한 음의 상관을 보인다 (p &lt; .001).
  <br>연도 평균으로 분석하면 r = −0.915에 달하며, 고정효과 패널 모형에서도 사교육비
  <strong>1만원 증가 시 출산율 0.027 하락</strong>이 확인된다.
  '한 아이에게 집중 투자'하는 교육 문화가 추가 출산을 억제하는 구조적 요인으로 작용한다.</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# PART 03 — 주거 불안정
# ═══════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <div class="num">03</div>
  <div>
    <div class="title">주거 불안정</div>
    <div class="sub">주택매매가격지수 × 합계출산율 (시도별, 2015–2023)</div>
  </div>
</div>
""", unsafe_allow_html=True)

df_house = load_house()

tab_h1, tab_h2, tab_h3 = st.tabs(["🗺️ 전국 산점도", "📊 수도권 이중축", "📉 시도별 상관계수"])

with tab_h1:
    fig3a = px.scatter(
        df_house, x="house_price_index", y="tfr",
        color="sido",
        trendline="ols",
        trendline_scope="overall",
        trendline_color_override=COLOR_MAIN,
        color_discrete_sequence=px.colors.qualitative.G10,
        labels={"house_price_index": "주택매매가격지수", "tfr": "합계출산율", "sido": "시도"},
        height=520,
    )
    fig3a.update_layout(
        **PLOTLY_LAYOUT,
        legend=dict(font=dict(color="#2b2b2b"), bgcolor="#ffffff", bordercolor="#e8e3dc", borderwidth=1),
    )
    fig3a.update_xaxes(**AXIS_STYLE, title_font=dict(color="#888078"))
    fig3a.update_yaxes(**AXIS_STYLE, title_font=dict(color="#888078"))
    st.plotly_chart(fig3a, use_container_width=True)
    st.markdown("""
<div class="insight-box">
  <p>전국 시도 패널 데이터에서 주택매매가격지수가 높을수록 합계출산율이 낮아지는 뚜렷한 음의 상관이 나타난다.
  <strong>추세선의 기울기</strong>는 집값 상승이 출산 의향을 전반적으로 억제함을 시사하며,
  특히 가격지수가 높은 수도권 시도에서 출산율이 집중적으로 낮게 분포한다.</p>
</div>
""", unsafe_allow_html=True)

with tab_h2:
    metro = ["서울특별시", "경기도", "인천광역시"]
    df_metro_avg = (
        df_house[df_house["sido"].isin(metro)]
        .groupby("year")[["house_price_index", "tfr"]]
        .mean()
        .reset_index()
    )

    fig3b = make_subplots(specs=[[{"secondary_y": True}]])
    fig3b.add_trace(
        go.Bar(
            x=df_metro_avg["year"], y=df_metro_avg["house_price_index"],
            name="주택매매가격지수 (수도권 평균)",
            marker_color=COLOR_SECOND, opacity=0.7,
            hovertemplate="지수: %{y:.1f}<extra></extra>",
        ),
        secondary_y=False,
    )
    fig3b.add_trace(
        go.Scatter(
            x=df_metro_avg["year"], y=df_metro_avg["tfr"],
            name="합계출산율 (수도권 평균)",
            line=dict(color=COLOR_MAIN, width=3),
            marker=dict(size=8, color=COLOR_MAIN),
            mode="lines+markers",
            hovertemplate="TFR: %{y:.3f}<extra></extra>",
        ),
        secondary_y=True,
    )
    fig3b.update_layout(
        **PLOTLY_LAYOUT,
        hovermode="x unified",
        legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center",
                    font=dict(color="#2b2b2b"), bgcolor="#ffffff",
                    bordercolor="#e8e3dc", borderwidth=1),
        height=520,
    )
    fig3b.update_xaxes(**AXIS_STYLE, title_text="연도", title_font=dict(color="#888078"))
    fig3b.update_yaxes(**AXIS_STYLE, title_text="주택매매가격지수", title_font=dict(color="#888078"), secondary_y=False)
    fig3b.update_yaxes(**AXIS_STYLE, title_text="합계출산율 (TFR)", title_font=dict(color=COLOR_MAIN), secondary_y=True)
    st.plotly_chart(fig3b, use_container_width=True)
    st.markdown("""
<div class="insight-box">
  <p>수도권(서울·경기·인천) 평균을 보면, 주택매매가격지수가 꾸준히 상승하는 동안
  합계출산율은 <strong>반대 방향으로 지속 하락</strong>해 두 지표가 뚜렷하게 역행한다.
  주거비 부담이 가장 높은 지역에서 출산율 하락도 가장 가파른 패턴은
  '내 집 마련 전 출산 유보' 심리를 뒷받침한다.</p>
</div>
""", unsafe_allow_html=True)

with tab_h3:
    corr_list_h = []
    for sido, grp in df_house.groupby("sido"):
        if len(grp) >= 4:
            r_h, p_h = stats.pearsonr(grp["house_price_index"], grp["tfr"])
            corr_list_h.append({"sido": sido, "r": r_h})
    df_corr = pd.DataFrame(corr_list_h).sort_values("r")

    bar_colors = [
        COLOR_MAIN if r < -0.7 else COLOR_SECOND if r < 0 else "#d4d4d4"
        for r in df_corr["r"]
    ]

    fig3c = go.Figure(go.Bar(
        x=df_corr["r"],
        y=df_corr["sido"],
        orientation="h",
        marker_color=bar_colors,
        text=[f"r = {r:.3f}" for r in df_corr["r"]],
        textposition="outside",
        hovertemplate="%{y}: r = %{x:.3f}<extra></extra>",
    ))
    fig3c.update_layout(
        **PLOTLY_LAYOUT,
        height=520,
        xaxis=dict(**AXIS_STYLE, range=[-1.1, 0.3], title="피어슨 상관계수 r", title_font=dict(color="#888078")),
        yaxis=dict(**AXIS_STYLE, title="", autorange="reversed"),
    )
    st.plotly_chart(fig3c, use_container_width=True)
    st.markdown(
        "<div style='text-align:center;color:#888078;font-size:.85rem;margin-top:-.5rem'>"
        "🔴 r &lt; -0.7: 강한 음의 상관 &nbsp;/&nbsp; 🔵 r &lt; 0: 음의 상관</div>",
        unsafe_allow_html=True,
    )
    st.markdown("""
<div class="insight-box">
  <p>대부분의 시도에서 주택매매가격지수와 합계출산율은 <strong>음의 상관</strong>을 보이며,
  서울·경기 등 수도권에서는 상관계수가 최대 <strong>r = −0.967</strong>에 달한다.
  집값 상승이 출산율 하락과 거의 완벽하게 동조화된 구조로,
  <strong>경제적 불안감이 출산 결정을 지연·포기</strong>시키는 핵심 요인임을 보여준다.</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# PART 04 — 통근 부담
# ═══════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <div class="num">04</div>
  <div>
    <div class="title">통근 부담</div>
    <div class="sub">평균 이동시간 × 합계출산율 (시도별, 2024년)</div>
  </div>
</div>
""", unsafe_allow_html=True)

df_commute = load_commute()

col_sel = "move_2024_week"
metro_sido = ["서울특별시", "경기도", "인천광역시"]
df_commute["region"] = df_commute["sido"].apply(
    lambda x: "수도권" if x in metro_sido else "기타"
)

df_commute_no_sj = df_commute[~df_commute["sido"].str.contains("세종")]
r_com, p_com = stats.pearsonr(df_commute_no_sj[col_sel], df_commute_no_sj["tfr"])

col_left, col_right = st.columns([2, 1])

with col_left:
    fig4 = px.scatter(
        df_commute,
        x=col_sel, y="tfr",
        color="region",
        text="sido",
        trendline="ols",
        trendline_scope="overall",
        trendline_color_override=COLOR_MAIN,
        color_discrete_map={"수도권": COLOR_MAIN, "기타": COLOR_ACCENT},
        labels={
            col_sel: "주평균 이동시간 (2024년, 분)",
            "tfr": "합계출산율",
            "region": "지역",
        },
        height=460,
    )
    fig4.update_traces(
        marker=dict(size=11, opacity=0.85),
        textposition="top center",
        selector=dict(mode="markers+text"),
    )
    fig4.update_layout(
        **PLOTLY_LAYOUT,
        legend=dict(
            font=dict(color="#2b2b2b"), bgcolor="#ffffff",
            bordercolor="#e8e3dc", borderwidth=1,
            orientation="h", y=1.06, x=0.5, xanchor="center",
        ),
    )
    fig4.update_xaxes(**AXIS_STYLE, title_font=dict(color="#888078"))
    fig4.update_yaxes(**AXIS_STYLE, title_font=dict(color="#888078"))
    st.plotly_chart(fig4, use_container_width=True)

with col_right:
    p_str = "< .01" if p_com < 0.01 else "< .05" if p_com < 0.05 else f"= {p_com:.3f}"
    st.markdown(f"""
    <div style='margin-top:1rem'>
    <div class="stat-card">
      <div class="val">r = {r_com:.3f}</div>
      <div class="lbl">이동시간-출산율 상관계수</div>
    </div>
    </div>
    <div style='margin-top:1rem'>
    <div class="stat-card">
      <div class="val">p {p_str}</div>
      <div class="lbl">p-value</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

col_top, col_bot = st.columns(2)

with col_top:
    st.markdown("<div style='margin-top:.8rem;color:#2b2b2b;font-weight:600'>이동시간 상위 3개 시도</div>", unsafe_allow_html=True)
    top3 = df_commute.nlargest(3, col_sel)[["sido", col_sel, "tfr"]].rename(
        columns={"sido": "시도", col_sel: "이동시간(분)", "tfr": "TFR"}
    )
    st.markdown(top3.to_html(index=False, classes="styled-table"), unsafe_allow_html=True)

with col_bot:
    st.markdown("<div style='margin-top:.8rem;color:#2b2b2b;font-weight:600'>이동시간 하위 3개 시도</div>", unsafe_allow_html=True)
    bot3 = df_commute.nsmallest(3, col_sel)[["sido", col_sel, "tfr"]].rename(
        columns={"sido": "시도", col_sel: "이동시간(분)", "tfr": "TFR"}
    )
    st.markdown(bot3.to_html(index=False, classes="styled-table"), unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
  <p>주평균 이동시간이 길수록 합계출산율이 낮아지는 경향이 확인된다 (r ≈ −0.56, p &lt; .05).
  <br>서울·인천·경기도 등 수도권 장거리 통근 지역은 육아·가사에 투입할 수 있는 시간 자원이 절대적으로 부족해진다.
  <br><strong>시간 빈곤</strong>이 출산을 억제하는 비금전적 요인으로 작용함을 시사한다.</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# PART 05 — 사회 신뢰 국제 비교
# ═══════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <div class="num">05</div>
  <div>
    <div class="title">사회 신뢰와 출산율 (국제 비교)</div>
    <div class="sub">OECD 국가 사회신뢰도 × 합계출산율</div>
  </div>
</div>
""", unsafe_allow_html=True)

df_intl = load_intl()
df_intl["group"] = df_intl["country"].apply(
    lambda c: "🇰🇷 한국" if "Korea" in c else "기타 OECD"
)
r_intl, p_intl = stats.pearsonr(df_intl["trust_pct"], df_intl["tfr"])

x_min = max(df_intl["trust_pct"].min() - 5, 0)
x_max = df_intl["trust_pct"].max() + 5
y_min = max(df_intl["tfr"].min() - 0.1, 0)
y_max = df_intl["tfr"].max() + 0.1

fig5 = px.scatter(
    df_intl,
    x="trust_pct", y="tfr",
    color="group",
    text="country",
    trendline="ols",
    trendline_scope="overall",
    trendline_color_override="#d97706",
    color_discrete_map={"🇰🇷 한국": COLOR_MAIN, "기타 OECD": COLOR_SECOND},
    labels={
        "trust_pct": "사회신뢰도 (%)",
        "tfr": "합계출산율 (TFR)",
        "group": "구분",
    },
    height=480,
)
fig5.update_traces(
    marker=dict(size=10, opacity=0.8),
    textposition="top center",
    selector=dict(mode="markers+text"),
)

fig5.update_layout(**PLOTLY_LAYOUT)
fig5.update_xaxes(**AXIS_STYLE, title_font=dict(color="#888078"), range=[x_min, x_max])
fig5.update_yaxes(**AXIS_STYLE, title_font=dict(color="#888078"), range=[y_min, y_max])

col5_left, col5_right = st.columns([2, 1])

with col5_left:
    st.plotly_chart(fig5, use_container_width=True)

with col5_right:
    p5_str = "< .01" if p_intl < 0.01 else "< .05" if p_intl < 0.05 else f"= {p_intl:.3f}"
    st.markdown(f"""
    <div style='margin-top:1rem'>
    <div class="stat-card">
      <div class="val">r = {r_intl:.3f}</div>
      <div class="lbl">신뢰도-출산율 상관계수</div>
    </div>
    </div>
    <div style='margin-top:1rem'>
    <div class="stat-card">
      <div class="val">p {p5_str}</div>
      <div class="lbl">p-value</div>
    </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"""
<div class="insight-box">
  <p>사회신뢰도와 출산율 간 통계적 상관은 유의하지 않지만 (r = {r_intl:.3f}, p {p5_str}),
  한국은 비슷한 신뢰도 수준의 국가들보다 출산율이 압도적으로 낮은
  <strong>극단적 이상치</strong>로 나타난다.
  이는 한국의 저출산이 사회신뢰만으로 설명되지 않는 <strong>복합적 구조 문제</strong>임을 시사한다.</p>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# PART 06 — 종합
# ═══════════════════════════════════════════════
st.markdown("""
<div class="section-header">
  <div class="num">06</div>
  <div>
    <div class="title">종합: 세 가지 구조적 요인</div>
    <div class="sub">데이터가 가리키는 저출산의 근원</div>
  </div>
</div>
""", unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("""
    <div class="summary-card">
      <div class="icon">📚</div>
      <div class="ctitle">교육경쟁</div>
      <div class="corr">r = −0.714 (패널)</div>
      <div class="desc">
        사교육비 1만원 증가 → TFR 0.027 하락<br>
        연도 추세 r = −0.915<br>
        '집중 양육' 문화가 추가 출산을 억제
      </div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown("""
    <div class="summary-card">
      <div class="icon">🏠</div>
      <div class="ctitle">주거불안정</div>
      <div class="corr">r = −0.967 (max)</div>
      <div class="desc">
        주택매매가격지수 상승과 출산율 하락이 거의 완벽하게 동조화<br>
        '내 집 마련 후 출산' 심리적 장벽
      </div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown("""
    <div class="summary-card">
      <div class="icon">🚌</div>
      <div class="ctitle">통근부담</div>
      <div class="corr">r = −0.564</div>
      <div class="desc">
        장거리 통근은 육아 가능 시간을 박탈<br>
        시간 빈곤이 비금전적 출산 억제 요인으로 작용
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

col_radar, col_ins = st.columns([1, 1])

with col_radar:
    categories = ["교육비 부담", "주거 불안정", "통근 시간", "사회 신뢰", "예산 효과성"]
    values     = [0.714, 0.967, 0.564, 0.1,0.818]
    # 닫힌 레이더 위해 첫 값 추가
    categories_r = categories + [categories[0]]
    values_r     = values + [values[0]]

    fig6 = go.Figure(go.Scatterpolar(
        r=values_r,
        theta=categories_r,
        fill="toself",
        fillcolor="rgba(233,69,96,0.25)",
        line=dict(color=COLOR_MAIN, width=2),
        name="설명력 (|r|)",
    ))
    _layout6 = {**PLOTLY_LAYOUT, "margin": dict(t=70, b=40, l=10, r=10)}
    fig6.update_layout(
        **_layout6,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 1], gridcolor="#ede9e3", tickfont=dict(color="#888078")),
            angularaxis=dict(gridcolor="#ede9e3", tickfont=dict(color="#888078")),
        ),
        title=dict(
            text="저출산 요인별 설명력 (|r| 기반)",
            font=dict(color="#2b2b2b", size=17),
            x=0.5,
            xanchor="center",
            pad=dict(b=20),
        ),
        height=400,
        showlegend=False,
    )
    st.plotly_chart(fig6, use_container_width=True)

with col_ins:
    st.markdown("""
    <div class="insight-box" style="height:400px; display:flex; flex-direction:column; justify-content:center">
      <p>
        다섯 가지 요인 모두 출산율과 음의 상관관계를 보이며, 재정 투입만으로는 구조적 원인을 해소하기 어렵다.<br><br>
        <strong>필요한 대응:</strong><br><br>
        📚 <strong>사교육비 경감</strong> → 공교육 질 혁신, 입시 제도 다양화<br><br>
        🏠 <strong>주거 안정</strong> → 공공임대 확대, 청년·신혼 우선 공급<br><br>
        🚌 <strong>통근 완화</strong> → 직주근접 도시 설계, 재택·유연근무 제도화<br><br>
        💰 <strong>예산 효율화</strong> → 현금 지원 중심에서 구조 개선 중심으로 전환<br><br>
        🤝 <strong>사회 신뢰</strong> → 통계적 유의성은 낮으나,<br>
        <span style="padding-left:5.6rem;">공공 돌봄 인프라 확충 등 장기 과제로 검토 필요</span>
      </p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# SQL 쿼리 뷰어
# ═══════════════════════════════════════════════
with st.expander("🗄️ DB 조인 쿼리 확인 (SQLite)", expanded=False):
    st.code("""
-- JOIN 1: 교육비 × 출산율
SELECT e.sido, e.year, e.edu_cost_per_student, t.tfr
FROM tb_edu e
JOIN tb_tfr t ON e.sido = t.sido AND e.year = t.year;

-- JOIN 2: 주택가격 × 출산율
SELECT h.sido, h.year, h.house_price_index, t.tfr
FROM tb_house h
JOIN tb_tfr t ON h.sido = t.sido AND h.year = t.year;

-- JOIN 3: 통근시간 × 출산율
SELECT c.sido, c.move_2019_week, c.move_2024_week, t.tfr
FROM tb_commute c
JOIN tb_tfr t ON c.sido = t.sido AND t.year = 2024;

-- JOIN 4: 예산 × 전국 평균 출산율
SELECT b.year, b.budget_trillion, AVG(t.tfr) AS avg_tfr
FROM tb_budget b
JOIN tb_tfr t ON b.year = t.year
GROUP BY b.year, b.budget_trillion;
    """, language="sql")

# ═══════════════════════════════════════════════
# 푸터
# ═══════════════════════════════════════════════
st.markdown("""
<div class="footer">
  📊 데이터 출처: 통계청 인구동향조사 · 사교육비조사 · 생활시간조사,
  한국부동산원 주택매매가격지수, OECD Family Database,
  Integrated Values Survey / UN World Population Prospects<br>
  Built with Streamlit · Plotly · SQLite
</div>
""", unsafe_allow_html=True)
