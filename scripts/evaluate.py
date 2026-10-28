"""Run the agent over data/eval_qa.jsonl and write eval/report.md + results.json.

Metrics are deliberately simple and reproducible:
- citation_accuracy: top-1 cited doc == expected doc (policy QA items only)
- answer_keyword_hit: at least one expected keyword appears in the answer
- decision_accuracy: agent decision == expected decision (all items)
- faithfulness_proxy: the answer is extractive — a sentence from the
  cited document appears in the answer (policy QA items only)
- autonomous_rate: ANSWERED + ANSWER_WITH_REVIEW share of all items

Run:  PYTHONPATH=src python scripts/evaluate.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from agentic_banking_copilot.agent import CaseInput, BankingAgent  # noqa: E402
from agentic_banking_copilot.kb import load_knowledge_base  # noqa: E402


def main() -> None:
    agent = BankingAgent(load_knowledge_base())
    rows = []
    with open(ROOT / "data" / "eval_qa.jsonl", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    results = []
    for row in rows:
        case = CaseInput(
            applicant_ref=row["id"],
            question=row["question"],
            country=row.get("country", ""),
            is_pep=row.get("is_pep", False),
            is_sanctions_match=row.get("is_sanctions_match", False),
            initial_deposit_usd=row.get("initial_deposit_usd", 0.0),
            documents_provided=row.get("documents_provided", []),
        )
        out = agent.run(case)
        answer_lower = out["answer"].lower()
        top_doc = out["citations"][0]["id"] if out["citations"] else ""
        is_policy = bool(row.get("expected_doc_id"))
        # Faithfulness proxy: an extractive answer reuses a cited doc sentence.
        cited_text = ""
        if top_doc:
            cited_text = next(
                (d["text"] for d in load_knowledge_base() if d["id"] == top_doc), ""
            )
        faithful = False
        if is_policy and cited_text:
            # Check any sentence fragment (first 40 chars of a sentence) in answer.
            for sentence in cited_text.split(". "):
                fragment = sentence.strip()[:40].lower()
                if fragment and fragment in answer_lower:
                    faithful = True
                    break
        results.append(
            {
                "id": row["id"],
                "decision": out["decision"],
                "expected_decision": row["expected_decision"],
                "decision_correct": out["decision"] == row["expected_decision"],
                "top_doc": top_doc,
                "expected_doc_id": row.get("expected_doc_id", ""),
                "citation_correct": (top_doc == row["expected_doc_id"]) if is_policy else None,
                "keyword_hit": (
                    any(k.lower() in answer_lower for k in row.get("answer_keywords", []))
                    if is_policy
                    else None
                ),
                "faithful": faithful if is_policy else None,
                "confidence": out["confidence"],
                "latency_ms": out["latency_ms"],
                "estimated_cost_usd": out["estimated_cost_usd"],
            }
        )

    policy = [r for r in results if r["citation_correct"] is not None]
    metrics = {
        "n_items": len(results),
        "n_policy_qa": len(policy),
        "citation_accuracy_top1": round(
            sum(r["citation_correct"] for r in policy) / max(1, len(policy)), 3
        ),
        "answer_keyword_hit_rate": round(
            sum(r["keyword_hit"] for r in policy) / max(1, len(policy)), 3
        ),
        "faithfulness_proxy": round(
            sum(r["faithful"] for r in policy) / max(1, len(policy)), 3
        ),
        "decision_accuracy": round(
            sum(r["decision_correct"] for r in results) / max(1, len(results)), 3
        ),
        "autonomous_rate": round(
            sum(
                r["decision"] in ("ANSWERED", "ANSWER_WITH_REVIEW") for r in results
            )
            / max(1, len(results)),
            3,
        ),
        "escalation_rate": round(
            sum(r["decision"] == "ESCALATE_TO_HUMAN" for r in results)
            / max(1, len(results)),
            3,
        ),
        "avg_latency_ms": round(
            sum(r["latency_ms"] for r in results) / max(1, len(results)), 1
        ),
        "avg_estimated_cost_usd": round(
            sum(r["estimated_cost_usd"] for r in results) / max(1, len(results)), 6
        ),
    }

    eval_dir = ROOT / "eval"
    eval_dir.mkdir(exist_ok=True)
    with open(eval_dir / "results.json", "w", encoding="utf-8") as f:
        json.dump({"metrics": metrics, "results": results}, f, indent=2)

    lines = [
        "# Evaluation report — synthetic data only",
        "",
        "The agent was run over `data/eval_qa.jsonl` (synthetic questions, "
        "synthetic applicants, synthetic policy documents). These numbers "
        "describe this demo, not any production system.",
        "",
        "| Metric | Value |",
        "|---|---|",
    ]
    for key, value in metrics.items():
        lines.append(f"| {key} | {value} |")
    lines += ["", "## Per-item results", ""]
    for r in results:
        lines.append(
            f"- {r['id']}: decision={r['decision']} "
            f"(expected {r['expected_decision']}, "
            f"{'correct' if r['decision_correct'] else 'WRONG'}), "
            f"top_doc={r['top_doc'] or 'none'}, confidence={r['confidence']}"
        )
    with open(eval_dir / "report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
