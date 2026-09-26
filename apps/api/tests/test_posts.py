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


def become_friends(client: TestClient, first: dict, second: dict) -> None:
    request = client.post(
        "/api/v1/friendships/requests",
        headers=auth(first),
        json={"username": second["user"]["username"]},
    )
    client.patch(
        f"/api/v1/friendships/requests/{request.json()['id']}",
        headers=auth(second),
        json={"action": "accept"},
    )


def test_post_crud_and_feed_visibility(client: TestClient) -> None:
    ada = register(client, "ada")
    grace = register(client, "grace")
    linus = register(client, "linus")
    become_friends(client, ada, grace)

    post = client.post("/api/v1/posts", headers=auth(grace), json={"content": "Hello, Ada"})
    assert post.status_code == 201
    post_id = post.json()["id"]

    hidden = client.post("/api/v1/posts", headers=auth(linus), json={"content": "Kernel news"})
    assert hidden.status_code == 201

    feed = client.get("/api/v1/posts/feed", headers=auth(ada))
    assert [item["content"] for item in feed.json()] == ["Hello, Ada"]

    forbidden = client.patch(
        f"/api/v1/posts/{post_id}", headers=auth(ada), json={"content": "Changed"}
    )
    assert forbidden.status_code == 403
    edited = client.patch(
        f"/api/v1/posts/{post_id}", headers=auth(grace), json={"content": "Hello, world"}
    )
    assert edited.status_code == 200


def test_comments_likes_and_shares_are_idempotent(client: TestClient) -> None:
    ada = register(client, "ada")
    grace = register(client, "grace")
    post = client.post("/api/v1/posts", headers=auth(ada), json={"content": "Analytical Engine"})
    post_id = post.json()["id"]

    first_like = client.put(f"/api/v1/posts/{post_id}/like", headers=auth(grace))
    second_like = client.put(f"/api/v1/posts/{post_id}/like", headers=auth(grace))
    assert first_like.json()["count"] == second_like.json()["count"] == 1

    first_share = client.put(f"/api/v1/posts/{post_id}/share", headers=auth(grace))
    second_share = client.put(f"/api/v1/posts/{post_id}/share", headers=auth(grace))
    assert first_share.json()["count"] == second_share.json()["count"] == 1

    commented = client.post(
        f"/api/v1/posts/{post_id}/comments",
        headers=auth(grace),
        json={"content": "Remarkable"},
    )
    assert commented.status_code == 201
    comment_id = commented.json()["comments"][0]["id"]

    forbidden = client.delete(f"/api/v1/posts/comments/{comment_id}", headers=auth(ada))
    assert forbidden.status_code == 403
    deleted = client.delete(f"/api/v1/posts/comments/{comment_id}", headers=auth(grace))
    assert deleted.status_code == 204
