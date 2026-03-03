from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.pipeline.schemas import ModerateRequest, ModerateResponse
from app.pipeline.policy import run_pipeline

app = FastAPI(title="SentinelAI Moderation API", version="0.1.0")

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

@app.post("/moderate", response_model=ModerateResponse)
def moderate(req: ModerateRequest):
    return run_pipeline(req.text, req.locale)
