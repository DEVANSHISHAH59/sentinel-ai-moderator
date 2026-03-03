import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
sys.path.append(str(BACKEND))

from app.pipeline.policy import run_pipeline  # noqa

st.set_page_config(page_title="SentinelAI — Content Safety", page_icon="🛡️")

st.title("🛡️ SentinelAI — Content Safety Analyzer")
st.write("Paste a social media post. The app flags risky categories and suggests trigger warnings.")

text = st.text_area("Post text", height=180, placeholder="Paste text here...")

run = st.button("Analyze", type="primary")
show_debug = st.toggle("Show debug", value=False)

if run:
    if not text.strip():
        st.warning("Please paste some text.")
    else:
        with st.spinner("Analyzing..."):
            result = run_pipeline(text, "en")

        st.subheader("Results")
        st.metric("Safe to show", "Yes" if result.safe_to_show else "No")
        st.metric("Overall severity", f"{result.overall_severity:.2f}")

        st.subheader("Trigger warnings")
        if result.trigger_warnings:
            for w in result.trigger_warnings:
                st.warning(w)
        else:
            st.success("No trigger warnings detected.")

        st.subheader("Findings")
        if result.findings:
            for f in result.findings:
                st.write(f"**{f.category}** — severity **{f.severity:.2f}** — reasons: `{', '.join(f.reasons)}`")
        else:
            st.write("No findings.")

        if show_debug:
            st.subheader("Debug")
            st.json(result.debug or {})
