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
# Helpers
# -----------------------------
def severity_label(score: float) -> str:
    if score >= 0.80:
        return "Critical"
    if score >= 0.60:
        return "High"
    if score >= 0.35:
        return "Medium"
    if score > 0.0:
        return "Low"
    return "None"

def badge_for_category(cat: str) -> str:
    mapping = {
        "scam_fraud": "💸 Scam / Fraud",
        "sexual_content": "🔞 Sexual Content",
        "child_safety": "🧒 Child Safety",
        "hate_harassment": "🧨 Hate / Harassment",
    }
    return mapping.get(cat, cat)

# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="SentinelAI — Content Safety Analyzer",
    page_icon="🛡️",
    layout="centered",
)

st.title("🛡️ SentinelAI — Content Safety Analyzer")
st.caption(
    "Portfolio demo: paste a social media post (or use a demo example) to generate risk findings and trigger warnings."
)

# -----------------------------
# Sidebar: About + controls
# -----------------------------
with st.sidebar:
    st.header("About")
    st.write(
        "- Hybrid-style moderation pipeline (rules + scoring)\n"
        "- Generates trigger warnings + severity score\n"
        "- Designed for social media safety demos\n"
    )
    locale = st.selectbox("Locale", ["en"], index=0)
    show_debug = st.toggle("Show debug / explainability", value=False)

# -----------------------------
# Demo examples
# -----------------------------
st.subheader("Try demo social media posts")
d1, d2, d3, d4 = st.columns(4)

if d1.button("🚨 Scam"):
    st.session_state["demo_text"] = (
        "URGENT: Your bank account will be closed today! Verify immediately and "
        "send a $200 gift card to restore access."
    )
if d2.button("⚠️ Sexual"):
    st.session_state["demo_text"] = (
        "Hey 😉 DM me for private pics and exclusive content tonight."
    )
if d3.button("🧒 Child safety"):
    st.session_state["demo_text"] = (
        "I'm 16 and an older guy keeps asking me to meet privately."
    )
if d4.button("✅ Safe"):
    st.session_state["demo_text"] = (
        "Just finished a great workout and enjoyed coffee with friends!"
    )

default_text = st.session_state.get("demo_text", "")

# -----------------------------
# Input
# -----------------------------
text = st.text_area(
    "Paste a social media post:",
    value=default_text,
    height=180,
    placeholder="Type your text here or click a demo example above...",
)

colA, colB = st.columns([1, 2])
with colA:
    analyze = st.button("Analyze", type="primary")
with colB:
    st.caption("Tip: Use the demo buttons above to quickly test the system.")

# -----------------------------
# Run analysis
# -----------------------------
if analyze:
    if not text.strip():
        st.warning("Please enter some text to analyze.")
        st.stop()

    with st.spinner("Analyzing..."):
        result = run_pipeline(text, locale)

    st.divider()

    # -----------------------------
    # Summary
    # -----------------------------
    st.subheader("Summary")

    score = float(result.get("overall_severity", 0.0))
    safe = bool(result.get("safe_to_show", True))

    s1, s2, s3 = st.columns(3)
    s1.metric("Safe to show", "✅ Yes" if safe else "⚠️ No")
    s2.metric("Severity", f"{score:.2f}")
    s3.metric("Risk level", severity_label(score))

    st.progress(min(max(score, 0.0), 1.0))

    # -----------------------------
    # Trigger warnings
    # -----------------------------
    st.subheader("Trigger warnings")
    tw = result.get("trigger_warnings", [])
    if tw:
        for w in tw:
            st.warning(w)
    else:
        st.success("No trigger warnings detected.")

    # -----------------------------
    # Category badges
    # -----------------------------
    findings = result.get("findings", [])
    st.subheader("Detected categories")

    if findings:
        cats = sorted({f.get("category", "unknown") for f in findings})
        st.write(" ".join([f"`{badge_for_category(c)}`" for c in cats]))
    else:
        st.write("No categories flagged.")

    # -----------------------------
    # Detailed findings (explainability)
    # -----------------------------
    st.subheader("Detailed findings")
    if findings:
        for f in findings:
            cat = f.get("category", "unknown")
            sev = float(f.get("severity", 0.0))
            reasons = f.get("reasons", [])
            with st.expander(f"{badge_for_category(cat)} — severity {sev:.2f}", expanded=True):
                st.write(f"**Reasons:** `{', '.join(reasons) if reasons else 'n/a'}`")
                st.write(
                    "This category was flagged by rule-based heuristics designed to detect common patterns."
                )
    else:
        st.write("No findings.")

    # -----------------------------
    # Debug panel
    # -----------------------------
    if show_debug:
        st.subheader("Debug / explainability")
        st.json(result)

st.divider()
st.caption("SentinelAI • Content Safety Analyzer • Streamlit portfolio demo")
