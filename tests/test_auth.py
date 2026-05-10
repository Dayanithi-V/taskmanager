def test_register_login_refresh_flow(client):
    email = "user_refresh@test.com"
    password = "secretpass123"

    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 200
    assert r.json()["email"] == email
    assert r.json().get("role") == "user"

    r = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]

    r2 = client.post("/auth/refresh", json={"refresh_token": body["refresh_token"]})
    assert r2.status_code == 200
    refreshed = r2.json()
    assert refreshed["access_token"]
    assert refreshed["refresh_token"]
    assert refreshed["refresh_token"] != body["refresh_token"]


def test_admin_role_when_configured(client):
    email = "admin@test.com"
    password = "adminsecret123"
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 200
    assert r.json()["role"] == "admin"
