"""
Deal Screener - Deal Screening Web App
"""

import streamlit as st
import json
import os
import pandas as pd
from agents.screener import DealScreener
from settings_store import load_settings, save_settings


# ── Page Config ──────────────────────────────────────────
st.set_page_config(
    page_title="Deal Screener",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    .big-score {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
    }
    .metric-box {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 5px;
    }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ──────────────────────────────────────────────
with st.sidebar:
    st.title("🏦 Deal Screener")
    st.markdown("---")

    page = st.radio(
        "Navigation",
        ["📊 Screen New Deal", "📁 Deal History", "⚙️ Settings"],
        index=0
    )

    st.markdown("---")
    app_settings = load_settings()
    st.markdown("### Fund Thesis")
    st.info(app_settings["fund_config"]["thesis"])

    st.markdown("### Quick Stats")
    try:
        with open("data/deals.json", "r") as f:
            deals = json.load(f)
        st.metric("Deals Screened", len(deals))
    except (FileNotFoundError, json.JSONDecodeError):
        st.metric("Deals Screened", 0)


# ── Page 1: Screen New Deal ──────────────────────────────
if page == "📊 Screen New Deal":

    st.title("📊 Deal Screening")
    st.markdown("Upload a pitch deck to get an instant AI-powered analysis.")

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload Pitch Deck (PDF)",
        type=["pdf"],
        help="Upload a startup's pitch deck in PDF format"
    )

    # Manual text input as backup
    with st.expander("📋 Or Paste Deck Content Manually"):
        manual_text = st.text_area(
            "Paste pitch deck text here",
            placeholder="Copy and paste the content from your pitch deck...",
            height=300
        )

    # Optional context
    with st.expander("➕ Add Additional Context (Optional)"):
        additional_notes = st.text_area(
            "Notes",
            placeholder="e.g., Referred by John from Sequoia, "
                        "met at TechCrunch Disrupt...",
            height=100
        )
        source = st.selectbox(
            "Deal Source",
            ["Inbound Email", "Referral", "Conference",
             "Cold Outreach", "AngelList", "Other"]
        )

    has_input = uploaded_file or (manual_text and len(manual_text) > 50)

    if uploaded_file:
        st.success(f"✅ Uploaded: {uploaded_file.name} "
                   f"({round(uploaded_file.size/1024, 1)} KB)")

    if manual_text and len(manual_text) > 50:
        st.success(f"✅ Manual text provided ({len(manual_text)} characters)")

    if has_input:
        if st.button("🚀 Screen This Deal", type="primary", use_container_width=True):

            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()

            def update_progress(message, percent):
                status_text.markdown(f"**{message}**")
                progress_bar.progress(percent)

            # Run screening
            screener = DealScreener()

            with st.spinner("Running full analysis..."):
                results = screener.screen_deal(
                    uploaded_file,
                    manual_text=manual_text if manual_text and len(manual_text) > 50 else None,
                    progress_callback=update_progress
                )

            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()

            if results["status"] == "error":
                st.error(f"❌ Error: {results.get('error', 'Unknown error')}")
            else:
                # ── Display Results ──────────────────────
                decision = results["decision"]
                scores = results["scores"]

                st.markdown("---")

                # ── Decision Banner ──────────────────────
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown(f"## {decision['decision']}")
                    st.markdown(f"**Next Step:** {decision['action']}")
                    st.markdown(f"**Company:** {results.get('company_name', 'Unknown')}")
                    st.markdown(f"**Sector:** {results.get('sector', 'Unknown')}")

                with col2:
                    st.markdown("### Composite Score")
                    st.markdown(
                        f"<div class='big-score'>{scores['composite']}/10</div>",
                        unsafe_allow_html=True
                    )

                with col3:
                    deck_fields = results["stages"].get("parsing", {}).get("key_fields", {})
                    st.markdown("### Deck Quality")
                    st.metric("Pages", deck_fields.get("page_count", "N/A"))
                    has_traction = "✅" if deck_fields.get("has_traction") else "❌"
                    has_team = "✅" if deck_fields.get("has_team_slide") else "❌"
                    st.markdown(f"Traction Slide: {has_traction}")
                    st.markdown(f"Team Slide: {has_team}")

                st.markdown("---")

                # ── Score Breakdown ──────────────────────
                st.markdown("### 📊 Score Breakdown")

                score_cols = st.columns(6)
                score_labels = [
                    ("🧑‍💼 Team", "team"),
                    ("📈 Market", "market"),
                    ("🚀 Traction", "traction"),
                    ("💡 Product", "product"),
                    ("🎯 Thesis Fit", "thesis_fit"),
                    ("💰 Deal Terms", "deal_terms"),
                ]

                for col, (label, key) in zip(score_cols, score_labels):
                    with col:
                        score_val = scores.get(key, 0)
                        if score_val >= 7:
                            color = "🟢"
                        elif score_val >= 5:
                            color = "🟡"
                        else:
                            color = "🔴"
                        st.metric(label, f"{score_val}/10")
                        st.markdown(f"<center>{color}</center>", unsafe_allow_html=True)

                st.markdown("---")

                # ── Detailed Analysis Tabs ───────────────
                st.markdown("### 📋 Detailed Analysis")

                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📝 Summary",
                    "🔍 Full Extraction",
                    "📊 Scoring Details",
                    "🌐 Web Research",
                    "✉️ Decline Email"
                ])

                with tab1:
                    st.markdown(results["stages"].get("summary", "No summary available."))

                with tab2:
                    st.markdown(results["stages"].get("extraction", "No extraction available."))
                    confidence_rows = results.get("confidence", [])
                    if confidence_rows:
                        st.markdown("#### Source-Aware Confidence")
                        st.dataframe(
                            pd.DataFrame(confidence_rows),
                            use_container_width=True,
                            hide_index=True
                        )

                with tab3:
                    st.markdown(results["stages"].get("scoring", "No scoring available."))

                with tab4:
                    st.markdown(results["stages"].get("enrichment", "No enrichment data available."))

                with tab5:
                    if "decline_email" in results["stages"]:
                        st.markdown(results["stages"]["decline_email"])
                        if st.button("📋 Copy Email"):
                            st.code(results["stages"]["decline_email"])
                    else:
                        st.info("No decline email needed — deal was not passed.")

                # ── Download Full Report ─────────────────
                st.markdown("---")
                full_report = f"""
# Deal Screening Report
## {results.get('company_name', 'Unknown Company')}
**Date:** {results.get('timestamp', 'N/A')}
**Decision:** {decision['decision']}
**Composite Score:** {scores['composite']}/10

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
                st.download_button(
                    label="📥 Download Full Report (Markdown)",
                    data=full_report,
                    file_name=f"screening_{results.get('company_name', 'deal')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )


# ── Page 2: Deal History ─────────────────────────────────
elif page == "📁 Deal History":

    st.title("📁 Deal History")
    st.markdown("All previously screened deals.")

    try:
        with open("data/deals.json", "r") as f:
            deals = json.load(f)

        if not deals:
            st.info("No deals screened yet. Go screen your first deal! 🚀")
        else:
            history_df = pd.DataFrame(deals)
            history_df["date"] = pd.to_datetime(history_df["timestamp"], errors="coerce")
            history_df["decision_bucket"] = history_df["decision"].fillna("Unknown").apply(
                lambda v: "FAST TRACK" if "FAST TRACK" in v else ("REVIEW" if "REVIEW" in v else ("PASS" if "PASS" in v else "Unknown"))
            )
            history_df["composite"] = history_df["scores"].apply(
                lambda s: s.get("composite") if isinstance(s, dict) else None
            )

            st.markdown("### Filters")
            all_sectors = sorted([s for s in history_df["sector"].dropna().unique().tolist() if s])
            selected_sectors = st.multiselect("Sector", all_sectors, default=all_sectors)
            selected_decisions = st.multiselect(
                "Decision",
                ["FAST TRACK", "REVIEW", "PASS", "Unknown"],
                default=["FAST TRACK", "REVIEW", "PASS", "Unknown"]
            )
            min_date = history_df["date"].min().date() if history_df["date"].notna().any() else None
            max_date = history_df["date"].max().date() if history_df["date"].notna().any() else None
            date_range = None
            if min_date and max_date:
                date_range = st.date_input("Date Range", (min_date, max_date))

            filtered_df = history_df[
                history_df["decision_bucket"].isin(selected_decisions) &
                (
                    history_df["sector"].isin(selected_sectors)
                    if selected_sectors else True
                )
            ]
            if date_range and len(date_range) == 2:
                start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
                filtered_df = filtered_df[
                    (filtered_df["date"] >= start) & (filtered_df["date"] <= end)
                ]

            # Summary stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Deals", len(filtered_df))
            with col2:
                fast_track = sum(1 for d in filtered_df.to_dict("records") if "FAST TRACK" in d.get("decision", ""))
                st.metric("🟢 Fast Track", fast_track)
            with col3:
                review = sum(1 for d in filtered_df.to_dict("records") if "REVIEW" in d.get("decision", ""))
                st.metric("🟡 Review", review)
            with col4:
                passed = sum(1 for d in filtered_df.to_dict("records") if "PASS" in d.get("decision", ""))
                st.metric("🔴 Passed", passed)

            st.markdown("---")
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

            st.markdown("---")

            # Deal table
            for i, deal in enumerate(reversed(filtered_df.to_dict("records"))):
                with st.expander(
                    f"{deal.get('decision', '❓')} | "
                    f"{deal.get('company_name', 'Unknown')} | "
                    f"Score: {deal.get('scores', {}).get('composite', 'N/A')}/10 | "
                    f"{deal.get('timestamp', 'N/A')[:10]}"
                ):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Company:** {deal.get('company_name', 'Unknown')}")
                        st.markdown(f"**Sector:** {deal.get('sector', 'Unknown')}")
                        st.markdown(f"**Date:** {deal.get('timestamp', 'N/A')[:10]}")
                    with col2:
                        scores = deal.get("scores", {})
                        st.markdown(f"**Team:** {scores.get('team', 'N/A')}/10")
                        st.markdown(f"**Market:** {scores.get('market', 'N/A')}/10")
                        st.markdown(f"**Traction:** {scores.get('traction', 'N/A')}/10")
                        st.markdown(f"**Product:** {scores.get('product', 'N/A')}/10")

            st.markdown("---")

            # Clear history button
            if st.button("🗑️ Clear All History", type="secondary"):
                with open("data/deals.json", "w") as f:
                    json.dump([], f)
                st.success("History cleared!")
                st.rerun()

    except (FileNotFoundError, json.JSONDecodeError):
        st.info("No deals screened yet. Go screen your first deal! 🚀")


# ── Page 3: Settings ─────────────────────────────────────
elif page == "⚙️ Settings":

    st.title("⚙️ Settings")

    st.markdown("### Fund Configuration")

    settings = load_settings()
    fund_config = settings["fund_config"]
    scoring_criteria = settings["scoring_criteria"]
    thresholds = settings["thresholds"]

    st.markdown("#### Editable Fund Thesis")
    fund_config["name"] = st.text_input("Fund Name", value=fund_config.get("name", ""))
    fund_config["thesis"] = st.text_area("Fund Thesis", value=fund_config.get("thesis", ""), height=120)

    st.markdown("#### Editable Stage Focus")
    stage_focus = ", ".join(fund_config.get("stage_focus", []))
    fund_config["stage_focus"] = [s.strip() for s in st.text_input("Stage Focus (comma separated)", value=stage_focus).split(",") if s.strip()]

    sectors_in = ", ".join(fund_config.get("sectors_of_interest", []))
    fund_config["sectors_of_interest"] = [s.strip() for s in st.text_area("Sectors of Interest (comma separated)", value=sectors_in, height=100).split(",") if s.strip()]

    sectors_out = ", ".join(fund_config.get("sectors_to_avoid", []))
    fund_config["sectors_to_avoid"] = [s.strip() for s in st.text_area("Sectors to Avoid (comma separated)", value=sectors_out, height=100).split(",") if s.strip()]

    st.markdown("---")

    st.markdown("### Editable Scoring Weights")
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
                label_visibility="collapsed"
            )
            st.caption(f"Weight: {details['weight']*100:.0f}% — {details['description']}")

    st.markdown("---")

    st.markdown("### Decision Thresholds")
    thresholds["fast_track"] = st.slider("Fast Track threshold", 0.0, 10.0, float(thresholds["fast_track"]), 0.1)
    thresholds["review"] = st.slider("Review threshold", 0.0, 10.0, float(thresholds["review"]), 0.1)
    st.markdown(f"- 🔴 **Pass:** Score < {thresholds['review']}/10")

    total_weight = sum(c.get("weight", 0) for c in scoring_criteria.values())
    if abs(total_weight - 1.0) > 0.01:
        st.warning(f"Scoring weights currently sum to {total_weight:.2f}. Recommended total is 1.00.")
    else:
        st.success("Scoring weights sum to 1.00.")

    if st.button("💾 Save Settings", type="primary"):
        save_settings({
            "fund_config": fund_config,
            "scoring_criteria": scoring_criteria,
            "thresholds": thresholds
        })
        st.success("Settings saved to data/settings.json")

    st.markdown("---")

    st.markdown("### API Status")
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        st.success(f"✅ Groq API Key configured (ends in ...{groq_key[-4:]})")
    else:
        st.error("❌ Groq API Key not found. Check your .env file.")

    st.markdown("---")
    st.caption("To modify fund criteria, edit config.py and restart the app.")
