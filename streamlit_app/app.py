import sys
from pathlib import Path
import streamlit as st

# --------------------------------------------------
# Fix imports so Streamlit can find backend code
# --------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"

sys.path.insert(0, str(BACKEND))

from app.pipeline.policy import run_pipeline

# --------------------------------------------------
# Streamlit Page Setup
# --------------------------------------------------
st.set_page_config(
    page_title="SentinelAI — Content Safety Analyzer",
    page_icon="🛡️",
    layout="centered"
)

# --------------------------------------------------
# UI Header
# --------------------------------------------------
st.title("🛡️ SentinelAI — Content Safety Analyzer")
st.write(
    """
Hybrid AI moderation system that analyzes social media text and generates
trigger warnings using rule-based heuristics and a local NLP model.
"""
)

# --------------------------------------------------
# Input Area
# --------------------------------------------------
text = st.text_area(
    "Paste a social media post:",
    height=180,
    placeholder="Example: URGENT verify your account now and send gift card..."
)

col1, col2 = st.columns([1, 1])

with col1:
    analyze = st.button("Analyze", type="primary")

with col2:
    show_debug = st.toggle("Show debug info", value=False)

# --------------------------------------------------
# Analysis Logic
# --------------------------------------------------
if analyze:

    if not text.strip():
        st.warning("Please enter some text to analyze.")
        st.stop()

    with st.spinner("Analyzing content..."):
        result = run_pipeline(text, "en")

    # --------------------------------------------------
    # Results Section
    # --------------------------------------------------
    st.divider()
    st.subheader("Results")

    c1, c2 = st.columns(2)

    with c1:
        st.metric(
            "Safe to Show",
            "✅ Yes" if result.safe_to_show else "⚠️ No"
        )

    with c2:
        st.metric(
            "Overall Severity",
            f"{result.overall_severity:.2f}"
        )

    # --------------------------------------------------
    # Trigger Warnings
    # --------------------------------------------------
    st.subheader("Trigger Warnings")

    if result.trigger_warnings:
        for warning in result.trigger_warnings:
            st.warning(warning)
    else:
        st.success("No trigger warnings detected.")

    # --------------------------------------------------
    # Detailed Findings
    # --------------------------------------------------
    st.subheader("Detected Categories")

    if result.findings:
        for finding in result.findings:
            st.write(
                f"""
**Category:** {finding.category}  
**Severity:** {finding.severity:.2f}  
**Reasons:** `{', '.join(finding.reasons)}`
"""
            )
    else:
        st.write("No risks detected.")

    # --------------------------------------------------
    # Debug Section (optional)
    # --------------------------------------------------
    if show_debug:
        st.subheader("Debug Information")
        st.json(result.debug or {})

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.divider()
st.caption("SentinelAI • Hybrid AI Content Moderation Prototype")
