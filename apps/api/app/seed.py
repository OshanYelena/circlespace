"""Idempotent demo data for local development."""

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.modules.friendships.models import Friendship
from app.modules.posts.models import Comment, Like, Post
from app.modules.users.models import Profile, User

DEMO_PASSWORD = "demo-password"


def seed() -> None:
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.email == "ada@example.com")):
            print("Demo data already exists.")
            return

        ada = User(
            email="ada@example.com",
            username="ada",
            hashed_password=hash_password(DEMO_PASSWORD),
            profile=Profile(
                display_name="Ada Lovelace",
                bio="Curious about machines, music, and impossible ideas.",
                location="London",
            ),
        )
        grace = User(
            email="grace@example.com",
            username="grace",
            hashed_password=hash_password(DEMO_PASSWORD),
            profile=Profile(
                display_name="Grace Hopper",
                bio="Making computers speak human.",
                location="New York",
            ),
        )
        db.add_all([ada, grace])
        db.flush()
        db.add(Friendship(user_low_id=min(ada.id, grace.id), user_high_id=max(ada.id, grace.id)))
        first = Post(
            author_id=ada.id,
            content="The imagination is a discovering faculty, pre-eminently.",
        )
        second = Post(
            author_id=grace.id,
            content="A ship in port is safe, but that is not what ships are for.",
        )
        db.add_all([first, second])
        db.flush()
        db.add_all(
            [
                Like(post_id=first.id, user_id=grace.id),
                Comment(post_id=first.id, author_id=grace.id, content="Here’s to discovering."),
            ]
        )
        db.commit()
        print("Created demo users ada and grace with password: demo-password")


if __name__ == "__main__":
    seed()
