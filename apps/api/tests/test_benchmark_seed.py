import random

import pytest

from app.benchmark_seed import (
    assert_safe_target,
    print_verification,
    skewed_choice,
    unique_canonical_pairs,
    unique_like_pairs,
)


def test_skew_helpers_are_deterministic_and_constraint_safe() -> None:
    users = list(range(1, 51))
    posts = list(range(1, 101))

    first_rng = random.Random(42)
    second_rng = random.Random(42)
    first_friendships = unique_canonical_pairs(
        first_rng,
        users,
        users,
        100,
        left_exponent=2.2,
        right_exponent=1.5,
    )
    second_friendships = unique_canonical_pairs(
        second_rng,
        users,
        users,
        100,
        left_exponent=2.2,
        right_exponent=1.5,
    )
    assert first_friendships == second_friendships
    assert len(first_friendships) == len(set(first_friendships)) == 100
    assert all(low < high for low, high in first_friendships)

    first_likes = unique_like_pairs(first_rng, posts, users, 500)
    second_likes = unique_like_pairs(second_rng, posts, users, 500)
    assert first_likes == second_likes
    assert len(first_likes) == len(set(first_likes)) == 500


def test_skewed_choice_prefers_low_ranked_items() -> None:
    rng = random.Random(42)
    items = list(range(100))
    sample = [skewed_choice(rng, items, 2.2) for _ in range(2_000)]
    assert sum(value < 20 for value in sample) > sum(value >= 80 for value in sample)


def test_reset_safety_requires_confirmation_and_local_postgres() -> None:
    with pytest.raises(RuntimeError, match="confirmation"):
        assert_safe_target("postgresql+psycopg://localhost/circlespace", False)
    with pytest.raises(RuntimeError, match="production-looking"):
        assert_safe_target("postgresql+psycopg://localhost/circlespace_prod", True)
    with pytest.raises(RuntimeError, match="non-local"):
        assert_safe_target("postgresql+psycopg://database.example.com/circlespace", True)
    with pytest.raises(RuntimeError, match="requires PostgreSQL"):
        assert_safe_target("sqlite:///test.db", True)

    assert_safe_target("postgresql+psycopg://db/circlespace", True)


def test_verification_fails_on_any_count_mismatch(capsys: pytest.CaptureFixture[str]) -> None:
    actual = {
        "users": 999,
        "profiles": 1_000,
        "posts": 10_000,
        "comments": 30_000,
        "likes": 50_000,
        "friendships": 5_000,
        "notifications": 10_000,
        "friend_requests": 0,
        "shares": 0,
    }
    assert not print_verification(actual, 1024, "1024 bytes", True, 1.0)
    assert "Dataset D1: FAIL" in capsys.readouterr().out
