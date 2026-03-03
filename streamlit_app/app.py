import sys
from pathlib import Path
import time
import streamlit as st

# Import backend
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.pipeline.policy import run_pipeline


def risk_level(score: float) -> str:
    if score >= 0.8:
        return "Critical"
    if score >= 0.6:
        return "High"
    if score >= 0.35:
        return "Medium"
    if score > 0:
        return "Low"
    return "None"


def badge(cat: str) -> str:
    return {
        "scam_fraud": "💸 Scam/Fraud",
        "sexual_content": "🔞 Sexual",
        "child_safety": "🧒 Child Safety",
    }.get(cat, cat)


# ---------------- PAGE ----------------
st.set_page_config(
    page_title="SentinelAI — Content Safety Analyzer",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ SentinelAI — Content Safety Analyzer")

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
mode = st.sidebar.radio(
    "Mode",
    ["Live Feed Mode", "Single Post Analyzer"]
)

locale = "en"
show_debug = st.sidebar.toggle("Show debug output", False)

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

        result = run_pipeline(text, locale)

        score = result.get("overall_severity", 0.0)
        safe = result.get("safe_to_show", True)

        c1, c2, c3 = st.columns(3)
        c1.metric("Safe", "✅ Yes" if safe else "⚠️ No")
        c2.metric("Severity", f"{score:.2f}")
        c3.metric("Risk", risk_level(score))

        st.progress(score)

        st.subheader("Trigger warnings")
        for w in result.get("trigger_warnings", []):
            st.warning(w)

        st.subheader("Findings")
        for f in result.get("findings", []):
            with st.expander(f"{badge(f['category'])} — {f['severity']:.2f}"):
                st.write(", ".join(f.get("reasons", [])))

        if show_debug:
            st.json(result)

# ---------------- LIVE FEED ----------------
else:

    st.subheader("Live Moderation Feed")

    for post in FEED_POSTS:

        result = run_pipeline(post["text"], locale)
        score = result.get("overall_severity", 0.0)

        with st.container(border=True):
            st.write(post["text"])
            st.progress(score)

            if post.get("link"):
                st.markdown(f"🔗 [Open post]({post['link']})")

            st.caption(f"Risk: {risk_level(score)}")


            
