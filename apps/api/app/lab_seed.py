"""Deterministic dataset generator for scaling-lab experiments."""

import argparse
import json
import random
import time
from pathlib import Path

from sqlalchemy import delete, func, insert, select, text

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.modules.articles.models import Notification
from app.modules.friendships.models import FriendRequest, Friendship
from app.modules.posts.models import Comment, Like, Post, Share
from app.modules.users.models import Profile, User

LAB_PASSWORD = "lab-password"


def reset_database() -> None:
    with SessionLocal() as db:
        if db.bind and db.bind.dialect.name == "postgresql":
            db.execute(
                text(
                    "TRUNCATE notifications, shares, likes, comments, posts, friendships, "
                    "friend_requests, profiles, users RESTART IDENTITY CASCADE"
                )
            )
        else:
            for model in (
                Notification,
                Share,
                Like,
                Comment,
                Post,
                Friendship,
                FriendRequest,
                Profile,
                User,
            ):
                db.execute(delete(model))
        db.commit()


def generate_dataset(
    user_count: int, article_count: int, like_count: int, comment_count: int, seed: int
) -> dict[str, int | float | str]:
    if min(user_count, article_count) < 1:
        raise ValueError("users and articles must both be at least 1")
    if like_count > user_count * article_count:
        raise ValueError("likes cannot exceed the number of unique user/article pairs")

    started = time.perf_counter()
    rng = random.Random(seed)
    shared_password = hash_password(LAB_PASSWORD)
    with SessionLocal() as db:
        existing = db.scalar(select(func.count()).select_from(User)) or 0
        if existing:
            raise RuntimeError("database is not empty; pass --reset for a reproducible dataset")

        db.execute(
            insert(User),
            [
                {
                    "email": f"lab_user_{index:07d}@example.test",
                    "username": f"lab_user_{index:07d}",
                    "hashed_password": shared_password,
                }
                for index in range(user_count)
            ],
        )
        user_ids = list(db.scalars(select(User.id).order_by(User.id)))
        db.execute(
            insert(Profile),
            [
                {
                    "user_id": user_id,
                    "display_name": f"Lab User {index:07d}",
                    "bio": "Deterministic scaling-lab account.",
                }
                for index, user_id in enumerate(user_ids)
            ],
        )
        db.execute(
            insert(Post),
            [
                {
                    "author_id": user_ids[index % user_count],
                    "title": f"Scaling Lab Article {index:09d}",
                    "content": (
                        f"Deterministic article {index:09d}. "
                        f"Topic bucket {index % 100:03d}. "
                        + "Measurement requires stable data. "
                        * (1 + index % 8)
                    ),
                    "view_count": rng.randrange(0, 10_000),
                }
                for index in range(article_count)
            ],
        )
        article_ids = list(db.scalars(select(Post.id).order_by(Post.id)))

        like_pairs: set[tuple[int, int]] = set()
        while len(like_pairs) < like_count:
            like_pairs.add((rng.choice(article_ids), rng.choice(user_ids)))
        db.execute(
            insert(Like),
            [{"post_id": article_id, "user_id": user_id} for article_id, user_id in like_pairs],
        )
        db.execute(
            insert(Comment),
            [
                {
                    "post_id": article_ids[index % article_count],
                    "author_id": user_ids[(index * 17) % user_count],
                    "content": f"Deterministic lab comment {index:09d}.",
                }
                for index in range(comment_count)
            ],
        )
        db.commit()

    return {
        "seed": seed,
        "users": user_count,
        "articles": article_count,
        "likes": like_count,
        "comments": comment_count,
        "article_id_min": article_ids[0],
        "article_id_max": article_ids[-1],
        "generation_seconds": round(time.perf_counter() - started, 3),
        "lab_username": "lab_user_0000000",
        "lab_password": LAB_PASSWORD,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--users", type=int, default=100)
    parser.add_argument("--articles", type=int, default=1_000)
    parser.add_argument("--likes", type=int, default=5_000)
    parser.add_argument("--comments", type=int, default=2_000)
    parser.add_argument("--seed", type=int, default=20260929)
    parser.add_argument("--reset", action="store_true")
    parser.add_argument("--manifest", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.reset:
        reset_database()
    manifest = generate_dataset(args.users, args.articles, args.likes, args.comments, args.seed)
    output = json.dumps(manifest, indent=2)
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(output + "\n")
    print(output)


if __name__ == "__main__":
    main()
