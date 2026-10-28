"""The agent: a small, explicit state machine over named nodes.

Node order mirrors a real onboarding flow, and each node appends to a
trace so the decision is auditable:

    intake_guardrails -> document_verification -> risk_check
        -> retrieval -> verifier -> decision

Design choice worth defending in an interview: the agent does NOT
maximise answer rate. It maximises *safe* answer rate. Low confidence,
high risk, missing documents, or a suspected injection all escalate
instead of producing a fluent but unverified answer. That is the whole
point for a regulated setting — the 15% a production assistant does
not answer autonomously is a feature, not a failure.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

from .guardrails import detect_injection, redact_text
from .kb import load_knowledge_base
from .retrieval import Retriever, extract_answer_sentences
from .risk import score_risk

CONFIDENCE_THRESHOLD = 0.35

# Decisions are deliberately coarse so a reviewer can act on them.
ANSWERED = "ANSWERED"
ANSWER_WITH_REVIEW = "ANSWER_WITH_REVIEW"
REQUEST_DOCUMENTS = "REQUEST_DOCUMENTS"
ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"


@dataclass
class CaseInput:
    applicant_ref: str  # synthetic reference only, e.g. "SYN-001"
    question: str
    country: str = ""
    is_pep: bool = False
    is_sanctions_match: bool = False
    initial_deposit_usd: float = 0.0
    expected_monthly_volume_usd: float = 0.0
    documents_provided: list[str] = field(default_factory=list)


class BankingAgent:
    def __init__(self, documents: list[dict] | None = None):
        self.retriever = Retriever(documents or load_knowledge_base())

    def run(self, case: CaseInput) -> dict:
        started = time.perf_counter()
        trace: list[str] = []

        # Node 1: intake + guardrails. Redact before logging anything.
        redacted_question = redact_text(case.question)
        injection = detect_injection(case.question)
        trace.append("intake_guardrails: question redacted for trace")
        if injection:
            trace.append("intake_guardrails: suspected prompt injection -> escalate")

        # Node 2: document verification.
        risk = score_risk(
            country=case.country,
            is_pep=case.is_pep,
            is_sanctions_match=case.is_sanctions_match,
            initial_deposit_usd=case.initial_deposit_usd,
            expected_monthly_volume_usd=case.expected_monthly_volume_usd,
            documents_provided=case.documents_provided,
        )
        trace.append(
            f"document_verification: missing={risk['missing_documents'] or 'none'}"
        )

        # Node 3: risk check (score already computed; record the level).
        trace.append(f"risk_check: score={risk['score']} level={risk['level']}")

        # Node 4: retrieval, skipped for injection attempts.
        citations = [] if injection else self.retriever.retrieve(redacted_question, top_k=3)
        confidence = citations[0]["confidence"] if citations else 0.0
        trace.append(
            f"retrieval: top_doc={citations[0]['id'] if citations else 'none'} "
            f"confidence={confidence}"
        )

        # Node 5: verifier + decision.
        if injection:
            decision = ESCALATE_TO_HUMAN
            answer = (
                "This request could not be processed autonomously and has been "
                "escalated to a human compliance reviewer."
            )
        elif risk["level"] == "high":
            decision = ESCALATE_TO_HUMAN
            answer = (
                "This case requires human compliance review before any account "
                "decision. No autonomous approval is given."
            )
        elif risk["missing_documents"]:
            decision = REQUEST_DOCUMENTS
            answer = (
                "Please provide the missing documents before onboarding can "
                f"continue: {', '.join(risk['missing_documents'])}."
            )
        elif not citations or confidence < CONFIDENCE_THRESHOLD:
            decision = ESCALATE_TO_HUMAN
            answer = (
                "No policy document could be verified with sufficient confidence "
                "for this question, so it has been escalated to a human reviewer "
                "rather than answered from an unverified source."
            )
        else:
            sentences = extract_answer_sentences(citations[0]["text"], redacted_question)
            answer = " ".join(sentences)
            if risk["level"] == "medium":
                decision = ANSWER_WITH_REVIEW
                answer += " This answer is flagged for human review due to medium risk."
            else:
                decision = ANSWERED
        trace.append(f"decision: {decision}")

        # Policy answer, when one exists, is appended after any case notice
        # so the reviewer sees both the decision and the grounded answer.
        if decision in (REQUEST_DOCUMENTS, ESCALATE_TO_HUMAN) and citations and not injection:
            if risk["level"] != "high":
                sentences = extract_answer_sentences(
                    citations[0]["text"], redacted_question
                )
                answer += " Relevant policy: " + " ".join(sentences)

        latency_ms = round((time.perf_counter() - started) * 1000, 1)
        # Stub cost model: ~4 chars per token at a placeholder $0.002 / 1k tokens.
        # This is a demo estimate, not a vendor bill, and is labelled as such.
        estimated_tokens = max(1, len(case.question + answer) // 4)
        estimated_cost_usd = round(estimated_tokens / 1000 * 0.002, 6)

        return {
            "applicant_ref": case.applicant_ref,
            "decision": decision,
            "answer": answer,
            "citations": [
                {"id": c["id"], "title": c["title"], "score": c["score"]}
                for c in citations
            ],
            "confidence": confidence,
            "risk": risk,
            "trace": trace,
            "redacted_question": redacted_question,
            "latency_ms": latency_ms,
            "estimated_cost_usd": estimated_cost_usd,
            "estimated_tokens": estimated_tokens,
        }
