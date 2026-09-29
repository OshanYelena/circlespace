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


def test_article_read_feed_search_and_atomic_views(client: TestClient) -> None:
    ada = register(client, "ada")
    created = client.post(
        "/api/v1/articles",
        headers=auth(ada),
        json={"title": "Analytical Engine", "content": "A machine for general computation."},
    )
    assert created.status_code == 201
    article_id = created.json()["id"]

    assert client.get(f"/api/v1/articles/{article_id}").json()["title"] == "Analytical Engine"
    assert client.get("/api/v1/feed").json()[0]["id"] == article_id
    assert client.get("/api/v1/articles/search?q=general").json()[0]["id"] == article_id

    first = client.post(f"/api/v1/articles/{article_id}/view")
    second = client.post(f"/api/v1/articles/{article_id}/view")
    assert first.json()["count"] == 1
    assert second.json()["count"] == 2


def test_article_engagement_is_idempotent_and_notifies_author(client: TestClient) -> None:
    ada = register(client, "ada")
    grace = register(client, "grace")
    article = client.post(
        "/api/v1/articles",
        headers=auth(ada),
        json={"title": "Notes", "content": "A short technical note."},
    ).json()

    first_like = client.post(f"/api/v1/articles/{article['id']}/like", headers=auth(grace))
    second_like = client.post(f"/api/v1/articles/{article['id']}/like", headers=auth(grace))
    assert first_like.json() == {"article_id": article["id"], "count": 1, "created": True}
    assert second_like.json() == {"article_id": article["id"], "count": 1, "created": False}

    comment = client.post(
        f"/api/v1/articles/{article['id']}/comments",
        headers=auth(grace),
        json={"content": "Useful work."},
    )
    assert comment.status_code == 200
    assert comment.json()["count"] == 1

    notifications = client.get("/api/v1/notifications", headers=auth(ada))
    assert [item["type"] for item in notifications.json()] == [
        "article_commented",
        "article_liked",
    ]
