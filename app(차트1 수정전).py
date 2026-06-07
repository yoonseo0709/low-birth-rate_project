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
COLOR_SECOND = "#0f3460"
COLOR_ACCENT = "#533483"

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#ccc", family="Noto Sans KR"),
    margin=dict(t=40, b=40, l=10, r=10),
)

AXIS_STYLE = dict(
    gridcolor="#1e2a45",
    zerolinecolor="#1e2a45",
    tickfont=dict(color="#aaa"),
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
    background-color: #0a0a1a;
}

/* HERO */
.hero {
    background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    padding: 3.5rem 2.5rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    text-align: center;
}
.hero h1 {
    font-size: 2.4rem;
    font-weight: 700;
    color: #fff;
    margin: 0 0 .8rem 0;
}
.hero p {
    font-size: 1.1rem;
    color: #c9c9e0;
    margin: 0;
}

/* SECTION HEADER */
.section-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 1.2rem 1.5rem;
    background: #1a1a2e;
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
    color: #fff;
}
.section-header .sub {
    font-size: .85rem;
    color: #aaa;
    margin-top: 3px;
}

/* STAT CARD */
.stat-card {
    background: #16213e;
    border: 1px solid #0f3460;
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
    color: #aaa;
    margin-top: 4px;
}

/* INSIGHT BOX */
.insight-box {
    background: linear-gradient(135deg, #16213e, #0f3460);
    border: 1px solid #e9456040;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-top: .8rem;
}
.insight-box p {
    color: #c9c9e0;
    font-size: .93rem;
    line-height: 1.65;
    margin: 0;
}
.insight-box strong {
    color: #e94560;
}

/* SUMMARY CARD */
.summary-card {
    background: #16213e;
    border: 1px solid #e9456030;
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
    color: #fff;
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
    color: #aaa;
    line-height: 1.6;
}

/* FOOTER */
.footer {
    text-align: center;
    color: #555;
    font-size: .8rem;
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #222;
}

/* Streamlit 기본 스타일 오버라이드 */
.stTabs [data-baseweb="tab-list"] {
    background-color: #1a1a2e;
    border-radius: 8px;
    padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #aaa;
}
.stTabs [aria-selected="true"] {
    background-color: #e94560 !important;
    color: #fff !important;
    border-radius: 6px;
}
div[data-testid="stSlider"] label {
    color: #ccc;
}
div[data-testid="stRadio"] label {
    color: #ccc;
}
div[data-testid="stMultiSelect"] label {
    color: #ccc;
}
.stDataFrame {
    background-color: #16213e;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DB 연결 & 데이터 로드
# ─────────────────────────────────────────────
@st.cache_resource
def get_conn():
    return sqlite3.connect("fertility.db", check_same_thread=False)

@st.cache_data
def load_budget():
    conn = get_conn()
    df = pd.read_sql("""
        SELECT b.year, b.budget_trillion, b.is_confirmed,
               AVG(t.tfr) AS tfr
        FROM tb_budget b
        LEFT JOIN tb_tfr t ON b.year = t.year
        GROUP BY b.year, b.budget_trillion, b.is_confirmed
        ORDER BY b.year
    """, conn)
    return df

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
    <div class="sub">정부 저출산 예산 vs 합계출산율 추이 (2006–2024)</div>
  </div>
</div>
""", unsafe_allow_html=True)

df_budget = load_budget()

fig1 = make_subplots(specs=[[{"secondary_y": True}]])

# 막대 — is_confirmed에 따라 색상 분리
colors_bar = [COLOR_MAIN if c == 1 else COLOR_SECOND for c in df_budget["is_confirmed"]]

fig1.add_trace(
    go.Bar(
        x=df_budget["year"],
        y=df_budget["budget_trillion"],
        name="저출산 예산 (조원)",
        marker_color=colors_bar,
        opacity=0.85,
        hovertemplate="%{y:.1f}조원<extra></extra>",
    ),
    secondary_y=False,
)

fig1.add_trace(
    go.Scatter(
        x=df_budget["year"],
        y=df_budget["tfr"],
        name="합계출산율 (TFR)",
        line=dict(color=COLOR_MAIN, width=3),
        marker=dict(size=7, color=COLOR_MAIN),
        mode="lines+markers",
        hovertemplate="TFR: %{y:.3f}<extra></extra>",
    ),
    secondary_y=True,
)

fig1.update_layout(
    **PLOTLY_LAYOUT,
    hovermode="x unified",
    legend=dict(orientation="h", y=1.08, x=0.5, xanchor="center"),
    height=420,
)
fig1.update_xaxes(**AXIS_STYLE, title_text="연도", title_font=dict(color="#aaa"))
fig1.update_yaxes(**AXIS_STYLE, title_text="예산 (조원)", title_font=dict(color="#aaa"), secondary_y=False)
fig1.update_yaxes(**AXIS_STYLE, title_text="합계출산율 (TFR)", title_font=dict(color=COLOR_MAIN), secondary_y=True)

# 범례 설명 annotation
fig1.add_annotation(
    x=0.01, y=1.13, xref="paper", yref="paper",
    text="🟥 확인된 예산   🟦 추정치",
    showarrow=False,
    font=dict(color="#aaa", size=11),
    bgcolor="rgba(0,0,0,0)",
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown("""
<div class="insight-box">
  <p>2006년 이후 저출산 예산이 지속 증가했음에도 합계출산율은 역대 최저 수준을 기록했다.
  단순한 재정 투입만으로는 출산율 반등을 이끌지 못한다는 것을 보여주며,
  <strong>사회구조적 근인(根因)</strong>에 주목할 필요가 있다.</p>
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
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={
            "edu_cost_per_student": "학생 1인당 사교육비 (만원)",
            "tfr": "합계출산율",
            "sido": "시도",
        },
        height=480,
    )
    fig2.update_layout(**PLOTLY_LAYOUT)
    fig2.update_xaxes(**AXIS_STYLE, title_font=dict(color="#aaa"))
    fig2.update_yaxes(**AXIS_STYLE, title_font=dict(color="#aaa"))
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
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={
                "year": "연도",
                "edu_cost_per_student": "학생 1인당 사교육비 (만원)",
                "sido": "시도",
            },
            height=420,
        )
        fig2b.update_layout(**PLOTLY_LAYOUT)
        fig2b.update_xaxes(**AXIS_STYLE, title_font=dict(color="#aaa"))
        fig2b.update_yaxes(**AXIS_STYLE, title_font=dict(color="#aaa"))
        st.plotly_chart(fig2b, use_container_width=True)
    else:
        st.info("시도를 한 개 이상 선택해주세요.")

st.markdown("""
<div class="insight-box">
  <p>학생 1인당 사교육비와 합계출산율은 전체 패널 기준 <strong>r = −0.714</strong>의 유의미한 음의 상관을 보인다 (p &lt; .001).
  연도 평균으로 분석하면 r = −0.915에 달하며, 고정효과 패널 모형에서도 사교육비
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

tab_h1, tab_h2 = st.tabs(["📊 시도별 상관관계", "📉 가격지수 추이"])

with tab_h1:
    # 시도별 pearsonr 계산 (데이터 4개 이상)
    corr_list = []
    for sido, grp in df_house.groupby("sido"):
        if len(grp) >= 4:
            r_h, p_h = stats.pearsonr(grp["house_price_index"], grp["tfr"])
            corr_list.append({"sido": sido, "r": r_h, "p": p_h})
    df_corr = pd.DataFrame(corr_list).sort_values("r")

    bar_colors = []
    for r in df_corr["r"]:
        if r < -0.7:
            bar_colors.append(COLOR_MAIN)
        elif r < 0:
            bar_colors.append(COLOR_SECOND)
        else:
            bar_colors.append("#555")

    fig3 = go.Figure(go.Bar(
        x=df_corr["r"],
        y=df_corr["sido"],
        orientation="h",
        marker_color=bar_colors,
        text=[f"r = {r:.3f}" for r in df_corr["r"]],
        textposition="outside",
        hovertemplate="%{y}: r = %{x:.3f}<extra></extra>",
    ))
    fig3.update_layout(
        **PLOTLY_LAYOUT,
        height=520,
        xaxis=dict(**AXIS_STYLE, range=[-1.1, 0.3], title="피어슨 상관계수 r", title_font=dict(color="#aaa")),
        yaxis=dict(**AXIS_STYLE, title=""),
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown(
        "<div style='text-align:center;color:#aaa;font-size:.85rem;margin-top:-.5rem'>"
        "🔴 r &lt; -0.7: 강한 음의 상관 / 🔵 r &lt; 0: 음의 상관</div>",
        unsafe_allow_html=True,
    )

with tab_h2:
    sido_h_list = sorted(df_house["sido"].unique().tolist())
    default_h = ["서울특별시", "경기도", "세종특별자치시", "전라남도"]
    sel_h = st.multiselect("시도 선택", sido_h_list, default=default_h, key="house_sido")

    if sel_h:
        df_house_f = df_house[df_house["sido"].isin(sel_h)]
        palette = px.colors.qualitative.Bold
        color_map = {s: palette[i % len(palette)] for i, s in enumerate(sel_h)}

        fig3b = make_subplots(specs=[[{"secondary_y": True}]])
        for sido in sel_h:
            grp = df_house_f[df_house_f["sido"] == sido].sort_values("year")
            col = color_map[sido]
            fig3b.add_trace(
                go.Scatter(
                    x=grp["year"], y=grp["house_price_index"],
                    name=f"{sido} (지수)",
                    line=dict(color=col, width=2),
                    mode="lines+markers",
                    hovertemplate=f"{sido} 지수: %{{y:.1f}}<extra></extra>",
                ),
                secondary_y=False,
            )
            fig3b.add_trace(
                go.Scatter(
                    x=grp["year"], y=grp["tfr"],
                    name=f"{sido} (TFR)",
                    line=dict(color=col, width=2, dash="dash"),
                    mode="lines+markers",
                    marker=dict(symbol="diamond"),
                    hovertemplate=f"{sido} TFR: %{{y:.3f}}<extra></extra>",
                ),
                secondary_y=True,
            )
        fig3b.update_layout(
            **PLOTLY_LAYOUT,
            height=460,
            legend=dict(orientation="h", y=-0.2, x=0.5, xanchor="center"),
        )
        fig3b.update_xaxes(**AXIS_STYLE, title_text="연도", title_font=dict(color="#aaa"))
        fig3b.update_yaxes(**AXIS_STYLE, title_text="주택매매가격지수", title_font=dict(color="#aaa"), secondary_y=False)
        fig3b.update_yaxes(**AXIS_STYLE, title_text="합계출산율 (TFR)", title_font=dict(color=COLOR_MAIN), secondary_y=True)
        st.plotly_chart(fig3b, use_container_width=True)
    else:
        st.info("시도를 한 개 이상 선택해주세요.")

st.markdown("""
<div class="insight-box">
  <p>서울·경기 등 주요 광역시에서 주택매매가격지수와 합계출산율 간 상관계수는 최대
  <strong>r = -0.967</strong>에 달한다. 집값이 오를수록 출산율이 가파르게 하락하는 패턴이 뚜렷하며,
  '내 집 마련 전에는 아이를 낳기 어렵다'는 경제적 불안감이 출산 결정을 지연·포기시키는
  구조임을 보여준다.</p>
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
    <div class="sub">평균 이동시간 × 합계출산율 (시도별, 2019 &amp; 2024)</div>
  </div>
</div>
""", unsafe_allow_html=True)

df_commute = load_commute()

year_sel = st.radio(
    "비교 연도", ["2019년", "2024년"], horizontal=True, key="commute_year"
)
col_sel = "move_2019_week" if year_sel == "2019년" else "move_2024_week"

r_com, p_com = stats.pearsonr(df_commute[col_sel], df_commute["tfr"])

col_left, col_right = st.columns([2, 1])

with col_left:
    fig4 = px.scatter(
        df_commute,
        x=col_sel, y="tfr",
        text="sido",
        trendline="ols",
        trendline_color_override=COLOR_MAIN,
        color_discrete_sequence=[COLOR_ACCENT],
        labels={
            col_sel: f"주평균 이동시간 ({year_sel[:4]}년, 분)",
            "tfr": "합계출산율",
        },
        height=420,
    )
    fig4.update_traces(
        marker=dict(size=11, color=COLOR_ACCENT, opacity=0.85),
        textposition="top center",
        selector=dict(mode="markers+text"),
    )
    fig4.update_layout(**PLOTLY_LAYOUT)
    fig4.update_xaxes(**AXIS_STYLE, title_font=dict(color="#aaa"))
    fig4.update_yaxes(**AXIS_STYLE, title_font=dict(color="#aaa"))
    st.plotly_chart(fig4, use_container_width=True)

with col_right:
    p_str = "< .05" if p_com < 0.05 else f"= {p_com:.3f}"
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

    st.markdown("<div style='margin-top:1.2rem;color:#fff;font-weight:600'>이동시간 상위 3개 시도</div>", unsafe_allow_html=True)
    top3 = df_commute.nlargest(3, col_sel)[["sido", col_sel, "tfr"]].rename(
        columns={col_sel: "이동시간(분)", "tfr": "TFR"}
    ).set_index("sido")
    st.dataframe(top3, use_container_width=True)

    st.markdown("<div style='margin-top:.8rem;color:#fff;font-weight:600'>이동시간 하위 3개 시도</div>", unsafe_allow_html=True)
    bot3 = df_commute.nsmallest(3, col_sel)[["sido", col_sel, "tfr"]].rename(
        columns={col_sel: "이동시간(분)", "tfr": "TFR"}
    ).set_index("sido")
    st.dataframe(bot3, use_container_width=True)

st.markdown("""
<div class="insight-box">
  <p>주평균 이동시간이 길수록 합계출산율이 낮아지는 경향이 확인된다 (r ≈ −0.56, p &lt; .05).
  경기도·서울·인천 등 수도권 장거리 통근 지역은 육아·가사에 투입할 수 있는 시간 자원이 절대적으로 부족해진다.
  <strong>시간 빈곤(time poverty)</strong>이 출산을 억제하는 비금전적 요인으로 작용함을 시사한다.</p>
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

fig5 = px.scatter(
    df_intl,
    x="trust_pct", y="tfr",
    color="group",
    text="country",
    trendline="ols",
    trendline_scope="overall",
    trendline_color_override="#f5c518",
    color_discrete_map={"🇰🇷 한국": COLOR_MAIN, "기타 OECD": "#4a6fa5"},
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

p_str5 = "< .05" if p_intl < 0.05 else f"= {p_intl:.2f}"
fig5.add_annotation(
    x=0.98, y=0.05, xref="paper", yref="paper",
    text=f"r = {r_intl:.3f}  (p {p_str5})",
    showarrow=False,
    font=dict(color="#f5c518", size=13),
    bgcolor="#16213e",
    bordercolor="#f5c518",
    borderwidth=1,
)
fig5.update_layout(**PLOTLY_LAYOUT)
fig5.update_xaxes(**AXIS_STYLE, title_font=dict(color="#aaa"))
fig5.update_yaxes(**AXIS_STYLE, title_font=dict(color="#aaa"))
st.plotly_chart(fig5, use_container_width=True)

st.markdown("""
<div class="insight-box">
  <p>OECD 국가 비교에서 사회신뢰도가 높은 국가일수록 출산율도 높은 경향이 나타난다.
  한국은 낮은 사회신뢰도와 낮은 출산율 모두에서 하위권에 위치한다.
  사회적 지지망과 공공기관에 대한 신뢰가 부족한 환경에서는
  <strong>'아이를 낳아도 사회가 함께 키워줄 것'</strong>이라는 기대가 형성되기 어렵다.</p>
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
      <div class="corr">r = −0.564 (2019)</div>
      <div class="desc">
        장거리 통근은 육아 가능 시간을 박탈<br>
        시간 빈곤(time poverty)이 비금전적 출산 억제 요인으로 작용
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)

col_radar, col_ins = st.columns([1, 1])

with col_radar:
    categories = ["교육비 부담", "주거 불안정", "통근 시간", "사회 신뢰", "예산 효과성"]
    values     = [0.714, 0.967, 0.564, 0.45, 0.1]
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
    fig6.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(range=[0, 1], gridcolor="#1e2a45", tickfont=dict(color="#aaa")),
            angularaxis=dict(gridcolor="#1e2a45", tickfont=dict(color="#ccc")),
        ),
        title=dict(
            text="저출산 요인별 설명력 (|r| 기반)",
            font=dict(color="#fff", size=14),
            x=0.5,
        ),
        height=380,
        showlegend=False,
    )
    st.plotly_chart(fig6, use_container_width=True)

with col_ins:
    st.markdown("""
    <div class="insight-box" style="height:340px; display:flex; flex-direction:column; justify-content:center">
      <p>
        세 가지 요인 모두 출산율과 강한 음의 상관관계를 보이며, 단순 현금 지원 정책만으로는 구조적 원인을 해소하기 어렵다.<br><br>
        <strong>필요한 대응:</strong><br><br>
        📚 <strong>사교육비 경감</strong> → 공교육 질 혁신, 입시 제도 다양화<br><br>
        🏠 <strong>주거 안정</strong> → 공공임대 확대, 청년·신혼 우선 공급<br><br>
        🚌 <strong>통근 완화</strong> → 직주근접 도시 설계, 재택·유연근무 제도화
      </p>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════
# SQL 쿼리 뷰어
# ═══════════════════════════════════════════════
with st.expander("🗄️ DB 조인 쿼리 확인 (SQLite)", expanded=False):
    st.code("""
-- 교육비 × 학원 밀도 × 출산율 3-way JOIN
SELECT e.sido, e.year, e.edu_cost_per_student, a.academy_per_1000, t.tfr
FROM tb_edu e
JOIN tb_tfr t ON e.sido = t.sido AND e.year = t.year
JOIN tb_academy a ON e.sido = a.sido AND e.year = a.year;

-- 주택가격지수 × 출산율 JOIN
SELECT h.sido, h.year, h.house_price_index, t.tfr
FROM tb_house h
JOIN tb_tfr t ON h.sido = t.sido AND h.year = t.year;

-- 통근시간 × 출산율 JOIN (2024년 기준)
SELECT c.sido, c.move_2019_week, c.move_2024_week, t.tfr
FROM tb_commute c
JOIN tb_tfr t ON c.sido = t.sido AND t.year = 2024;
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
