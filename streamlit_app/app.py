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


def categories_line(findings) -> str:
    if not findings:
        return "—"
    cats = sorted({(f or {}).get("category", "unknown") for f in findings})
    return " · ".join([badge(c) for c in cats]) if cats else "—"


# -----------------------------
# Page setup (Recruiter-friendly)
# -----------------------------
st.set_page_config(
    page_title="SentinelAI — Content Safety Analyzer",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ SentinelAI — Content Safety Analyzer")
st.caption(
    
)

INSTAGRAM_LINK = "https://www.instagram.com/reel/DVaFCuqDQEx/?igsh=cXphdTg5aTRlcDZm"

# Demo feed data (no scraping; simulated captions/comments)
FEED_POSTS = [
    {
        "id": "ig_demo",
        "source": "Instagram Reel",
        "link": INSTAGRAM_LINK,
        "text": "Demo link included. Open the reel and paste any caption/comment text here to analyze.",
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
# Sidebar controls
# -----------------------------
with st.sidebar:
    st.header("Demo mode")
    mode = st.radio("Choose a mode", ["Live Feed Mode", "Single Post Analyzer"], index=0)

    st.divider()
    st.header("Options")
    locale = st.selectbox("Locale", ["en"], index=0)
    show_debug = st.toggle("Show debug output", value=False)

    auto_refresh = False
    refresh_seconds = 6
    if mode == "Live Feed Mode":
        auto_refresh = st.toggle("Auto-refresh feed", value=False)
        refresh_seconds = st.slider("Refresh every (seconds)", 3, 15, 6)

# -----------------------------
# SINGLE POST ANALYZER
# -----------------------------
if mode == "Single Post Analyzer":
    st.subheader("Single Post Analyzer")
    st.markdown(f"🔗 Demo Instagram Reel: [Open link]({INSTAGRAM_LINK})")

    d1, d2, d3, d4 = st.columns(4)
    if d1.button("🚨 Scam"):
        st.session_state["single_text"] = FEED_POSTS[1]["text"]
    if d2.button("🔞 Sexual"):
        st.session_state["single_text"] = FEED_POSTS[2]["text"]
    if d3.button("🧒 Child safety"):
        st.session_state["single_text"] = FEED_POSTS[3]["text"]
    if d4.button("✅ Safe"):
        st.session_state["single_text"] = FEED_POSTS[4]["text"]

    text = st.text_area(
        "Paste a social media post:",
        value=st.session_state.get("single_text", ""),
        height=200,
        placeholder="Paste caption/comment/message here...",
    )

    if st.button("Analyze", type="primary"):
        if not text.strip():
            st.warning("Please enter some text.")
            st.stop()

        result = run_pipeline(text, locale)

        score = float(result.get("overall_severity", 0.0))
        safe = bool(result.get("safe_to_show", True))

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("Safe to show", "✅ Yes" if safe else "⚠️ No")
        c2.metric("Severity", f"{score:.2f}")
        c3.metric("Risk level", risk_level(score))
        st.progress(min(max(score, 0.0), 1.0))

        st.subheader("Trigger warnings")
        for w in (result.get("trigger_warnings") or []):
            st.warning(w)
        if not (result.get("trigger_warnings") or []):
            st.success("No trigger warnings detected.")

        st.subheader("Findings")
        findings = result.get("findings") or []
        if findings:
            for f in findings:
                cat = (f or {}).get("category", "unknown")
                sev = float((f or {}).get("severity", 0.0))
                reasons = (f or {}).get("reasons", [])
                with st.expander(f"{badge(cat)} — severity {sev:.2f}", expanded=True):
                    st.write("Reasons:", ", ".join(reasons) if reasons else "—")
        else:
            st.write("No findings.")

        if show_debug:
            st.subheader("Debug")
            st.json(result)

# -----------------------------
# LIVE FEED MODE
# -----------------------------
else:
    st.subheader("Live Feed Mode — Moderation Dashboard")
    st.write(
        "This simulates a Trust & Safety moderation dashboard: a feed of posts is analyzed and labeled with "
        "severity, categories, and trigger warnings."
    )
    st.markdown(f"🔗 Instagram reel included in feed: [Open link]({INSTAGRAM_LINK})")

    if "feed_tick" not in st.session_state:
        st.session_state["feed_tick"] = 0

    if auto_refresh:
        time.sleep(refresh_seconds)
        st.session_state["feed_tick"] += 1
        st.rerun()

    left, right = st.columns([2, 1], gap="large")

    with left:
        st.caption("Feed")
        for post in FEED_POSTS:
            result = run_pipeline(post.get("text", ""), locale)

            score = float(result.get("overall_severity", 0.0))
            safe = bool(result.get("safe_to_show", True))
            findings = result.get("findings") or []

            status = "✅ SAFE" if safe else "⛔ BLOCK"
            level = risk_level(score)
            cats = categories_line(findings)

            with st.container(border=True):
                top = st.columns([2, 1, 1])
                top[0].markdown(f"**{post.get('source','Post')}**")
                top[1].markdown(f"**{status}**")
                top[2].markdown(f"**{level}**")

                st.progress(min(max(score, 0.0), 1.0))
                st.write(post.get("text", ""))
                st.caption(f"Categories: {cats}")

                if post.get("link"):
                    st.markdown(f"🔗 Link: [Open post]({post['link']})")

                if st.button(f"Inspect → {post['id']}", key=f"inspect_{post['id']}"):
                    st.session_state["selected_post"] = post
                    st.session_state["selected_result"] = result

    with right:
        st.caption("Inspector")
        selected = st.session_state.get("selected_post")
        selected_result = st.session_state.get("selected_result")

        if not selected:
            st.info("Click **Inspect** on any post to view full trigger warnings and reasons.")
        else:
            st.markdown(f"### {selected.get('source','Post')} — Details")
            if selected.get("link"):
                st.markdown(f"🔗 [Open post]({selected['link']})")

            score = float((selected_result or {}).get("overall_severity", 0.0))
            safe = bool((selected_result or {}).get("safe_to_show", True))
            findings = (selected_result or {}).get("findings") or []

            st.metric("Safe to show", "✅ Yes" if safe else "⚠️ No")
            st.metric("Severity", f"{score:.2f}")
            st.metric("Risk level", risk_level(score))
            st.progress(min(max(score, 0.0), 1.0))

            st.subheader("Trigger warnings")
            tw = (selected_result or {}).get("trigger_warnings") or []
            if tw:
                for w in tw:
                    st.warning(w)
            else:
                st.success("No trigger warnings detected.")

            st.subheader("Findings")
            if findings:
                for f in findings:
                    cat = (f or {}).get("category", "unknown")
                    sev = float((f or {}).get("severity", 0.0))
                    reasons = (f or {}).get("reasons", [])
                    with st.expander(f"{badge(cat)} — {sev:.2f}", expanded=True):
                        st.write("Reasons:", ", ".join(reasons) if reasons else "—")
            else:
                st.write("No findings.")

            if show_debug:
                st.subheader("Debug")
                st.json(selected_result or {})

st.divider()
st.caption("SentinelAI • Live moderation dashboard demo • Streamlit portfolio project")
