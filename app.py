"""
Football Player Performance Analytics Dashboard
================================================
Synthetic data only — not real-world football statistics.
Run:  streamlit run app.py
"""

import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ──────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# THEME / CSS
# ──────────────────────────────────────────────────────────────────────────────
DARK_BG      = "#0d1117"
SURFACE      = "#161b22"
ACCENT_GREEN = "#00c853"
TEXT_LIGHT   = "#e6edf3"
TEXT_MUTED   = "#8b949e"
BORDER       = "#30363d"
CHART_COLORS = [
    "#00c853", "#1de9b6", "#00b0ff", "#d500f9",
    "#ff6d00", "#ffea00", "#f50057", "#76ff03",
    "#40c4ff", "#e040fb",
]

st.markdown(
    f"""
    <style>
    /* ── global ── */
    html, body, [class*="css"] {{
        background-color: {DARK_BG};
        color: {TEXT_LIGHT};
        font-family: 'Segoe UI', system-ui, sans-serif;
    }}
    .stApp {{ background-color: {DARK_BG}; }}

    /* ── sidebar ── */
    [data-testid="stSidebar"] {{
        background-color: {SURFACE};
        border-right: 1px solid {BORDER};
    }}
    [data-testid="stSidebar"] * {{ color: {TEXT_LIGHT} !important; }}

    /* ── metric cards ── */
    [data-testid="stMetric"] {{
        background-color: {SURFACE};
        border: 1px solid {BORDER};
        border-radius: 10px;
        padding: 16px 20px;
    }}
    [data-testid="stMetricLabel"] {{ color: {TEXT_MUTED} !important; font-size: 0.82rem; }}
    [data-testid="stMetricValue"] {{ color: {ACCENT_GREEN} !important; font-size: 1.8rem; font-weight: 700; }}
    [data-testid="stMetricDelta"] {{ font-size: 0.78rem; }}

    /* ── section headers ── */
    .section-header {{
        font-size: 1.15rem;
        font-weight: 600;
        color: {ACCENT_GREEN};
        border-left: 4px solid {ACCENT_GREEN};
        padding-left: 10px;
        margin: 24px 0 12px 0;
    }}

    /* ── page title ── */
    .page-title {{
        font-size: 2rem;
        font-weight: 800;
        color: {TEXT_LIGHT};
        margin-bottom: 4px;
    }}
    .page-subtitle {{
        font-size: 0.9rem;
        color: {TEXT_MUTED};
        margin-bottom: 24px;
    }}

    /* ── data table ── */
    [data-testid="stDataFrame"] {{ border-radius: 8px; overflow: hidden; }}

    /* ── buttons ── */
    .stButton > button, .stDownloadButton > button {{
        background-color: {ACCENT_GREEN};
        color: #000;
        font-weight: 600;
        border: none;
        border-radius: 6px;
        padding: 8px 18px;
    }}
    .stDownloadButton > button:hover {{ opacity: 0.88; }}

    /* ── divider ── */
    hr {{ border-color: {BORDER}; }}

    /* ── synthetic badge ── */
    .synthetic-badge {{
        display: inline-block;
        background: #2d333b;
        color: #f0a500;
        font-size: 0.72rem;
        font-weight: 600;
        border: 1px solid #f0a500;
        border-radius: 20px;
        padding: 2px 10px;
        letter-spacing: 0.05em;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────────────────────────────────────
# PLOTLY CHART TEMPLATE
# ──────────────────────────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor=SURFACE,
    plot_bgcolor=SURFACE,
    font=dict(family="Segoe UI, system-ui, sans-serif", color=TEXT_LIGHT, size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    colorway=CHART_COLORS,
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor=BORDER, borderwidth=1),
    xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
    yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER),
)


def style_fig(fig: go.Figure) -> go.Figure:
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


# ──────────────────────────────────────────────────────────────────────────────
# DATA LOADING & VALIDATION
# ──────────────────────────────────────────────────────────────────────────────
CSV_PATH = "football_players.csv"

REQUIRED_COLUMNS = [
    "player_id", "player_name", "team", "position", "season", "age",
    "nationality", "matches_played", "minutes_played", "goals", "assists",
    "shots", "shots_on_target", "passes", "pass_accuracy", "tackles",
    "interceptions", "yellow_cards", "red_cards", "clean_sheets", "rating",
]


@st.cache_data(show_spinner="Loading dataset…")
def load_data() -> pd.DataFrame:
    if not os.path.exists(CSV_PATH):
        st.error(
            f"❌ Dataset file `{CSV_PATH}` not found. "
            "Please ensure `football_players.csv` is in the same directory as `app.py`."
        )
        st.stop()

    df = pd.read_csv(CSV_PATH)

    # column validation
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        st.error(f"❌ CSV is missing columns: {missing_cols}")
        st.stop()

    # fill missing numeric values with column median
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    null_before = df[numeric_cols].isnull().sum().sum()
    df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
    df["position"] = df["position"].fillna("Unknown")
    df["team"]     = df["team"].fillna("Unknown")
    null_after = df[numeric_cols].isnull().sum().sum()

    if null_before > 0:
        st.sidebar.info(f"ℹ️ Filled {null_before} missing value(s) with column median.")

    # derived columns
    df["shot_conversion"] = np.where(df["shots"] > 0, df["goals"] / df["shots"] * 100, 0.0)
    df["goals_per_90"]    = np.where(df["minutes_played"] > 0, df["goals"] / df["minutes_played"] * 90, 0.0)
    df["assists_per_90"]  = np.where(df["minutes_played"] > 0, df["assists"] / df["minutes_played"] * 90, 0.0)

    return df


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
def render_sidebar(df: pd.DataFrame):
    st.sidebar.markdown(
        "<div style='text-align:center; padding: 8px 0 4px 0;'>"
        "<span style='font-size:2.2rem;'>⚽</span><br>"
        "<span style='font-size:1.1rem; font-weight:700; color:#00c853;'>Football Analytics</span><br>"
        "<span class='synthetic-badge'>⚠ SYNTHETIC DATA</span>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🔍 Filters")

    seasons   = ["All"] + sorted(df["season"].unique().tolist())
    teams     = ["All"] + sorted(df["team"].unique().tolist())
    positions = ["All"] + sorted(df["position"].unique().tolist())

    sel_season   = st.sidebar.selectbox("Season",   seasons,   index=0)
    sel_teams    = st.sidebar.multiselect("Team",   sorted(df["team"].unique()), default=[])
    sel_positions= st.sidebar.multiselect("Position", sorted(df["position"].unique()), default=[])

    # filter before offering player names
    filtered = df.copy()
    if sel_season != "All":
        filtered = filtered[filtered["season"] == sel_season]
    if sel_teams:
        filtered = filtered[filtered["team"].isin(sel_teams)]
    if sel_positions:
        filtered = filtered[filtered["position"].isin(sel_positions)]

    all_players   = sorted(filtered["player_name"].unique().tolist())
    sel_players   = st.sidebar.multiselect("Player", all_players, default=[])

    min_rating = st.sidebar.slider(
        "Minimum Rating", min_value=5.0, max_value=10.0, value=5.0, step=0.1
    )

    st.sidebar.markdown("---")

    if st.sidebar.button("🔄 Reset Filters"):
        st.rerun()

    # apply all filters
    if sel_players:
        filtered = filtered[filtered["player_name"].isin(sel_players)]
    filtered = filtered[filtered["rating"] >= min_rating]

    # CSV download
    csv_bytes = filtered.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(
        label="📥 Download Filtered CSV",
        data=csv_bytes,
        file_name="filtered_football_data.csv",
        mime="text/csv",
    )

    st.sidebar.markdown(
        f"<div style='color:{TEXT_MUTED}; font-size:0.75rem; margin-top:10px;'>"
        f"Showing <b style='color:{ACCENT_GREEN};'>{len(filtered)}</b> rows from "
        f"<b style='color:{ACCENT_GREEN};'>{filtered['player_name'].nunique()}</b> players"
        "</div>",
        unsafe_allow_html=True,
    )

    return filtered


# ──────────────────────────────────────────────────────────────────────────────
# HELPER: empty-data guard
# ──────────────────────────────────────────────────────────────────────────────
def guard_empty(df: pd.DataFrame, context: str = "chart") -> bool:
    if df.empty:
        st.warning(
            "⚠️ No data matches the selected filters. "
            "Please adjust the sidebar filters to see this " + context + "."
        )
        return True
    return False


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 1 — OVERVIEW
# ──────────────────────────────────────────────────────────────────────────────
def page_overview(df: pd.DataFrame, raw_df: pd.DataFrame):
    st.markdown("<div class='page-title'>📊 Overview</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>High-level KPIs and top-performer summaries across the filtered dataset.</div>",
        unsafe_allow_html=True,
    )

    if guard_empty(df, "overview"):
        return

    # ── KPI Cards ────────────────────────────────────────────────────────────
    total_players  = df["player_name"].nunique()
    total_goals    = int(df["goals"].sum())
    total_assists  = int(df["assists"].sum())
    total_minutes  = int(df["minutes_played"].sum())
    avg_rating     = round(df["rating"].mean(), 2)

    # previous-season deltas (only meaningful when one season is selected)
    seasons_in_filter = df["season"].unique()
    if len(seasons_in_filter) == 1:
        current_season  = seasons_in_filter[0]
        all_seasons     = sorted(raw_df["season"].unique())
        idx             = all_seasons.index(current_season)
        if idx > 0:
            prev_season = all_seasons[idx - 1]
            prev_df = raw_df[raw_df["season"] == prev_season]
            goals_delta   = total_goals  - int(prev_df["goals"].sum())
            assists_delta = total_assists - int(prev_df["assists"].sum())
            rating_delta  = round(avg_rating - prev_df["rating"].mean(), 2)
        else:
            goals_delta = assists_delta = rating_delta = None
    else:
        goals_delta = assists_delta = rating_delta = None

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("👥 Total Players",        f"{total_players:,}")
    c2.metric("⚽ Total Goals",          f"{total_goals:,}",   delta=goals_delta)
    c3.metric("🎯 Total Assists",        f"{total_assists:,}", delta=assists_delta)
    c4.metric("⏱ Minutes Played",       f"{total_minutes/1_000_000:.2f}M")
    c5.metric("⭐ Avg Player Rating",   f"{avg_rating}",      delta=rating_delta)

    st.markdown("---")

    # ── Top 10 Scorers ───────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>🏆 Top 10 Goal Scorers</div>", unsafe_allow_html=True)

    top_scorers = (
        df.groupby(["player_name", "team", "position"])
        .agg(goals=("goals", "sum"), assists=("assists", "sum"), rating=("rating", "mean"))
        .reset_index()
        .sort_values("goals", ascending=False)
        .head(10)
    )

    if not top_scorers.empty:
        fig_scorers = px.bar(
            top_scorers,
            x="goals",
            y="player_name",
            orientation="h",
            color="team",
            text="goals",
            hover_data={"assists": True, "rating": ":.2f", "position": True},
            labels={"goals": "Goals", "player_name": "Player", "team": "Team"},
            color_discrete_sequence=CHART_COLORS,
        )
        fig_scorers.update_traces(textposition="outside")
        fig_scorers.update_layout(
            **PLOTLY_LAYOUT,
            title="Top 10 Goal Scorers",
            yaxis=dict(autorange="reversed", gridcolor=BORDER),
            height=380,
            showlegend=True,
        )
        st.plotly_chart(fig_scorers, use_container_width=True)

    st.markdown("---")
    col_left, col_right = st.columns(2)

    # ── Goals by Position — donut ─────────────────────────────────────────────
    with col_left:
        st.markdown("<div class='section-header'>📐 Goals by Position</div>", unsafe_allow_html=True)
        pos_goals = df.groupby("position")["goals"].sum().reset_index()
        if not pos_goals.empty:
            fig_donut = px.pie(
                pos_goals,
                names="position",
                values="goals",
                hole=0.55,
                color_discrete_sequence=CHART_COLORS,
            )
            fig_donut.update_traces(
                textinfo="percent+label",
                hovertemplate="<b>%{label}</b><br>Goals: %{value}<br>Share: %{percent}<extra></extra>",
            )
            fig_donut.update_layout(**PLOTLY_LAYOUT, title="Goals Distribution by Position", height=360)
            st.plotly_chart(fig_donut, use_container_width=True)

    # ── Rating Distribution — histogram ──────────────────────────────────────
    with col_right:
        st.markdown("<div class='section-header'>📈 Player Rating Distribution</div>", unsafe_allow_html=True)
        fig_hist = px.histogram(
            df,
            x="rating",
            nbins=25,
            color="position",
            barmode="overlay",
            opacity=0.75,
            color_discrete_sequence=CHART_COLORS,
            labels={"rating": "Rating", "count": "Players"},
        )
        fig_hist.update_layout(
            **PLOTLY_LAYOUT, title="Player Rating Distribution", height=360, bargap=0.05
        )
        st.plotly_chart(fig_hist, use_container_width=True)


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 2 — PLAYER ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────
def page_player_analysis(df: pd.DataFrame):
    st.markdown("<div class='page-title'>🔍 Player Analysis</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>Compare individual player performance through scatter charts, radar comparison and a detailed statistics table.</div>",
        unsafe_allow_html=True,
    )

    if guard_empty(df, "player analysis"):
        return

    # ── Goals vs Assists Scatter ──────────────────────────────────────────────
    st.markdown("<div class='section-header'>⚽ Goals vs Assists</div>", unsafe_allow_html=True)

    fig_ga = px.scatter(
        df,
        x="goals",
        y="assists",
        size="minutes_played",
        color="position",
        hover_name="player_name",
        hover_data={"team": True, "rating": ":.2f", "minutes_played": True},
        labels={"goals": "Goals", "assists": "Assists", "minutes_played": "Minutes Played"},
        color_discrete_sequence=CHART_COLORS,
        opacity=0.85,
    )
    fig_ga.update_layout(
        **PLOTLY_LAYOUT, title="Goals vs Assists (bubble size = minutes played)", height=430
    )
    st.plotly_chart(fig_ga, use_container_width=True)

    st.markdown("---")
    col_l, col_r = st.columns(2)

    # ── Shots vs Goals Scatter ────────────────────────────────────────────────
    with col_l:
        st.markdown("<div class='section-header'>🎯 Shots vs Goals (Conversion)</div>", unsafe_allow_html=True)
        fig_sg = px.scatter(
            df,
            x="shots",
            y="goals",
            size="rating",
            color="team",
            hover_name="player_name",
            hover_data={"shot_conversion": ":.1f", "shots_on_target": True, "position": True},
            labels={"shots": "Total Shots", "goals": "Goals", "shot_conversion": "Conversion %"},
            color_discrete_sequence=CHART_COLORS,
            opacity=0.85,
        )
        fig_sg.update_layout(
            **PLOTLY_LAYOUT, title="Shots vs Goals (bubble size = rating)", height=380
        )
        st.plotly_chart(fig_sg, use_container_width=True)

    # ── Goals per 90 — Top 15 ────────────────────────────────────────────────
    with col_r:
        st.markdown("<div class='section-header'>⚡ Goals per 90 Minutes</div>", unsafe_allow_html=True)
        top_g90 = (
            df[df["minutes_played"] >= 450]
            .groupby(["player_name", "position"])
            .agg(gp90=("goals_per_90", "mean"))
            .reset_index()
            .sort_values("gp90", ascending=False)
            .head(15)
        )
        if not top_g90.empty:
            fig_g90 = px.bar(
                top_g90,
                x="gp90",
                y="player_name",
                color="position",
                orientation="h",
                text=top_g90["gp90"].round(2),
                labels={"gp90": "Goals / 90 min", "player_name": "Player"},
                color_discrete_sequence=CHART_COLORS,
            )
            fig_g90.update_traces(textposition="outside")
            fig_g90.update_layout(
                **PLOTLY_LAYOUT,
                title="Top 15 — Goals per 90 min (min 450 mins played)",
                yaxis=dict(autorange="reversed", gridcolor=BORDER),
                height=380,
            )
            st.plotly_chart(fig_g90, use_container_width=True)

    st.markdown("---")

    # ── Radar Comparison ─────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>🕸 Player Radar Comparison</div>", unsafe_allow_html=True)

    all_players = sorted(df["player_name"].unique().tolist())
    default_two = all_players[:2] if len(all_players) >= 2 else all_players

    selected_radar = st.multiselect(
        "Select 2–5 players to compare on the radar chart:",
        options=all_players,
        default=default_two,
        key="radar_select",
    )

    RADAR_ATTRS = ["goals", "assists", "shots", "passes", "tackles", "rating"]
    RADAR_LABELS = ["Goals", "Assists", "Shots", "Passes", "Tackles", "Rating"]

    if len(selected_radar) < 2:
        st.info("ℹ️ Select at least 2 players to display the radar comparison.")
    elif len(selected_radar) > 5:
        st.info("ℹ️ Select at most 5 players for a readable radar chart.")
    else:
        radar_df = df[df["player_name"].isin(selected_radar)].groupby("player_name")[RADAR_ATTRS].mean().reset_index()

        # normalise 0–100
        for col in RADAR_ATTRS:
            col_min, col_max = df[col].min(), df[col].max()
            if col_max > col_min:
                radar_df[col] = (radar_df[col] - col_min) / (col_max - col_min) * 100
            else:
                radar_df[col] = 0

        fig_radar = go.Figure()
        for i, row in radar_df.iterrows():
            vals = [row[c] for c in RADAR_ATTRS]
            vals += [vals[0]]  # close the polygon
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=vals,
                    theta=RADAR_LABELS + [RADAR_LABELS[0]],
                    fill="toself",
                    name=row["player_name"],
                    line=dict(color=CHART_COLORS[i % len(CHART_COLORS)], width=2),
                    opacity=0.75,
                )
            )
        fig_radar.update_layout(
            **PLOTLY_LAYOUT,
            title="Radar Comparison (normalised 0–100)",
            polar=dict(
                bgcolor=SURFACE,
                radialaxis=dict(visible=True, range=[0, 100], gridcolor=BORDER, color=TEXT_MUTED),
                angularaxis=dict(gridcolor=BORDER, color=TEXT_LIGHT),
            ),
            height=460,
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    st.markdown("---")

    # ── Searchable Stats Table ────────────────────────────────────────────────
    st.markdown("<div class='section-header'>📋 Player Statistics Table</div>", unsafe_allow_html=True)

    search_term = st.text_input("🔎 Search player name:", placeholder="Type a player name…")
    display_cols = [
        "player_name", "team", "position", "season", "age",
        "goals", "assists", "shots", "shot_conversion",
        "passes", "pass_accuracy", "tackles", "rating",
        "minutes_played", "yellow_cards", "red_cards",
    ]
    table_df = df[display_cols].copy()
    table_df["shot_conversion"] = table_df["shot_conversion"].round(1)
    table_df["pass_accuracy"]   = table_df["pass_accuracy"].round(1)
    table_df["rating"]          = table_df["rating"].round(2)

    if search_term:
        table_df = table_df[table_df["player_name"].str.contains(search_term, case=False, na=False)]
        if table_df.empty:
            st.warning(f"No players found matching **'{search_term}'**.")

    st.dataframe(
        table_df.sort_values("goals", ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=400,
    )


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 3 — TEAM ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────
def page_team_analysis(df: pd.DataFrame):
    st.markdown("<div class='page-title'>🏟 Team Analysis</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>Aggregated team-level performance metrics for goals, assists, squad depth and average ratings.</div>",
        unsafe_allow_html=True,
    )

    if guard_empty(df, "team analysis"):
        return

    team_df = (
        df.groupby("team")
        .agg(
            goals=("goals", "sum"),
            assists=("assists", "sum"),
            players=("player_name", "nunique"),
            avg_rating=("rating", "mean"),
            total_shots=("shots", "sum"),
            total_passes=("passes", "sum"),
        )
        .reset_index()
        .sort_values("goals", ascending=False)
    )
    team_df["avg_rating"] = team_df["avg_rating"].round(2)

    # ── Goals + Assists grouped bar ───────────────────────────────────────────
    st.markdown("<div class='section-header'>⚽ Team Goals & Assists</div>", unsafe_allow_html=True)

    fig_team = go.Figure()
    fig_team.add_trace(
        go.Bar(name="Goals",   x=team_df["team"], y=team_df["goals"],   marker_color=CHART_COLORS[0], text=team_df["goals"],   textposition="outside")
    )
    fig_team.add_trace(
        go.Bar(name="Assists", x=team_df["team"], y=team_df["assists"], marker_color=CHART_COLORS[1], text=team_df["assists"], textposition="outside")
    )
    fig_team.update_layout(
        **PLOTLY_LAYOUT,
        title="Total Goals & Assists per Team",
        barmode="group",
        xaxis_title="Team",
        yaxis_title="Count",
        height=400,
    )
    st.plotly_chart(fig_team, use_container_width=True)

    st.markdown("---")
    c_left, c_right = st.columns(2)

    # ── Avg Rating ────────────────────────────────────────────────────────────
    with c_left:
        st.markdown("<div class='section-header'>⭐ Average Player Rating by Team</div>", unsafe_allow_html=True)
        fig_rating = px.bar(
            team_df.sort_values("avg_rating", ascending=True),
            x="avg_rating",
            y="team",
            orientation="h",
            text="avg_rating",
            color="avg_rating",
            color_continuous_scale=["#1a3a2a", ACCENT_GREEN],
            labels={"avg_rating": "Avg Rating", "team": "Team"},
        )
        fig_rating.update_traces(textposition="outside")
        fig_rating.update_layout(
            **PLOTLY_LAYOUT,
            title="Average Player Rating by Team",
            coloraxis_showscale=False,
            height=360,
        )
        st.plotly_chart(fig_rating, use_container_width=True)

    # ── Player Count ─────────────────────────────────────────────────────────
    with c_right:
        st.markdown("<div class='section-header'>👥 Squad Depth (Player Count)</div>", unsafe_allow_html=True)
        fig_players = px.bar(
            team_df.sort_values("players", ascending=True),
            x="players",
            y="team",
            orientation="h",
            text="players",
            color="players",
            color_continuous_scale=["#1a2a3a", "#00b0ff"],
            labels={"players": "Unique Players", "team": "Team"},
        )
        fig_players.update_traces(textposition="outside")
        fig_players.update_layout(
            **PLOTLY_LAYOUT,
            title="Unique Players per Team (filtered view)",
            coloraxis_showscale=False,
            height=360,
        )
        st.plotly_chart(fig_players, use_container_width=True)

    st.markdown("---")

    # ── Team Stats Table ──────────────────────────────────────────────────────
    st.markdown("<div class='section-header'>📊 Team Summary Table</div>", unsafe_allow_html=True)
    st.dataframe(
        team_df.rename(columns={
            "team": "Team", "goals": "Goals", "assists": "Assists",
            "players": "Players", "avg_rating": "Avg Rating",
            "total_shots": "Total Shots", "total_passes": "Total Passes",
        }).reset_index(drop=True),
        use_container_width=True,
        height=380,
    )


# ──────────────────────────────────────────────────────────────────────────────
# PAGE 4 — POSITION ANALYSIS
# ──────────────────────────────────────────────────────────────────────────────
def page_position_analysis(df: pd.DataFrame):
    st.markdown("<div class='page-title'>📐 Position Analysis</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='page-subtitle'>Breakdown of player statistics by playing position — Goalkeepers, Defenders, Midfielders and Forwards.</div>",
        unsafe_allow_html=True,
    )

    if guard_empty(df, "position analysis"):
        return

    col_l, col_r = st.columns(2)

    # ── Goals by Position — box plot ──────────────────────────────────────────
    with col_l:
        st.markdown("<div class='section-header'>⚽ Goals Distribution by Position</div>", unsafe_allow_html=True)
        fig_box = px.box(
            df,
            x="position",
            y="goals",
            color="position",
            points="outliers",
            color_discrete_sequence=CHART_COLORS,
            labels={"goals": "Goals", "position": "Position"},
            category_orders={"position": ["GK", "DEF", "MID", "FWD"]},
        )
        fig_box.update_layout(**PLOTLY_LAYOUT, title="Goals Distribution by Position", height=380, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    # ── Pass Accuracy — violin ────────────────────────────────────────────────
    with col_r:
        st.markdown("<div class='section-header'>🎯 Pass Accuracy by Position</div>", unsafe_allow_html=True)
        fig_violin = px.violin(
            df,
            x="position",
            y="pass_accuracy",
            color="position",
            box=True,
            points="outliers",
            color_discrete_sequence=CHART_COLORS,
            labels={"pass_accuracy": "Pass Accuracy (%)", "position": "Position"},
            category_orders={"position": ["GK", "DEF", "MID", "FWD"]},
        )
        fig_violin.update_layout(**PLOTLY_LAYOUT, title="Pass Accuracy Distribution by Position", height=380, showlegend=False)
        st.plotly_chart(fig_violin, use_container_width=True)

    st.markdown("---")
    col_l2, col_r2 = st.columns(2)

    # ── Squad composition — stacked bar ──────────────────────────────────────
    with col_l2:
        st.markdown("<div class='section-header'>🏟 Squad Composition per Team</div>", unsafe_allow_html=True)
        comp_df = (
            df.groupby(["team", "position"])["player_name"]
            .nunique()
            .reset_index()
            .rename(columns={"player_name": "count"})
        )
        fig_comp = px.bar(
            comp_df,
            x="team",
            y="count",
            color="position",
            barmode="stack",
            color_discrete_sequence=CHART_COLORS,
            labels={"count": "Players", "team": "Team", "position": "Position"},
            category_orders={"position": ["GK", "DEF", "MID", "FWD"]},
        )
        fig_comp.update_layout(
            **PLOTLY_LAYOUT,
            title="Squad Composition by Position per Team",
            xaxis_tickangle=-35,
            height=400,
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    # ── GK Clean Sheets ───────────────────────────────────────────────────────
    with col_r2:
        st.markdown("<div class='section-header'>🧤 Goalkeeper Clean Sheets</div>", unsafe_allow_html=True)
        gk_df = (
            df[df["position"] == "GK"]
            .groupby(["player_name", "team"])
            .agg(clean_sheets=("clean_sheets", "sum"), rating=("rating", "mean"))
            .reset_index()
            .sort_values("clean_sheets", ascending=False)
            .head(15)
        )
        if gk_df.empty:
            st.info("ℹ️ No Goalkeeper data available in the current filter selection.")
        else:
            fig_gk = px.bar(
                gk_df,
                x="clean_sheets",
                y="player_name",
                orientation="h",
                color="team",
                text="clean_sheets",
                hover_data={"rating": ":.2f"},
                color_discrete_sequence=CHART_COLORS,
                labels={"clean_sheets": "Clean Sheets", "player_name": "Goalkeeper"},
            )
            fig_gk.update_traces(textposition="outside")
            fig_gk.update_layout(
                **PLOTLY_LAYOUT,
                title="Top 15 Goalkeepers by Clean Sheets",
                yaxis=dict(autorange="reversed", gridcolor=BORDER),
                height=400,
            )
            st.plotly_chart(fig_gk, use_container_width=True)

    st.markdown("---")

    # ── Position KPI Summary Cards ────────────────────────────────────────────
    st.markdown("<div class='section-header'>📊 Position KPI Summary</div>", unsafe_allow_html=True)
    pos_summary = (
        df.groupby("position")
        .agg(
            players=("player_name", "nunique"),
            avg_goals=("goals", "mean"),
            avg_assists=("assists", "mean"),
            avg_rating=("rating", "mean"),
            avg_pass_acc=("pass_accuracy", "mean"),
            avg_tackles=("tackles", "mean"),
        )
        .reset_index()
        .round(2)
    )
    # reorder to GK / DEF / MID / FWD if present
    pos_order = [p for p in ["GK", "DEF", "MID", "FWD"] if p in pos_summary["position"].values]
    pos_summary["position"] = pd.Categorical(pos_summary["position"], categories=pos_order, ordered=True)
    pos_summary = pos_summary.sort_values("position")

    st.dataframe(
        pos_summary.rename(columns={
            "position": "Position", "players": "Players",
            "avg_goals": "Avg Goals", "avg_assists": "Avg Assists",
            "avg_rating": "Avg Rating", "avg_pass_acc": "Avg Pass Acc %",
            "avg_tackles": "Avg Tackles",
        }).reset_index(drop=True),
        use_container_width=True,
        height=210,
    )


# ──────────────────────────────────────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────────────────────────────────────
def main():
    raw_df = load_data()
    filtered_df = render_sidebar(raw_df)

    st.sidebar.markdown("---")
    page = st.sidebar.radio(
        "Navigate",
        ["📊 Overview", "🔍 Player Analysis", "🏟 Team Analysis", "📐 Position Analysis"],
        label_visibility="collapsed",
    )

    if page == "📊 Overview":
        page_overview(filtered_df, raw_df)
    elif page == "🔍 Player Analysis":
        page_player_analysis(filtered_df)
    elif page == "🏟 Team Analysis":
        page_team_analysis(filtered_df)
    elif page == "📐 Position Analysis":
        page_position_analysis(filtered_df)

    # ── footer ────────────────────────────────────────────────────────────────
    st.markdown(
        f"""
        <hr style='border-color:{BORDER}; margin-top:40px;'>
        <div style='text-align:center; color:{TEXT_MUTED}; font-size:0.78rem; padding:8px 0 16px 0;'>
            ⚽ Football Analytics Dashboard &nbsp;|&nbsp;
            <span class='synthetic-badge'>⚠ SYNTHETIC DATA — not real-world statistics</span>
            &nbsp;|&nbsp; Built with Streamlit &amp; Plotly
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
