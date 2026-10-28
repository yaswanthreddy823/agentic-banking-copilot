# Evaluation report — synthetic data only

The agent was run over `data/eval_qa.jsonl` (synthetic questions, synthetic applicants, synthetic policy documents). These numbers describe this demo, not any production system.

| Metric | Value |
|---|---|
| n_items | 32 |
| n_policy_qa | 26 |
| citation_accuracy_top1 | 0.962 |
| answer_keyword_hit_rate | 0.885 |
| faithfulness_proxy | 1.0 |
| decision_accuracy | 1.0 |
| autonomous_rate | 0.812 |
| escalation_rate | 0.125 |
| avg_latency_ms | 0.2 |
| avg_estimated_cost_usd | 0.000137 |

## Per-item results

- eval-01: decision=ANSWERED (expected ANSWERED, correct), top_doc=kyc-documents, confidence=0.936
- eval-02: decision=ANSWERED (expected ANSWERED, correct), top_doc=kyc-verification-steps, confidence=0.952
- eval-03: decision=ANSWERED (expected ANSWERED, correct), top_doc=onboarding-checklist, confidence=0.968
- eval-04: decision=ANSWERED (expected ANSWERED, correct), top_doc=aml-monitoring, confidence=0.993
- eval-05: decision=ANSWERED (expected ANSWERED, correct), top_doc=aml-sanctions, confidence=0.939
- eval-06: decision=ANSWERED (expected ANSWERED, correct), top_doc=aml-pep, confidence=0.939
- eval-07: decision=ANSWERED (expected ANSWERED, correct), top_doc=account-eligibility, confidence=0.836
- eval-08: decision=ANSWERED (expected ANSWERED, correct), top_doc=high-risk-jurisdictions, confidence=0.982
- eval-09: decision=ANSWERED (expected ANSWERED, correct), top_doc=fraud-reporting, confidence=0.987
- eval-10: decision=ANSWERED (expected ANSWERED, correct), top_doc=servicing-address-change, confidence=0.886
- eval-11: decision=ANSWERED (expected ANSWERED, correct), top_doc=servicing-online-banking, confidence=0.991
- eval-12: decision=ANSWERED (expected ANSWERED, correct), top_doc=source-of-funds, confidence=0.991
- eval-13: decision=ANSWERED (expected ANSWERED, correct), top_doc=servicing-address-change, confidence=0.871
- eval-14: decision=ANSWERED (expected ANSWERED, correct), top_doc=kyc-documents, confidence=0.884
- eval-15: decision=ANSWERED (expected ANSWERED, correct), top_doc=kyc-verification-steps, confidence=0.943
- eval-16: decision=ANSWERED (expected ANSWERED, correct), top_doc=onboarding-checklist, confidence=0.95
- eval-17: decision=ANSWERED (expected ANSWERED, correct), top_doc=aml-monitoring, confidence=0.939
- eval-18: decision=ANSWERED (expected ANSWERED, correct), top_doc=aml-sanctions, confidence=0.96
- eval-19: decision=ANSWERED (expected ANSWERED, correct), top_doc=aml-pep, confidence=0.951
- eval-20: decision=ANSWERED (expected ANSWERED, correct), top_doc=account-eligibility, confidence=0.934
- eval-21: decision=ANSWERED (expected ANSWERED, correct), top_doc=high-risk-jurisdictions, confidence=0.985
- eval-22: decision=ANSWERED (expected ANSWERED, correct), top_doc=fraud-reporting, confidence=0.98
- eval-23: decision=ANSWERED (expected ANSWERED, correct), top_doc=servicing-address-change, confidence=0.905
- eval-24: decision=ANSWERED (expected ANSWERED, correct), top_doc=servicing-online-banking, confidence=0.992
- eval-25: decision=ANSWERED (expected ANSWERED, correct), top_doc=source-of-funds, confidence=0.969
- eval-26: decision=ESCALATE_TO_HUMAN (expected ESCALATE_TO_HUMAN, correct), top_doc=kyc-documents, confidence=0.936
- eval-27: decision=ESCALATE_TO_HUMAN (expected ESCALATE_TO_HUMAN, correct), top_doc=kyc-documents, confidence=0.936
- eval-28: decision=REQUEST_DOCUMENTS (expected REQUEST_DOCUMENTS, correct), top_doc=kyc-documents, confidence=0.936
- eval-29: decision=REQUEST_DOCUMENTS (expected REQUEST_DOCUMENTS, correct), top_doc=kyc-documents, confidence=0.936
- eval-30: decision=ESCALATE_TO_HUMAN (expected ESCALATE_TO_HUMAN, correct), top_doc=none, confidence=0.0
- eval-31: decision=ESCALATE_TO_HUMAN (expected ESCALATE_TO_HUMAN, correct), top_doc=none, confidence=0.0
- eval-32: decision=ANSWER_WITH_REVIEW (expected ANSWER_WITH_REVIEW, correct), top_doc=aml-pep, confidence=0.939
