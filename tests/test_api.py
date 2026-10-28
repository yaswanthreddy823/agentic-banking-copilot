import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient

from agentic_banking_copilot.app import app

client = TestClient(app)


def test_health():
    assert client.get("/health").json() == {"status": "ok"}


def test_onboarding_run():
    resp = client.post(
        "/onboarding/run",
        json={
            "applicant_ref": "SYN-001",
            "question": "What documents are required to open an account?",
            "documents_provided": ["government_id", "proof_of_address"],
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["decision"] == "ANSWERED"
    assert body["citations"]
