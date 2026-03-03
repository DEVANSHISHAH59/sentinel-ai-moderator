from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.pipeline.policy import run_pipeline

app = FastAPI(title="SentinelAI Moderation API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/moderate")
def moderate(payload: dict):
    return run_pipeline(payload.get("text", ""), payload.get("locale", "en"))
