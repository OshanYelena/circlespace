from fastapi.testclient import TestClient


def register(client: TestClient, username: str) -> dict:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": f"{username}@example.com",
            "username": username,
            "password": "correct-horse",
            "display_name": username.title(),
        },
    )
    assert response.status_code == 201
    return response.json()


def auth(user: dict) -> dict[str, str]:
    return {"Authorization": f"Bearer {user['access_token']}"}


def test_friend_request_accept_and_remove(client: TestClient) -> None:
    ada = register(client, "ada")
    grace = register(client, "grace")

    sent = client.post(
        "/api/v1/friendships/requests", headers=auth(ada), json={"username": "grace"}
    )
    assert sent.status_code == 201

    received = client.get("/api/v1/friendships/requests/received", headers=auth(grace))
    assert received.status_code == 200
    assert received.json()[0]["requester"]["username"] == "ada"

    accepted = client.patch(
        f"/api/v1/friendships/requests/{sent.json()['id']}",
        headers=auth(grace),
        json={"action": "accept"},
    )
    assert accepted.status_code == 200
    assert accepted.json()["status"] == "accepted"

    friends = client.get("/api/v1/friendships", headers=auth(ada))
    assert [friend["username"] for friend in friends.json()] == ["grace"]

    removed = client.delete(f"/api/v1/friendships/{grace['user']['id']}", headers=auth(ada))
    assert removed.status_code == 204


def test_friend_request_invariants(client: TestClient) -> None:
    ada = register(client, "ada")
    grace = register(client, "grace")

    self_request = client.post(
        "/api/v1/friendships/requests", headers=auth(ada), json={"username": "ada"}
    )
    assert self_request.status_code == 400

    first = client.post(
        "/api/v1/friendships/requests", headers=auth(ada), json={"username": "grace"}
    )
    assert first.status_code == 201
    duplicate = client.post(
        "/api/v1/friendships/requests", headers=auth(grace), json={"username": "ada"}
    )
    assert duplicate.status_code == 409

    forbidden = client.patch(
        f"/api/v1/friendships/requests/{first.json()['id']}",
        headers=auth(ada),
        json={"action": "reject"},
    )
    assert forbidden.status_code == 403
