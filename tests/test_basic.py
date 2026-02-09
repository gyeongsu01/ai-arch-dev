# Basic tests

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ask_doc_search_permit():
    r = client.post("/ask", json={"user":{"id":"u1","role":"analyst","scopes":["doc:read"]},"question":"최신 금리 문서 찾아줘"})
    assert r.status_code == 200
    assert "검색 결과" in r.json()["answer"]

def test_ask_doc_search_deny_missing_scope():
    r = client.post("/ask", json={"user":{"id":"u2","role":"guest","scopes":[]},"question":"최신 금리 문서 찾아줘"})
    assert r.status_code == 200
    assert "DENY" in r.json()["answer"]
