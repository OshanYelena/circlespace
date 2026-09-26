from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.modules.users.models import Profile, User
from app.modules.users.schemas import ProfileUpdate


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.scalar(select(User).options(selectinload(User.profile)).where(User.id == user_id))


def get_user_by_login(db: Session, login: str) -> User | None:
    return db.scalar(
        select(User)
        .options(selectinload(User.profile))
        .where(or_(User.email == login.lower(), User.username == login))
    )


def get_user_by_username(db: Session, username: str) -> User:
    user = db.scalar(
        select(User).options(selectinload(User.profile)).where(User.username == username)
    )
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


def update_profile(db: Session, user: User, data: ProfileUpdate) -> User:
    profile = user.profile or Profile(user_id=user.id, display_name=user.username)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, field, str(value) if field == "avatar_url" and value else value)
    db.add(profile)
    db.commit()
    db.refresh(user)
    return get_user_by_id(db, user.id) or user
