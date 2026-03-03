import sys
from pathlib import Path
import streamlit as st

# -----------------------------
# Import backend pipeline
# -----------------------------
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.pipeline.policy import run_pipeline  # noqa

# -----------------------------
# Page setup
# -----------------------------
st.set_page_config(
    page_title="SentinelAI — Content Safety Analyzer",
    page_icon="🛡️",
    layout="centered",
)

st.title("🛡️ SentinelAI — Content Safety Analyzer")

st.caption(
    "AI-powered trigger warning system for social media moderation. "
    "Paste a post or try a real demo example below."
)

# -----------------------------
# Instagram Demo Section ⭐
# -----------------------------
st.subheader("📱 Real Social Media Demo")

INSTAGRAM_LINK = "https://www.instagram.com/reel/DVaFCuqDQEx/?igsh=cXphdTg5aTRlcDZm"

st.markdown(
    f"""
🔗 **Demo Instagram Reel**

👉 [Open Instagram Reel]({INSTAGRAM_LINK})

This demo simulates analyzing captions/comments from a real social media post.
"""
)

if st.button("Load Instagram Demo Example"):
    st.session_state["demo_text"] = (
        "URGENT announcement! Limited time offer — verify your account now "
        "or it will be permanently closed. Send confirmation immediately."
    )

st.divider()

# -----------------------------
# Other demo buttons
# -----------------------------
st.subheader("Quick Demo Examples")

c1, c2, c3 = st.columns(3)

if c1.button("🚨 Scam Post"):
    st.session_state["demo_text"] = (
        "Your account will be closed today! Send a gift card immediately."
    )

if c2.button("🔞 Sexual Content"):
    st.session_state["demo_text"] = (
        "DM me for private pics and exclusive content tonight 😉"
    )

if c3.button("🧒 Child Safety Risk"):
    st.session_state["demo_text"] = (
        "I'm 16 and someone older keeps asking me to meet privately."
    )

default_text = st.session_state.get("demo_text", "")

# -----------------------------
# Input area
# -----------------------------
text = st.text_area(
    "Paste a social media post:",
    value=default_text,
    height=180,
    placeholder="Paste caption, comment, or message here...",
)

show_debug = st.toggle("Show debug info")

# -----------------------------
# Analyze button
# -----------------------------
if st.button("Analyze", type="primary"):

    if not text.strip():
        st.warning("Please enter text.")
        st.stop()

    result = run_pipeline(text)

    st.divider()
    st.subheader("📊 Analysis Result")

    score = result["overall_severity"]
    safe = result["safe_to_show"]

    col1, col2, col3 = st.columns(3)

    col1.metric("Safe to show", "✅ Yes" if safe else "⚠️ No")
    col2.metric("Severity Score", f"{score:.2f}")

    level = (
        "Critical" if score >= 0.8 else
        "High" if score >= 0.6 else
        "Medium" if score >= 0.35 else
        "Low"
    )

    col3.metric("Risk Level", level)

    st.progress(score)

    # -----------------------------
    # Warnings
    # -----------------------------
    st.subheader("⚠️ Trigger Warnings")

    if result["trigger_warnings"]:
        for w in result["trigger_warnings"]:
            st.warning(w)
    else:
        st.success("No warnings detected.")

    # -----------------------------
    # Findings
    # -----------------------------
    st.subheader("🔎 Detailed Findings")

    for f in result["findings"]:
        with st.expander(f"{f['category']} — severity {f['severity']:.2f}"):
            st.write("Reasons:", ", ".join(f["reasons"]))

    # -----------------------------
    # Debug panel
    # -----------------------------
    if show_debug:
        st.subheader("Debug Output")
        st.json(result)

st.divider()
st.caption("SentinelAI • AI Content Moderation Portfolio Project")
