 SentinelAI — Content Safety Analyzer

Hybrid AI content moderation system that analyzes social media text and generates trigger warnings using rule-based heuristics and a local NLP model.

 Features
- Scam/fraud cues (rule-based)
- Sexual solicitation cues (rule-based)
- Child-safety risk cues (rule-based)
- Hate/harassment signal (local transformer model)
- Severity scoring + explainable findings

 Run the Streamlit demo locally
```bash
pip install -r requirements.txt
streamlit run streamlit_app/app.py
