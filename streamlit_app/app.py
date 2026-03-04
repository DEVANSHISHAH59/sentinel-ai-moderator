import sys
from pathlib import Path
from datetime import datetime, timedelta
import re
import time

import numpy as np
import pandas as pd
import streamlit as st
import altair as alt
import matplotlib.pyplot as plt

# Import backend
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.pipeline.policy import run_pipeline


# ---------------- HELPERS ----------------
def risk_level(score: float) -> str:
    # score expected 0..1
    if score >= 0.8:
        return "Critical"
    if score >= 0.6:
        return "High"
    if score >= 0.35:
        return "Medium"
    if score > 0:
        return "Low"
    return "None"


def decision_from(score: float, safe_to_show: bool) -> str:
    # Simple moderation decision policy
    if not safe_to_show or score >= 0.75:
        return "Remove"
    if score >= 0.40:
        return "Review"
    return "Allow"


def badge(cat: str) -> str:
    return {
        "scam_fraud": "💸 Scam/Fraud",
        "sexual_content": "🔞 Sexual",
        "child_safety": "🧒 Child Safety",
    }.get(cat, cat)


def normalize_policy_label(category: str) -> str:
    # Map backend categories to dashboard labels
    mapping = {
        "scam_fraud": "Scam/Fraud",
        "sexual_content": "Sexual Content",
        "child_safety": "Child Safety",
    }
    return mapping.get(category, "Other")


def extract_top_policy(result: dict) -> str:
    findings = result.get("findings", []) or []
    if not findings:
        return "Benign"
    # pick max severity finding
    top = max(findings, key=lambda x: float(x.get("severity", 0.0)))
    cat = str(top.get("category", "Other"))
    return normalize_policy_label(cat)


def ensure_event_store():
    if "events" not in st.session_state:
        st.session_state["events"] = []  # list[dict]


def log_event(text: str, locale: str, source: str, link: str | None, result: dict):
    ensure_event_store()

    score = float(result.get("overall_severity", 0.0) or 0.0)
    safe = bool(result.get("safe_to_show", True))
    pol = extract_top_policy(result)
    sev = risk_level(score)
    dec = decision_from(score, safe)

    st.session_state["events"].append(
        {
            "timestamp": datetime.utcnow(),
            "source": source,
            "link": link or "",
            "language": locale,
            "policy_label": pol,
            "risk_score": score,
            "severity": sev,
            "decision": dec,
            "safe_to_show": safe,
            "text": text,
        }
    )


def get_events_df() -> pd.DataFrame:
    ensure_event_store()
    if not st.session_state["events"]:
        return pd.DataFrame(
            columns=[
                "timestamp",
                "source",
                "link",
                "language",
                "policy_label",
                "risk_score",
                "severity",
                "decision",
                "safe_to_show",
                "text",
            ]
        )
    df = pd.DataFrame(st.session_state["events"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    return df


def seed_sample_events_if_empty(locale: str = "en"):
    """
    Seed the dashboard with sample events once, so it never looks empty.
    It uses your FEED_POSTS + some synthetic timestamps.
    """
    ensure_event_store()
    if st.session_state["events"]:
        return

    now = datetime.utcnow()
    # Add your feed posts first
    for i, post in enumerate(FEED_POSTS):
        result = run_pipeline(post["text"], locale)
        # stagger timestamps across last few days
        ts = now - timedelta(hours=6 * i)
        score = float(result.get("overall_severity", 0.0) or 0.0)
        safe = bool(result.get("safe_to_show", True))
        pol = extract_top_policy(result)
        sev = risk_level(score)
        dec = decision_from(score, safe)

        st.session_state["events"].append(
            {
                "timestamp": ts,
                "source": post.get("source", "Feed"),
                "link": post.get("link", "") or "",
                "language": locale,
                "policy_label": pol,
                "risk_score": score,
                "severity": sev,
                "decision": dec,
                "safe_to_show": safe,
                "text": post["text"],
            }
        )

    # Add synthetic events to make charts more interesting
    rng = np.random.default_rng(7)
    policy_labels = ["Benign", "Scam/Fraud", "Sexual Content", "Child Safety", "Other"]
    sources = ["Instagram", "Comment", "DM", "Caption"]
    for _ in range(120):
        pol = rng.choice(policy_labels, p=[0.45, 0.18, 0.10, 0.07, 0.20])
        base = float(rng.normal(0.18, 0.12))
        bump = {"Benign": 0.0, "Scam/Fraud": 0.45, "Sexual Content": 0.35, "Child Safety": 0.55, "Other": 0.25}[pol]
        score = float(np.clip(base + bump + rng.normal(0, 0.05), 0, 1))
        sev = risk_level(score)
        safe = True if score < 0.65 else False
        dec = decision_from(score, safe)

        ts = now - timedelta(hours=int(rng.integers(0, 24 * 14)))  # last 14 days
        st.session_state["events"].append(
            {
                "timestamp": ts,
                "source": str(rng.choice(sources)),
                "link": "",
                "language": locale,
                "policy_label": pol,
                "risk_score": score,
                "severity": sev,
                "decision": dec,
                "safe_to_show": safe,
                "text": f"Sample content related to {pol.lower()}...",
            }
        )


# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="SentinelAI — Content Safety Analyzer",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ SentinelAI — Content Safety Analyzer")
st.caption("Hybrid AI moderation prototype + Safety Analytics Dashboard")

INSTAGRAM_LINK = "https://www.instagram.com/reel/DVaFCuqDQEx/?igsh=cXphdTg5aTRlcDZm"

# ---------------- DEMO POSTS ----------------
FEED_POSTS = [
    {
        "id": "ig_demo",
        "source": "Instagram Reel",
        "link": INSTAGRAM_LINK,
        "text": "Demo Instagram reel — open link and analyze caption text.",
    },
    {
        "id": "p1",
        "source": "Instagram",
        "text": "URGENT verify your account now and send a gift card.",
    },
    {
        "id": "p2",
        "source": "Instagram",
        "text": "DM me for private pics tonight 😉",
    },
    {
        "id": "p3",
        "source": "Instagram",
        "text": "I'm 16 and someone keeps asking me to meet privately.",
    },
    {
        "id": "p4",
        "source": "Instagram",
        "text": "Beautiful morning run today!",
    },
]

# ---------------- SIDEBAR ----------------
st.sidebar.header("Navigation")

mode = st.sidebar.radio(
    "Mode",
    ["Single Post Analyzer", "Live Feed Mode", "Safety Dashboard"],
)

locale = st.sidebar.selectbox("Language/Locale", ["en", "hi", "ne", "fr"], index=0)
show_debug = st.sidebar.toggle("Show debug output", False)

st.sidebar.divider()
if st.sidebar.button("Reset dashboard data"):
    st.session_state.pop("events", None)
    st.toast("Dashboard data cleared. Open Safety Dashboard to reseed.", icon="🧹")


# ---------------- SINGLE ANALYZER ----------------
if mode == "Single Post Analyzer":
    st.subheader("Analyze a post")
    st.markdown(f"🔗 Demo Instagram Reel: [Open link]({INSTAGRAM_LINK})")

    text = st.text_area(
        "Paste social media text",
        height=200,
        placeholder="Paste caption/comment/message here..."
    )

    if st.button("Analyze", type="primary"):
        if not text.strip():
            st.warning("Please paste some text to analyze.")
        else:
            with st.spinner("Running moderation pipeline..."):
                result = run_pipeline(text, locale)

            # Log this run so it appears in the Safety Dashboard
            log_event(text=text, locale=locale, source="Single Analyzer", link="", result=result)

            score = float(result.get("overall_severity", 0.0) or 0.0)
            safe = bool(result.get("safe_to_show", True))

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Decision", decision_from(score, safe))
            c2.metric("Safe to show", "✅ Yes" if safe else "⚠️ No")
            c3.metric("Severity score", f"{score:.2f}")
            c4.metric("Risk level", risk_level(score))

            st.progress(score)

            st.subheader("Trigger warnings")
            tw = result.get("trigger_warnings", []) or []
            if not tw:
                st.info("No trigger warnings.")
            else:
                for w in tw:
                    st.warning(w)

            st.subheader("Findings")
            findings = result.get("findings", []) or []
            if not findings:
                st.success("No policy findings. Content appears benign.")
            else:
                for fnd in findings:
                    cat = fnd.get("category", "Other")
                    sev = float(fnd.get("severity", 0.0) or 0.0)
                    with st.expander(f"{badge(cat)} — severity {sev:.2f}"):
                        st.write(", ".join(fnd.get("reasons", []) or []))

            if show_debug:
                st.json(result)

# ---------------- LIVE FEED ----------------
elif mode == "Live Feed Mode":
    st.subheader("Live Moderation Feed")
    st.caption("Each feed item you run gets added to the Safety Dashboard automatically.")

    for post in FEED_POSTS:
        with st.container(border=True):
            st.write(post["text"])

            colA, colB = st.columns([1, 1])
            with colA:
                if post.get("link"):
                    st.markdown(f"🔗 [Open post]({post['link']})")
            with colB:
                run = st.button(f"Analyze '{post['id']}'", key=f"an_{post['id']}")

            if run:
                with st.spinner("Running moderation pipeline..."):
                    result = run_pipeline(post["text"], locale)
                log_event(
                    text=post["text"],
                    locale=locale,
                    source=post.get("source", "Feed"),
                    link=post.get("link", ""),
                    result=result,
                )
                score = float(result.get("overall_severity", 0.0) or 0.0)
                st.progress(score)
                st.caption(f"Decision: {decision_from(score, bool(result.get('safe_to_show', True)))} • Risk: {risk_level(score)}")

                if show_debug:
                    st.json(result)

    st.info("Tip: Open **Safety Dashboard** to see analytics from your runs.")

# ---------------- SAFETY DASHBOARD ----------------
else:
    st.subheader("Safety Analytics Dashboard")
    st.caption("This dashboard summarizes moderation results (session data + seeded samples).")

    # Ensure we always have something to show
    seed_sample_events_if_empty(locale=locale)
    df = get_events_df()

    # ---- Filters
    st.sidebar.subheader("Dashboard Filters")

    if df.empty:
        st.warning("No moderation events available.")
        st.stop()

    df_local = df.copy()
    df_local["date"] = df_local["timestamp"].dt.tz_convert("UTC").dt.date

    min_date = df_local["date"].min()
    max_date = df_local["date"].max()
    date_range = st.sidebar.date_input("Date range", [min_date, max_date])

    sources = ["All"] + sorted(df_local["source"].dropna().unique().tolist())
    src = st.sidebar.selectbox("Source", sources)

    languages = ["All"] + sorted(df_local["language"].dropna().unique().tolist())
    lang = st.sidebar.selectbox("Language", languages)

    labels = ["All"] + sorted(df_local["policy_label"].dropna().unique().tolist())
    label = st.sidebar.selectbox("Policy label", labels)

    severities = ["All"] + sorted(df_local["severity"].dropna().unique().tolist())
    sev = st.sidebar.selectbox("Severity", severities)

    decisions = ["All"] + sorted(df_local["decision"].dropna().unique().tolist())
    dec = st.sidebar.selectbox("Decision", decisions)

    # Apply filters
    start = pd.to_datetime(date_range[0])
    end = pd.to_datetime(date_range[1]) + pd.Timedelta(days=1)

    f = df_local[(df_local["timestamp"].dt.tz_convert("UTC") >= start.tz_localize("UTC")) &
                 (df_local["timestamp"].dt.tz_convert("UTC") < end.tz_localize("UTC"))]

    if src != "All":
        f = f[f["source"] == src]
    if lang != "All":
        f = f[f["language"] == lang]
    if label != "All":
        f = f[f["policy_label"] == label]
    if sev != "All":
        f = f[f["severity"] == sev]
    if dec != "All":
        f = f[f["decision"] == dec]

    # ---- KPI Row
    total = len(f)
    flagged = int(f["decision"].isin(["Review", "Remove"]).sum())
    removed = int((f["decision"] == "Remove").sum())
    avg_risk = float(f["risk_score"].mean()) if total else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Items analyzed", f"{total:,}")
    c2.metric("% Flagged (Review+Remove)", f"{(flagged/total*100 if total else 0):.1f}%")
    c3.metric("% Removed", f"{(removed/total*100 if total else 0):.1f}%")
    c4.metric("Avg risk score", f"{avg_risk:.2f}")

    st.divider()

    # ---- Charts layout
    left, right = st.columns([1.2, 1])

    # Bar: violation categories
    with left:
        st.markdown("### Violation categories")
        vc = f["policy_label"].value_counts().reset_index()
        vc.columns = ["policy_label", "count"]
        bar = (
            alt.Chart(vc)
            .mark_bar()
            .encode(
                x=alt.X("policy_label:N", sort="-y", title="Policy label"),
                y=alt.Y("count:Q", title="Count"),
                tooltip=["policy_label", "count"],
            )
            .properties(height=320)
        )
        st.altair_chart(bar, use_container_width=True)

    # Pie-ish: moderation decisions (Altair arc)
    with right:
        st.markdown("### Moderation decisions")
        dc = f["decision"].value_counts().reset_index()
        dc.columns = ["decision", "count"]
        pie = (
            alt.Chart(dc)
            .mark_arc()
            .encode(
                theta="count:Q",
                color="decision:N",
                tooltip=["decision", "count"],
            )
            .properties(height=320)
        )
        st.altair_chart(pie, use_container_width=True)

    # Heatmap: policy label vs severity
    st.markdown("### Risk severity heatmap")
    pivot = pd.crosstab(f["policy_label"], f["severity"]).reset_index().melt(
        id_vars="policy_label", var_name="severity", value_name="count"
    )
    heat = (
        alt.Chart(pivot)
        .mark_rect()
        .encode(
            x=alt.X("severity:N", title="Severity"),
            y=alt.Y("policy_label:N", title="Policy label"),
            color=alt.Color("count:Q"),
            tooltip=["policy_label", "severity", "count"],
        )
        .properties(height=260)
    )
    st.altair_chart(heat, use_container_width=True)

    # Timeline: abuse trends over time (stacked or multi-line)
    st.markdown("### Abuse trends over time")
    trend = f.copy()
    trend["date"] = trend["timestamp"].dt.tz_convert("UTC").dt.date
    trend = trend.groupby(["date", "policy_label"]).size().reset_index(name="count")

    line = (
        alt.Chart(trend)
        .mark_line(point=True)
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("count:Q", title="Count"),
            color="policy_label:N",
            tooltip=["date", "policy_label", "count"],
        )
        .properties(height=300)
    )
    st.altair_chart(line, use_container_width=True)

    # Word cloud: common toxic phrases (optional)
    st.markdown("### Common phrases in flagged content")
    flagged_text = " ".join(f.loc[f["decision"].isin(["Review", "Remove"]), "text"].astype(str).tolist()).strip()

    if not flagged_text:
        st.info("No flagged content available for the current filter selection.")
    else:
        try:
            from wordcloud import WordCloud

            wc = WordCloud(width=1200, height=450).generate(flagged_text)
            fig, ax = plt.subplots(figsize=(12, 4))
            ax.imshow(wc, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        except Exception:
            st.info("Install `wordcloud` to enable the word cloud visualization (optional).")

    st.divider()

    # Review queue table
    st.markdown("### Review queue")
    queue = f[f["decision"].isin(["Review", "Remove"])].sort_values(["risk_score"], ascending=False)
    st.dataframe(
        queue[["timestamp", "source", "language", "policy_label", "severity", "risk_score", "decision", "text"]].head(50),
        use_container_width=True,
        hide_index=True,
    )

    with st.expander("See raw dashboard data"):
        st.dataframe(f.sort_values("timestamp", ascending=False), use_container_width=True, hide_index=True)
