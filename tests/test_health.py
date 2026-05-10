def test_health_returns_payload(client):
    res = client.get("/health")
    assert res.status_code == 200
    body = res.json()
    assert "status" in body
    assert body["database"] == "connected"


def test_root_message(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.json().get("message")
