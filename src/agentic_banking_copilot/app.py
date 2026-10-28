"""FastAPI service for the agent.

Run locally:
    uvicorn agentic_banking_copilot.app:app --reload --port 8000

Then POST to /onboarding/run. See README for an example payload.
No LLM API key is required: retrieval and answering are extractive
over the synthetic knowledge base by default.
"""

from __future__ import annotations

from collections import Counter

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .agent import BankingAgent, CaseInput

app = FastAPI(title="Agentic Banking Copilot", version="0.1.0")
agent = BankingAgent()
_decisions = Counter()
_cases = 0


class CaseRequest(BaseModel):
    applicant_ref: str = Field(default="SYN-001")
    question: str
    country: str = ""
    is_pep: bool = False
    is_sanctions_match: bool = False
    initial_deposit_usd: float = 0.0
    expected_monthly_volume_usd: float = 0.0
    documents_provided: list[str] = Field(default_factory=list)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> dict:
    return {"cases_processed": _cases, "decisions": dict(_decisions)}


@app.post("/onboarding/run")
def run_case(payload: CaseRequest) -> dict:
    global _cases
    result = agent.run(CaseInput(**payload.model_dump()))
    _cases += 1
    _decisions[result["decision"]] += 1
    return result
