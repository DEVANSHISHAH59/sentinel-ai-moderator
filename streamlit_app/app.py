import sys
from pathlib import Path
import time
import streamlit as st

# -----------------------------
# Import backend pipeline
# -----------------------------
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.pipeline.policy import run_pipeline  # noqa

# -----------------------------
# Helpers
# -----------------------------
def risk_level(score: float) -> str:
    if score >= 0.80:
        return "Critical"
    if score >= 0.60:
        return "High"
    if score >= 0.35:
        return "Medium"
    if score > 0:
        return "Low"
    return "None"

def badge(cat: str) -> str:
    m = {
        "scam_fraud": "💸 Scam/Fraud",
        "sexual_content": "🔞 Sexual",
        "child_safety": "🧒 Child Safety",
        "hate_harassment": "🧨 Hate/Harassment",
    }
    return m.get(cat, cat)

def summarize_categories(findings):
    cats = sorted({f.get("category", "unknown") for f in findings})
    return " · ".join([badge(c) for c in cats]) if cats else "—"

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="SentinelAI — Content Safety Analyzer",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ SentinelAI — Content Safety Analyzer")
st.caption(
    "Recruiter demo: a content moderation pipeline that flags risky social media text and produces trigger warnings."
)

# -----------------------------
# Sidebar controls
# -----------------------------
with st.sidebar:
    st.header("Modes")
    mode = st.radio("Choose a mode", ["Single Post Analyzer", "Live Feed Mode"], index=1)

    st.divider()
    st.header("Settings")
    locale = st.selectbox("Locale", ["en"], index=0)
    show_debug = st.toggle("Show debug / raw output", value=False)

    if mode == "Live Feed Mode":
        auto_refresh = st.toggle("Auto-refresh feed", value=False)
        refresh_seconds = st.slider("Refresh every (seconds)", 3, 15, 6)

# -----------------------------
# Demo data (safe + risky)
# -----------------------------
INSTAGRAM_LINK = "https://www.instagram.com/reel/DVaFCuqDQEx/?igsh=cXphdTg5aTRlcDZm"

FEED_POSTS = [
    {
        "id": "ig1",
        "source": "Instagram Reel",
        "link": INSTAGRAM_LINK,
        "text": "Demo: recruiter can open the reel link above. (This app analyzes text you paste or simulated captions.)",
    },
    {
        "id": "p1",
        "source": "Instagram",
        "link": None,
        "text": "URGENT: Verify your account now or it will be closed. Send a gift card immediately.",
    },
    {
        "id": "p2",
        "source": "Instagram",
        "link": None,
        "text": "Hey 😉 DM me for private pics and exclusive content tonight.",
    },
    {
        "id": "p3",
        "source": "Instagram",
        "link": None,
        "text": "I'm 16 and an older guy keeps asking me to meet privately.",
    },
    {
        "id": "p4",
        "source": "Instagram",
        "link": None,
        "text": "Just finished a run and grabbed coffee. Great day!",
    },
    {
        "id": "p5",
        "source": "Instagram",
        "link": None,
        "text": "Final notice: act now. Your account will be closed if you don't verify today.",
    },
]

# -----------------------------
# SINGLE POST ANALYZER
# -----------------------------
if mode == "Single Post Analyzer":
    st.subheader("Single Post Analyzer")

    demo_col1, demo_col2, demo_col3, demo_col4 = st.columns(4)
    if demo_col1.button("🚨 Scam"):
        st.session_state["single_text"] = FEED_POSTS[1]["text"]
    if demo_col2.button("🔞 Sexual"):
        st.session_state["single_text"] = FEED_POSTS[2]["text"]
    if demo_col3.button("🧒 Child safety"):
        st.session_state["single_text"] = FEED_POSTS[3]["text"]
    if demo_col4.button("✅ Safe"):
        st.session_state["single_text"] = FEED_POSTS[4]["text"]

    st.markdown(f"🔗 Optional demo reel: [Open Instagram Reel]({INSTAGRAM_LINK})")

    text = st.text_area(
        "Paste a social media post:",
        value=st.session_state.get("single_text", ""),
        height=180,
        placeholder="Paste caption/comment/message here..."
    )

    if st.button("Analyze", type="primary"):
        if not text.strip():
            st.warning("Please enter text.")
            st.stop()

        result = run_pipeline(text, locale)
        st.divider()

        score = float(result["overall_severity"])
        safe = bool(result["safe_to_show"])

        c1, c2, c3 = st.columns(3)
        c1.metric("Safe to show", "✅ Yes" if safe else "⚠️ No")
        c2.metric("Severity", f"{score:.2f}")
        c3.metric("Risk level", risk_level(score))
        st.progress(min(max(score, 0.0), 1.0))

        st.subheader("Trigger warnings")
        if result["trigger_warnings"]:
            for w in result["trigger_warnings"]:
                st.warning(w)
        else:
            st.success("No trigger warnings detected.")

        st.subheader("Findings")
        if result["findings"]:
            for f in result["findings"]:
                with st.expander(f"{badge(f['category'])} — severity {f['severity']:.2f}", expanded=True):
                    st.write("Reasons:", ", ".join(f.get("reasons", [])) or "—")
        else:
            st.write("No findings.")

        if show_debug:
            st.subheader("Debug output")
            st.json(result)

# -----------------------------
# LIVE FEED MODE (Recruiter dashboard)
# -----------------------------
else:
    st.subheader("Live Feed Mode — Moderation Dashboard")
    st.write(
        "This simulates a Trust & Safety moderation view: a feed of posts is analyzed and labeled with severity, "
        "categories, and trigger warnings."
    )
    st.markdown(f"🔗 Demo reel link included in feed: [Open Instagram Reel]({INSTAGRAM_LINK})")

    left, right = st.columns([2, 1], gap="large")

    # Auto refresh option
    if "feed_tick" not in st.session_state:
        st.session_state["feed_tick"] = 0

    if auto_refresh:
        time.sleep(refresh_seconds)
        st.session_state["feed_tick"] += 1
        st.rerun()

    with left:
        st.caption("Feed")
        for post in FEED_POSTS:
            # Analyze each post (skip the IG link item if it has no meaningful text)
            analysis_text = post["text"]
            result = run_pipeline(analysis_text, locale)
            score = float(result["overall_severity"])
            safe = bool(result["safe_to_show"])
            cats = summarize_categories(result.get("findings", []))

            status = "✅ SAFE" if safe else "⛔ BLOCK"
            level = risk_level(score)

            with st.container(border=True):
                top = st.columns([2, 1, 1])
                top[0].markdown(f"**{post['source']}**")
                top[1].markdown(f"**{status}**")
                top[2].markdown(f"**{level}**")

                st.progress(min(max(score, 0.0), 1.0))
                st.write(post["text"])
                st.caption(f"Categories: {cats}")

                if post["link"]:
                    st.markdown(f"🔗 Link: [Open post]({post['link']})")

                # Select post for detail view
                if st.button(f"Inspect details → {post['id']}", key=f"inspect_{post['id']}"):
                    st.session_state["selected_post"] = post
                    st.session_state["selected_result"] = result

    with right:
        st.caption("Inspector")
        selected = st.session_state.get("selected_post")
        selected_result = st.session_state.get("selected_result")

        if not selected:
            st.info("Click **Inspect details** on any post to view full warnings and reasons.")
        else:
            st.markdown(f"### {selected['source']} — Details")
            if selected.get("link"):
                st.markdown(f"🔗 [Open post]({selected['link']})")

            score = float(selected_result["overall_severity"])
            safe = bool(selected_result["safe_to_show"])

            st.metric("Safe to show", "✅ Yes" if safe else "⚠️ No")
            st.metric("Severity", f"{score:.2f}")
            st.progress(min(max(score, 0.0), 1.0))

            st.subheader("Trigger warnings")
            if selected_result["trigger_warnings"]:
                for w in selected_result["trigger_warnings"]:
                    st.warning(w)
            else:
                st.success("No trigger warnings detected.")

            st.subheader("Findings")
            if selected_result["findings"]:
                for f in selected_result["findings"]:
                    with st.expander(f"{badge(f['category'])} — {f['severity']:.2f}", expanded=True):
                        st.write("Reasons:", ", ".join(f.get("reasons", [])) or "—")
            else:
                st.write("No findings.")

            if show_debug:
                st.subheader("Debug output")
                st.json(selected_result)

st.divider()
st.caption("SentinelAI • Live moderation dashboard demo • Streamlit portfolio app")
