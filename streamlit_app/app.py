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
# Page config
# -----------------------------
st.set_page_config(
    page_title="SentinelAI — Content Safety Analyzer",
    page_icon="🛡️",
    layout="centered",
)

st.title("🛡️ SentinelAI — Content Safety Analyzer")
st.write(
    "Hybrid content safety analyzer for social media text. "
    "Flags scam/fraud cues, sexual solicitation cues, and child-safety risk cues, "
    "then generates trigger warnings with severity scoring."
)

# -----------------------------
# Demo examples
# -----------------------------
st.caption("Quick examples:")
c1, c2, c3, c4 = st.columns(4)

if c1.button("Scam"):
    st.session_state["demo_text"] = "URGENT: Verify your account now or it will be closed. Pay with gift card."
if c2.button("Sexual"):
    st.session_state["demo_text"] = "DM for nudes now"
if c3.button("Child safety"):
    st.session_state["demo_text"] = "I'm 16 and older men keep messaging me"
if c4.button("Safe"):
    st.session_state["demo_text"] = "Normal post about coffee and a walk."

default_text = st.session_state.get("demo_text", "")

text = st.text_area(
    "Paste a social media post:",
    value=default_text,
    height=180,
    placeholder="Example: URGENT verify your account now and send gift card...",
)

colA, colB = st.columns([1, 1])
with colA:
    analyze = st.button("Analyze", type="primary")
with colB:
    show_debug = st.toggle("Show debug info", value=False)

# -----------------------------
# Run analysis
# -----------------------------
if analyze:
    if not text.strip():
        st.warning("Please enter some text to analyze.")
        st.stop()

    with st.spinner("Analyzing..."):
        result = run_pipeline(text, "en")

    st.divider()
    st.subheader("Results")

    m1, m2 = st.columns(2)
    m1.metric("Safe to show", "✅ Yes" if result["safe_to_show"] else "⚠️ No")
    m2.metric("Overall severity", f'{result["overall_severity"]:.2f}')

    st.subheader("Trigger warnings")
    if result["trigger_warnings"]:
        for w in result["trigger_warnings"]:
            st.warning(w)
    else:
        st.success("No trigger warnings detected.")

    st.subheader("Findings")
    if result["findings"]:
        for f in result["findings"]:
            st.write(
                f'**{f["category"]}** — severity **{f["severity"]:.2f}** — reasons: `{", ".join(f["reasons"])}`'
            )
    else:
        st.write("No findings.")

    if show_debug:
        st.subheader("Debug")
        st.json(result.get("debug", {}))

st.divider()
st.caption("SentinelAI • Portfolio demo • Rule-based moderation pipeline (Streamlit Cloud friendly)")
