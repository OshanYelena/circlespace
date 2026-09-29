"""Reset and seed deterministic Dataset D1 for development benchmarks only."""

import argparse
import random
import sys
import time
from collections.abc import Iterable, Sequence
from datetime import datetime, timedelta, timezone
from typing import TypeVar

from sqlalchemy import func, insert, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password, verify_password
from app.db.session import SessionLocal
from app.modules.articles.models import Notification
from app.modules.friendships.models import FriendRequest, Friendship
from app.modules.posts.models import Comment, Like, Post, Share
from app.modules.users.models import Profile, User

DATASET_NAME = "D1"
RANDOM_SEED = 42
BENCHMARK_USERNAME = "benchmark_user_0001"
BENCHMARK_PASSWORD = "benchmark-password-d1"
BASE_TIME = datetime(2024, 1, 1, tzinfo=timezone.utc)
BATCH_SIZE = 5_000

TARGET_COUNTS = {
    "users": 1_000,
    "profiles": 1_000,
    "posts": 10_000,
    "comments": 30_000,
    "likes": 50_000,
    "friendships": 5_000,
    "notifications": 10_000,
    "friend_requests": 0,
    "shares": 0,
}

TABLE_MODELS = {
    "users": User,
    "profiles": Profile,
    "posts": Post,
    "comments": Comment,
    "likes": Like,
    "friendships": Friendship,
    "notifications": Notification,
    "friend_requests": FriendRequest,
    "shares": Share,
}

DELETE_ORDER = (
    "notifications",
    "shares",
    "likes",
    "comments",
    "posts",
    "friendships",
    "friend_requests",
    "profiles",
    "users",
)

T = TypeVar("T")


def skewed_choice(rng: random.Random, items: Sequence[T], exponent: float) -> T:
    """Choose lower-ranked items more often without rebuilding weighted tables."""
    if not items:
        raise ValueError("cannot choose from an empty sequence")
    index = min(int((rng.random() ** exponent) * len(items)), len(items) - 1)
    return items[index]


def unique_canonical_pairs(
    rng: random.Random,
    left_items: Sequence[int],
    right_items: Sequence[int],
    count: int,
    *,
    left_exponent: float,
    right_exponent: float,
) -> list[tuple[int, int]]:
    """Generate deterministic unique non-self pairs in canonical order."""
    maximum = len(set(left_items) | set(right_items))
    if count > maximum * (maximum - 1) // 2:
        raise ValueError("requested pair count exceeds available canonical pairs")

    pairs: set[tuple[int, int]] = set()
    while len(pairs) < count:
        left = skewed_choice(rng, left_items, left_exponent)
        right = skewed_choice(rng, right_items, right_exponent)
        if left != right:
            pairs.add((min(left, right), max(left, right)))
    return sorted(pairs)


def unique_like_pairs(
    rng: random.Random,
    ranked_post_ids: Sequence[int],
    ranked_user_ids: Sequence[int],
    count: int,
) -> list[tuple[int, int]]:
    """Generate unique post/user likes with deterministic popularity skew."""
    if count > len(ranked_post_ids) * len(ranked_user_ids):
        raise ValueError("requested likes exceed available unique post/user pairs")

    pairs: set[tuple[int, int]] = set()
    while len(pairs) < count:
        post_id = skewed_choice(rng, ranked_post_ids, 2.2)
        user_id = skewed_choice(rng, ranked_user_ids, 1.7)
        pairs.add((post_id, user_id))
    return sorted(pairs)


def assert_safe_target(database_url: str, confirmed: bool) -> None:
    """Reject accidental destructive execution outside known local/container targets."""
    if not confirmed:
        raise RuntimeError("reset confirmation missing; pass --confirm-reset-d1")

    url = make_url(database_url)
    if url.get_backend_name() != "postgresql":
        raise RuntimeError("Dataset D1 requires PostgreSQL")

    database = (url.database or "").lower()
    host = (url.host or "").lower()
    if any(marker in database or marker in host for marker in ("prod", "production", "live")):
        raise RuntimeError("refusing to reset a production-looking database target")
    if host not in {"localhost", "127.0.0.1", "::1", "db", "postgres"}:
        raise RuntimeError(
            f"refusing non-local database host {host!r}; D1 is development tooling only"
        )


def _insert_in_batches(session: Session, model: type, rows: Iterable[dict]) -> None:
    batch: list[dict] = []
    for row in rows:
        batch.append(row)
        if len(batch) == BATCH_SIZE:
            session.execute(insert(model), batch)
            batch.clear()
    if batch:
        session.execute(insert(model), batch)


def reset_application_data(session: Session) -> None:
    table_list = ", ".join(DELETE_ORDER)
    session.execute(text(f"TRUNCATE TABLE {table_list} RESTART IDENTITY CASCADE"))


def seed_d1(session: Session) -> None:
    rng = random.Random(RANDOM_SEED)
    shared_password_hash = hash_password(BENCHMARK_PASSWORD)

    _insert_in_batches(
        session,
        User,
        (
            {
                "email": f"benchmark_user_{index:04d}@example.test",
                "username": f"benchmark_user_{index:04d}",
                "hashed_password": shared_password_hash,
                "created_at": BASE_TIME + timedelta(seconds=index),
            }
            for index in range(1, TARGET_COUNTS["users"] + 1)
        ),
    )
    user_ids = list(session.scalars(select(User.id).order_by(User.id)))

    locations = ("Colombo", "London", "New York", "Berlin", "Singapore", "Toronto")
    _insert_in_batches(
        session,
        Profile,
        (
            {
                "user_id": user_id,
                "display_name": f"Benchmark User {index:04d}",
                "bio": f"Dataset D1 participant in activity cohort {index % 20:02d}.",
                "location": locations[index % len(locations)],
                "updated_at": BASE_TIME + timedelta(seconds=index),
            }
            for index, user_id in enumerate(user_ids, 1)
        ),
    )

    ranked_user_ids = user_ids.copy()
    rng.shuffle(ranked_user_ids)
    topics = ("databases", "systems", "networks", "testing", "design", "operations")
    post_rows = []
    for index in range(1, TARGET_COUNTS["posts"] + 1):
        author_id = skewed_choice(rng, ranked_user_ids, 2.0)
        popularity = rng.random() ** 4
        post_rows.append(
            {
                "author_id": author_id,
                "title": f"D1 {topics[index % len(topics)].title()} Note {index:05d}",
                "content": (
                    f"Deterministic benchmark post {index:05d} about "
                    f"{topics[index % len(topics)]}. Activity cohort {author_id % 25:02d}."
                ),
                "image_url": None,
                "view_count": int(popularity * 250_000),
                "created_at": BASE_TIME + timedelta(minutes=index),
                "updated_at": BASE_TIME + timedelta(minutes=index),
            }
        )
    _insert_in_batches(session, Post, post_rows)
    post_ids = list(session.scalars(select(Post.id).order_by(Post.id)))
    author_by_post = dict(session.execute(select(Post.id, Post.author_id)).tuples().all())

    ranked_post_ids = post_ids.copy()
    rng.shuffle(ranked_post_ids)

    friendship_pairs = unique_canonical_pairs(
        rng,
        ranked_user_ids,
        ranked_user_ids,
        TARGET_COUNTS["friendships"],
        left_exponent=2.2,
        right_exponent=1.5,
    )
    _insert_in_batches(
        session,
        Friendship,
        (
            {
                "user_low_id": low_id,
                "user_high_id": high_id,
                "created_at": BASE_TIME + timedelta(seconds=index),
            }
            for index, (low_id, high_id) in enumerate(friendship_pairs)
        ),
    )

    _insert_in_batches(
        session,
        Comment,
        (
            {
                "post_id": skewed_choice(rng, ranked_post_ids, 2.0),
                "author_id": skewed_choice(rng, ranked_user_ids, 1.6),
                "content": f"Deterministic D1 comment {index:05d}.",
                "created_at": BASE_TIME + timedelta(minutes=10_000, seconds=index),
                "updated_at": BASE_TIME + timedelta(minutes=10_000, seconds=index),
            }
            for index in range(1, TARGET_COUNTS["comments"] + 1)
        ),
    )

    like_pairs = unique_like_pairs(rng, ranked_post_ids, ranked_user_ids, TARGET_COUNTS["likes"])
    _insert_in_batches(
        session,
        Like,
        (
            {
                "post_id": post_id,
                "user_id": user_id,
                "created_at": BASE_TIME + timedelta(minutes=20_000, seconds=index),
            }
            for index, (post_id, user_id) in enumerate(like_pairs)
        ),
    )

    notification_rows = []
    for index in range(1, TARGET_COUNTS["notifications"] + 1):
        post_id = skewed_choice(rng, ranked_post_ids, 2.3)
        created_at = BASE_TIME + timedelta(minutes=30_000, seconds=index)
        notification_rows.append(
            {
                "user_id": author_by_post[post_id],
                "type": "article_liked" if index % 3 else "article_commented",
                "reference_id": post_id,
                "created_at": created_at,
                "read_at": created_at + timedelta(minutes=5) if index % 4 == 0 else None,
            }
        )
    _insert_in_batches(session, Notification, notification_rows)


def collect_verification(session: Session) -> tuple[dict[str, int], int, str, bool]:
    actual = {
        table_name: session.scalar(select(func.count()).select_from(model)) or 0
        for table_name, model in TABLE_MODELS.items()
    }
    database_size = session.scalar(text("SELECT pg_database_size(current_database())")) or 0
    database_size_pretty = (
        session.scalar(text("SELECT pg_size_pretty(pg_database_size(current_database()))"))
        or "unknown"
    )
    benchmark_user = session.scalar(select(User).where(User.username == BENCHMARK_USERNAME))
    auth_valid = bool(
        benchmark_user and verify_password(BENCHMARK_PASSWORD, benchmark_user.hashed_password)
    )
    return actual, int(database_size), str(database_size_pretty), auth_valid


def print_verification(
    actual: dict[str, int],
    database_size: int,
    database_size_pretty: str,
    auth_valid: bool,
    elapsed_seconds: float,
) -> bool:
    print(f"CircleSpace benchmark dataset: {DATASET_NAME}")
    print(f"Random seed: {RANDOM_SEED}")
    print(f"Elapsed seed time: {elapsed_seconds:.3f} seconds")
    print(f"PostgreSQL database size: {database_size_pretty} ({database_size} bytes)")
    print(f"Benchmark username: {BENCHMARK_USERNAME}")
    print(f"Benchmark password: {BENCHMARK_PASSWORD} (development/load testing only)")
    print("\nTable verification:")
    print(f"{'table':<18} {'expected':>10} {'actual':>10} {'result':>8}")
    all_passed = True
    for table_name, expected in TARGET_COUNTS.items():
        observed = actual.get(table_name, -1)
        passed = observed == expected
        all_passed = all_passed and passed
        print(f"{table_name:<18} {expected:>10,} {observed:>10,} {'PASS' if passed else 'FAIL':>8}")
    login_result = "PASS" if auth_valid else "FAIL"
    print(f"{'benchmark_login':<18} {'valid':>10} {str(auth_valid):>10} {login_result:>8}")
    all_passed = all_passed and auth_valid
    print(f"\nDataset {DATASET_NAME}: {'PASS' if all_passed else 'FAIL'}")
    return all_passed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--confirm-reset-d1",
        action="store_true",
        help="confirm deletion of all application rows before recreating D1",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="verify the current database without deleting or inserting rows",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = get_settings()
    started = time.perf_counter()

    try:
        if not args.verify_only:
            assert_safe_target(settings.database_url, args.confirm_reset_d1)
        with SessionLocal() as session:
            if not args.verify_only:
                reset_application_data(session)
                seed_d1(session)
                session.commit()
            actual, database_size, database_size_pretty, auth_valid = collect_verification(session)
    except Exception as exc:
        print(f"Dataset {DATASET_NAME} seed failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    passed = print_verification(
        actual,
        database_size,
        database_size_pretty,
        auth_valid,
        time.perf_counter() - started,
    )
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
