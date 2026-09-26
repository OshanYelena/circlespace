from fastapi.testclient import TestClient


def test_register_login_and_read_profile(client: TestClient, registered_user: dict) -> None:
    token = registered_user["access_token"]
    me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "ada"

    login = client.post("/api/v1/auth/login", json={"login": "ada", "password": "correct-horse"})
    assert login.status_code == 200
    assert login.json()["token_type"] == "bearer"


def test_profile_update_and_public_read(client: TestClient, registered_user: dict) -> None:
    token = registered_user["access_token"]
    updated = client.patch(
        "/api/v1/users/me/profile",
        headers={"Authorization": f"Bearer {token}"},
        json={"bio": "Computing pioneer", "location": "London"},
    )
    assert updated.status_code == 200
    assert updated.json()["profile"]["bio"] == "Computing pioneer"

    public = client.get("/api/v1/users/ada")
    assert public.status_code == 200
    assert "email" not in public.json()


def test_rejects_duplicate_and_invalid_login(client: TestClient, registered_user: dict) -> None:
    duplicate = client.post(
        "/api/v1/auth/register",
        json={
            "email": "ada@example.com",
            "username": "another",
            "password": "correct-horse",
            "display_name": "Duplicate",
        },
    )
    assert duplicate.status_code == 409

    login = client.post("/api/v1/auth/login", json={"login": "ada", "password": "wrong-pass"})
    assert login.status_code == 401
