# Main application entry point

from __future__ import annotations
from fastapi import FastAPI
from app.common.types import AskRequest
from app.agent.graph import run_graph
from app.infra.config import Config


app = FastAPI(title="AI Arch Dev (FastAPI + LangGraph)")


@app.get("/health")
def health():
    infra_info = Config.get_infra_context()
    return {
        "ok": True, 
        "mode": Config.DEPLOYMENT_MODE,
        "infra": infra_info
    }


@app.post("/ask")
def ask(req: AskRequest):
    out = run_graph(user=req.user.model_dump(), question=req.question)
    # answer 중심으로 반환
    return {"trace_id": out.get("trace_id"), "answer": out.get("answer")}
