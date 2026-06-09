"""
Deal Screener - professional deal intelligence workbench.
"""

import json
import os
import re

import pandas as pd
import streamlit as st

from agents.screener import DealScreener
from settings_store import load_settings, save_settings


# Page configuration
st.set_page_config(
    page_title="Deal Screener",
    layout="wide",
    initial_sidebar_state="expanded",
)


# Professional visual system inspired by enterprise analytics dashboards.
st.markdown(
    """
<style>
    :root {
        --ds-bg: #f6f8fb;
        --ds-surface: #ffffff;
        --ds-surface-muted: #f8fafc;
        --ds-border: #d9e2ec;
        --ds-text: #102033;
        --ds-muted: #5f6f85;
        --ds-primary: #1f5eff;
        --ds-primary-dark: #1646bf;
        --ds-success: #157f3b;
        --ds-warning: #b7791f;
        --ds-danger: #b42318;
        --ds-shadow: 0 18px 45px rgba(16, 32, 51, 0.08);
    }

    .stApp {
        background: linear-gradient(180deg, #f8fbff 0%, var(--ds-bg) 100%);
        color: var(--ds-text);
    }

    section[data-testid="stSidebar"] {
        background: #0f172a;
        border-right: 1px solid rgba(255,255,255,0.08);
    }

    section[data-testid="stSidebar"] * {
        color: #e5edf8 !important;
    }

    section[data-testid="stSidebar"] .stAlert {
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.10);
    }

    .hero-card {
        background: radial-gradient(circle at top left, rgba(31,94,255,0.18), transparent 32%),
                    linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid rgba(255,255,255,0.14);
        border-radius: 24px;
        box-shadow: var(--ds-shadow);
        color: white;
        padding: 32px;
        margin: 8px 0 24px;
    }

    .hero-kicker {
        color: #93c5fd;
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.16em;
        margin-bottom: 12px;
        text-transform: uppercase;
    }

    .hero-card h1 {
        color: #ffffff;
        font-size: clamp(2rem, 5vw, 4rem);
        line-height: 0.98;
        margin: 0 0 16px;
    }

    .hero-card p {
        color: #cbd5e1;
        font-size: 1.05rem;
        max-width: 780px;
        margin-bottom: 0;
    }

    .workbench-card, .metric-card, .decision-card, .pipeline-card {
        background: var(--ds-surface);
        border: 1px solid var(--ds-border);
        border-radius: 18px;
        box-shadow: 0 12px 32px rgba(16, 32, 51, 0.06);
    }

    .workbench-card {
        padding: 24px;
        margin-bottom: 18px;
    }

    .metric-card {
        padding: 18px;
        min-height: 128px;
    }

    .metric-label {
        color: var(--ds-muted);
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .metric-value {
        color: var(--ds-text);
        font-size: 2rem;
        font-weight: 800;
        line-height: 1;
        margin: 12px 0 8px;
    }

    .metric-caption {
        color: var(--ds-muted);
        font-size: 0.9rem;
    }

    .decision-card {
        padding: 24px;
        border-left: 6px solid var(--decision-color, var(--ds-primary));
    }

    .decision-label {
        color: var(--decision-color, var(--ds-primary));
        font-size: 0.78rem;
        font-weight: 900;
        letter-spacing: 0.14em;
        text-transform: uppercase;
    }

    .decision-title {
        color: var(--ds-text);
        font-size: 2.25rem;
        font-weight: 900;
        margin: 8px 0;
    }

    .decision-meta {
        color: var(--ds-muted);
        font-size: 0.95rem;
        margin-top: 6px;
    }

    .score-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 14px;
        margin: 12px 0 24px;
    }

    .score-card {
        background: var(--ds-surface);
        border: 1px solid var(--ds-border);
        border-radius: 16px;
        padding: 16px;
    }

    .score-name {
        color: var(--ds-muted);
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .score-value {
        color: var(--ds-text);
        font-size: 1.7rem;
        font-weight: 850;
        margin: 10px 0;
    }

    .score-track {
        background: #e8eef6;
        border-radius: 999px;
        height: 9px;
        overflow: hidden;
    }

    .score-fill {
        background: var(--score-color, var(--ds-primary));
        border-radius: 999px;
        height: 100%;
    }

    .pipeline-card {
        padding: 18px;
    }

    .pipeline-step {
        align-items: center;
        border-bottom: 1px solid var(--ds-border);
        display: flex;
        gap: 14px;
        padding: 12px 0;
    }

    .pipeline-step:last-child {
        border-bottom: 0;
    }

    .step-number {
        align-items: center;
        background: #eaf1ff;
        border: 1px solid #c8d8ff;
        border-radius: 999px;
        color: var(--ds-primary-dark);
        display: inline-flex;
        flex: 0 0 34px;
        font-weight: 850;
        height: 34px;
        justify-content: center;
        width: 34px;
    }

    .step-title {
        color: var(--ds-text);
        font-weight: 800;
    }

    .step-caption {
        color: var(--ds-muted);
        font-size: 0.88rem;
    }

    .status-pill {
        border-radius: 999px;
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 850;
        letter-spacing: 0.08em;
        padding: 5px 10px;
        text-transform: uppercase;
    }

    .status-fast-track { background: #dcfce7; color: #14532d; }
    .status-review { background: #fef3c7; color: #78350f; }
    .status-pass { background: #fee2e2; color: #7f1d1d; }
    .status-neutral { background: #e2e8f0; color: #334155; }

    .stButton > button, .stDownloadButton > button {
        border-radius: 12px;
        font-weight: 800;
        transition: all 180ms ease;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 10px 20px rgba(16,32,51,0.12);
    }
</style>
""",
    unsafe_allow_html=True,
)


SCORE_LABELS = [
    ("Team", "team"),
    ("Market", "market"),
    ("Traction", "traction"),
    ("Product", "product"),
    ("Thesis Fit", "thesis_fit"),
    ("Deal Terms", "deal_terms"),
]

PIPELINE_STEPS = [
    ("Parse", "Extract text from PDF or manual input."),
    ("Extract", "Identify company, team, market, traction, and terms."),
    ("Enrich", "Add external web and trends context."),
    ("Score", "Evaluate the opportunity against fund criteria."),
    ("Summarize", "Produce an investment-ready executive summary."),
    ("Archive", "Save the screening record for portfolio analytics."),
]


def strip_emoji(text: str) -> str:
    return re.sub(r"[^\w\s/\-:&().]", "", str(text)).strip()


def clean_decision(decision: str) -> str:
    cleaned = strip_emoji(decision).upper()
    if "FAST" in cleaned:
        return "FAST TRACK"
    if "REVIEW" in cleaned:
        return "REVIEW"
    if "PASS" in cleaned:
        return "PASS"
    return cleaned or "UNKNOWN"


def decision_color(decision: str) -> str:
    label = clean_decision(decision)
    if label == "FAST TRACK":
        return "#157f3b"
    if label == "REVIEW":
        return "#b7791f"
    if label == "PASS":
        return "#b42318"
    return "#1f5eff"


def decision_class(decision: str) -> str:
    label = clean_decision(decision).lower().replace(" ", "-")
    return f"status-{label}" if label in {"fast-track", "review", "pass"} else "status-neutral"


def score_color(score: float) -> str:
    if score >= 7:
        return "#157f3b"
    if score >= 5:
        return "#b7791f"
    return "#b42318"


def load_deals() -> list[dict]:
    try:
        with open("data/deals.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def render_hero(title: str, subtitle: str, kicker: str = "AI Deal Intelligence") -> None:
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="hero-kicker">{kicker}</div>
            <h1>{title}</h1>
            <p>{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric(label: str, value: str, caption: str = "") -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_decision_card(results: dict) -> None:
    decision = results["decision"]
    scores = results["scores"]
    label = clean_decision(decision["decision"])
    color = decision_color(label)
    st.markdown(
        f"""
        <div class="decision-card" style="--decision-color: {color};">
            <div class="decision-label">Recommendation</div>
            <div class="decision-title">{label}</div>
            <div class="decision-meta"><strong>Next step:</strong> {decision['action']}</div>
            <div class="decision-meta"><strong>Company:</strong> {results.get('company_name', 'Unknown')}</div>
            <div class="decision-meta"><strong>Sector:</strong> {results.get('sector', 'Unknown')}</div>
            <div class="decision-meta"><strong>Composite score:</strong> {scores.get('composite', 0)}/10</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_score_grid(scores: dict) -> None:
    cards = []
    for label, key in SCORE_LABELS:
        value = float(scores.get(key, 0) or 0)
        width = max(0, min(100, value * 10))
        color = score_color(value)
        cards.append(
            f"""
            <div class="score-card">
                <div class="score-name">{label}</div>
                <div class="score-value">{value:g}/10</div>
                <div class="score-track"><div class="score-fill" style="--score-color: {color}; width: {width}%;"></div></div>
            </div>
            """
        )
    st.markdown(f"<div class=\"score-grid\">{''.join(cards)}</div>", unsafe_allow_html=True)


def render_pipeline_trace(active: bool = False) -> None:
    rows = []
    for index, (title, caption) in enumerate(PIPELINE_STEPS, start=1):
        rows.append(
            f"""
            <div class="pipeline-step">
                <div class="step-number">{index}</div>
                <div>
                    <div class="step-title">{title}</div>
                    <div class="step-caption">{caption}</div>
                </div>
            </div>
            """
        )
    status = "Live execution path" if active else "Screening architecture"
    st.markdown(
        f"""
        <div class="pipeline-card">
            <div class="metric-label">{status}</div>
            {''.join(rows)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def build_report(results: dict) -> str:
    decision = clean_decision(results["decision"]["decision"])
    scores = results["scores"]
    return f"""
# Deal Screening Report

## {results.get('company_name', 'Unknown Company')}

**Date:** {results.get('timestamp', 'N/A')}

**Decision:** {decision}

**Composite Score:** {scores.get('composite', 0)}/10

---

## Executive Summary
{results['stages'].get('summary', 'N/A')}

---

## Company Analysis
{results['stages'].get('extraction', 'N/A')}

---

## Scoring Details
{results['stages'].get('scoring', 'N/A')}

---

## Web Research
{results['stages'].get('enrichment', 'N/A')}
"""


def render_results(results: dict) -> None:
    scores = results["scores"]
    deck_fields = results["stages"].get("parsing", {}).get("key_fields", {})

    st.markdown("---")
    left, right = st.columns([1.7, 1])
    with left:
        render_decision_card(results)
    with right:
        render_metric("Composite Score", f"{scores.get('composite', 0)}/10", "Weighted investment score")

    st.markdown("### Scorecard")
    render_score_grid(scores)

    quality_cols = st.columns(4)
    with quality_cols[0]:
        render_metric("Pages Parsed", str(deck_fields.get("page_count", "N/A")), "Deck structure signal")
    with quality_cols[1]:
        render_metric("Traction Evidence", "Yes" if deck_fields.get("has_traction") else "No", "Detected in deck text")
    with quality_cols[2]:
        render_metric("Team Evidence", "Yes" if deck_fields.get("has_team_slide") else "No", "Detected in deck text")
    with quality_cols[3]:
        render_metric("Market Evidence", "Yes" if deck_fields.get("has_market_size") else "No", "Detected in deck text")

    st.markdown("### Analysis Workbench")
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Investment Memo",
        "Extracted Signals",
        "Scoring Rationale",
        "Research Context",
        "Confidence Trace",
        "Communication",
    ])

    with tab1:
        st.markdown(results["stages"].get("summary", "No summary available."))

    with tab2:
        st.markdown(results["stages"].get("extraction", "No extraction available."))

    with tab3:
        st.markdown(results["stages"].get("scoring", "No scoring available."))

    with tab4:
        st.markdown(results["stages"].get("enrichment", "No enrichment data available."))

    with tab5:
        confidence_rows = results.get("confidence", [])
        if confidence_rows:
            st.dataframe(pd.DataFrame(confidence_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No confidence trace was produced for this analysis.")

    with tab6:
        if "decline_email" in results["stages"]:
            st.markdown(results["stages"]["decline_email"])
            if st.button("Show email as plain text"):
                st.code(results["stages"]["decline_email"])
        else:
            st.info("No decline email is required for this recommendation.")

    full_report = build_report(results)
    st.download_button(
        label="Download investment report",
        data=full_report,
        file_name=f"{results.get('company_name', 'deal').replace(' ', '_')}_report.md",
        mime="text/markdown",
        use_container_width=True,
    )


def prepare_history_dataframe(deals: list[dict]) -> pd.DataFrame:
    df = pd.DataFrame(deals)
    if df.empty:
        return df
    df["composite"] = df["scores"].apply(lambda s: s.get("composite") if isinstance(s, dict) else None)
    df["date"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["decision_bucket"] = df["decision"].apply(clean_decision)
    return df


# Sidebar
with st.sidebar:
    st.title("Deal Screener")
    st.caption("AI-native investment screening")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["Screen New Deal", "Deal History", "Settings"],
        index=0,
    )

    st.markdown("---")
    app_settings = load_settings()
    st.markdown("### Fund Thesis")
    st.info(app_settings["fund_config"]["thesis"])

    st.markdown("### Quick Stats")
    st.metric("Deals Screened", len(load_deals()))


# Page 1: Screen New Deal
if page == "Screen New Deal":
    render_hero(
        "Deal intelligence workbench",
        "Convert pitch decks into structured investment memos, source-aware signals, scoring rationale, and a clear partner-ready recommendation.",
    )

    input_col, trace_col = st.columns([1.35, 1])
    with input_col:
        st.markdown("### New Screening")
        uploaded_file = st.file_uploader(
            "Upload pitch deck PDF",
            type=["pdf"],
            help="Upload a startup pitch deck in PDF format.",
        )

        with st.expander("Paste deck content manually"):
            manual_text = st.text_area(
                "Deck content",
                placeholder="Copy and paste text from the pitch deck.",
                height=260,
            )

        with st.expander("Additional deal context"):
            st.text_area(
                "Notes",
                placeholder="Example: referred by a partner, met at a conference, or prior founder touchpoint.",
                height=100,
            )
            st.selectbox(
                "Deal source",
                ["Inbound Email", "Referral", "Conference", "Cold Outreach", "AngelList", "Other"],
            )

        has_input = uploaded_file or (manual_text and len(manual_text) > 50)
        if uploaded_file:
            st.success(f"Uploaded {uploaded_file.name} ({round(uploaded_file.size / 1024, 1)} KB).")
        if manual_text and len(manual_text) > 50:
            st.success(f"Manual text provided ({len(manual_text)} characters).")

    with trace_col:
        st.markdown("### Screening Architecture")
        render_pipeline_trace()

    if has_input:
        if st.button("Screen this deal", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(message, percent):
                status_text.markdown(f"**{strip_emoji(message)}**")
                progress_bar.progress(percent)

            screener = DealScreener()
            with st.spinner("Running full analysis..."):
                results = screener.screen_deal(
                    uploaded_file,
                    manual_text=manual_text if manual_text and len(manual_text) > 50 else None,
                    progress_callback=update_progress,
                )

            progress_bar.empty()
            status_text.empty()

            if results["status"] == "error":
                st.error(f"Error: {results.get('error', 'Unknown error')}")
            else:
                render_results(results)


# Page 2: Deal History
elif page == "Deal History":
    render_hero(
        "Deal history and analytics",
        "Review screened companies, compare decision quality, and monitor how the pipeline changes over time.",
        kicker="Portfolio Intelligence",
    )

    deals = load_deals()
    if not deals:
        st.info("No deals have been screened yet. Screen a deal to populate the analytics workspace.")
    else:
        df = prepare_history_dataframe(deals)
        st.markdown("### Filters")
        filter_cols = st.columns(3)
        with filter_cols[0]:
            all_sectors = sorted(df["sector"].dropna().unique().tolist())
            selected_sectors = st.multiselect("Sector", all_sectors, default=all_sectors)
        with filter_cols[1]:
            all_decisions = sorted(df["decision_bucket"].dropna().unique().tolist())
            selected_decisions = st.multiselect("Decision", all_decisions, default=all_decisions)
        with filter_cols[2]:
            valid_dates = df["date"].dropna()
            if valid_dates.empty:
                date_range = None
            else:
                date_range = st.date_input("Date Range", (valid_dates.min().date(), valid_dates.max().date()))

        filtered_df = df[
            df["sector"].isin(selected_sectors)
            & df["decision_bucket"].isin(selected_decisions)
        ]

        if date_range and len(date_range) == 2:
            start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            filtered_df = filtered_df[
                (filtered_df["date"] >= start_date)
                & (filtered_df["date"] <= end_date + pd.Timedelta(days=1))
            ]

        metric_cols = st.columns(4)
        with metric_cols[0]:
            render_metric("Total Deals", str(len(filtered_df)), "Filtered records")
        with metric_cols[1]:
            render_metric("Fast Track", str((filtered_df["decision_bucket"] == "FAST TRACK").sum()), "High conviction")
        with metric_cols[2]:
            render_metric("Review", str((filtered_df["decision_bucket"] == "REVIEW").sum()), "Needs diligence")
        with metric_cols[3]:
            render_metric("Pass", str((filtered_df["decision_bucket"] == "PASS").sum()), "Below threshold")

        st.markdown("### Analytics")
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            st.markdown("**Decision Distribution**")
            st.bar_chart(filtered_df["decision_bucket"].value_counts())
        with chart_col2:
            st.markdown("**Average Composite Score by Sector**")
            sector_avg = filtered_df.dropna(subset=["composite"]).groupby("sector")["composite"].mean().sort_values(ascending=False)
            if not sector_avg.empty:
                st.bar_chart(sector_avg)
            else:
                st.info("No composite score data available for selected filters.")

        trend_df = filtered_df.dropna(subset=["date", "composite"]).copy()
        if not trend_df.empty:
            trend_df["month"] = trend_df["date"].dt.to_period("M").dt.to_timestamp()
            monthly_scores = trend_df.groupby("month")["composite"].mean()
            st.markdown("**Average Composite Score Trend (Monthly)**")
            st.line_chart(monthly_scores)
        else:
            st.info("Not enough data to plot score trends.")

        st.markdown("### Deal Records")
        for deal in reversed(filtered_df.to_dict("records")):
            decision = clean_decision(deal.get("decision", "Unknown"))
            status = decision_class(decision)
            header = (
                f"<span class='status-pill {status}'>{decision}</span> "
                f"<strong>{deal.get('company_name', 'Unknown')}</strong> "
                f"Score: {deal.get('scores', {}).get('composite', 'N/A')}/10 "
                f"Date: {str(deal.get('timestamp', 'N/A'))[:10]}"
            )
            with st.expander(strip_emoji(f"{decision} | {deal.get('company_name', 'Unknown')} | Score: {deal.get('scores', {}).get('composite', 'N/A')}/10")):
                st.markdown(header, unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Company:** {deal.get('company_name', 'Unknown')}")
                    st.markdown(f"**Sector:** {deal.get('sector', 'Unknown')}")
                    st.markdown(f"**Date:** {str(deal.get('timestamp', 'N/A'))[:10]}")
                with col2:
                    deal_scores = deal.get("scores", {})
                    st.markdown(f"**Team:** {deal_scores.get('team', 'N/A')}/10")
                    st.markdown(f"**Market:** {deal_scores.get('market', 'N/A')}/10")
                    st.markdown(f"**Traction:** {deal_scores.get('traction', 'N/A')}/10")
                    st.markdown(f"**Product:** {deal_scores.get('product', 'N/A')}/10")

        if st.button("Clear all history", type="secondary"):
            with open("data/deals.json", "w", encoding="utf-8") as f:
                json.dump([], f)
            st.success("History cleared.")
            st.rerun()


# Page 3: Settings
elif page == "Settings":
    render_hero(
        "Fund configuration",
        "Tune thesis, scoring weights, and decision thresholds so recommendations reflect your investment strategy.",
        kicker="Operating Model",
    )

    settings = load_settings()
    fund_config = settings["fund_config"]
    scoring_criteria = settings["scoring_criteria"]
    thresholds = settings["thresholds"]

    st.markdown("### Fund Thesis")
    fund_config["name"] = st.text_input("Fund Name", value=fund_config.get("name", ""))
    fund_config["thesis"] = st.text_area("Fund Thesis", value=fund_config.get("thesis", ""), height=120)

    st.markdown("### Investment Focus")
    stage_focus = ", ".join(fund_config.get("stage_focus", []))
    fund_config["stage_focus"] = [s.strip() for s in st.text_input("Stage Focus", value=stage_focus).split(",") if s.strip()]

    sectors_in = ", ".join(fund_config.get("sectors_of_interest", []))
    fund_config["sectors_of_interest"] = [s.strip() for s in st.text_area("Sectors of Interest", value=sectors_in, height=100).split(",") if s.strip()]

    sectors_out = ", ".join(fund_config.get("sectors_to_avoid", []))
    fund_config["sectors_to_avoid"] = [s.strip() for s in st.text_area("Sectors to Avoid", value=sectors_out, height=100).split(",") if s.strip()]

    st.markdown("### Scoring Weights")
    for criterion, details in scoring_criteria.items():
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"**{criterion.replace('_', ' ').title()}**")
        with col2:
            details["weight"] = st.slider(
                f"{criterion}_weight",
                min_value=0.0,
                max_value=1.0,
                value=float(details.get("weight", 0)),
                step=0.01,
                label_visibility="collapsed",
            )
            st.caption(f"Weight: {details['weight'] * 100:.0f}% - {details['description']}")

    st.markdown("### Decision Thresholds")
    thresholds["fast_track"] = st.slider("Fast Track threshold", 0.0, 10.0, float(thresholds["fast_track"]), 0.1)
    thresholds["review"] = st.slider("Review threshold", 0.0, 10.0, float(thresholds["review"]), 0.1)
    st.markdown(f"- **Pass:** Score < {thresholds['review']}/10")

    total_weight = sum(c.get("weight", 0) for c in scoring_criteria.values())
    if abs(total_weight - 1.0) > 0.01:
        st.warning(f"Scoring weights currently sum to {total_weight:.2f}. Recommended total is 1.00.")
    else:
        st.success("Scoring weights sum to 1.00.")

    if st.button("Save settings", type="primary"):
        save_settings({
            "fund_config": fund_config,
            "scoring_criteria": scoring_criteria,
            "thresholds": thresholds,
        })
        st.success("Settings saved to data/settings.json")

    st.markdown("### API Status")
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        st.success(f"Groq API key configured (ends in ...{groq_key[-4:]}).")
    else:
        st.error("Groq API key not found. Check your .env file.")
