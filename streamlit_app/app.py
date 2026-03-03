import sys
from pathlib import Path
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]

# Try both possible layouts
candidates = [
    ROOT / "backend",                     # Case A
    ROOT / "trigger-warning-app" / "backend",  # Case B
]

backend_path = None
for c in candidates:
    if (c / "app").exists():
        backend_path = c
        break

if backend_path is None:
    st.error("Backend folder not found. Expected backend/app or trigger-warning-app/backend/app")
    st.stop()

# IMPORTANT: insert at position 0 (stronger than append)
sys.path.insert(0, str(backend_path))

from app.pipeline.policy import run_pipeline  # noqa

st.set_page_config(page_title="SentinelAI — Content Safety", page_icon="🛡️", layout="centered")
st.title("🛡️ SentinelAI — Content Safety Analyzer")

text = st.text_area("Paste a social media post", height=180)

if st.button("Analyze", type="primary"):
    if not text.strip():
        st.warning("Please paste some text.")
    else:
        r = run_pipeline(text, "en")
        st.metric("Safe to show", "Yes" if r.safe_to_show else "No")
        st.metric("Overall severity", f"{r.overall_severity:.2f}")

        st.subheader("Trigger warnings")
        if r.trigger_warnings:
            for w in r.trigger_warnings:
                st.warning(w)
        else:
            st.success("No trigger warnings detected.")

        st.subheader("Findings")
        for f in r.findings:
            st.write(f"**{f.category}** — {f.severity:.2f} — `{', '.join(f.reasons)}`")
