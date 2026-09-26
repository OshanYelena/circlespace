from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.modules.auth.schemas import RegisterRequest, TokenResponse
from app.modules.users.models import Profile, User
from app.modules.users.service import get_user_by_id, get_user_by_login


def register(db: Session, data: RegisterRequest) -> TokenResponse:
    existing = db.scalar(
        select(User).where(or_(User.email == data.email.lower(), User.username == data.username))
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or username exists")

    user = User(
        email=data.email.lower(),
        username=data.username,
        hashed_password=hash_password(data.password),
        profile=Profile(display_name=data.display_name),
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email or username exists"
        ) from exc
    db.refresh(user)
    hydrated = get_user_by_id(db, user.id) or user
    return TokenResponse(access_token=create_access_token(str(user.id)), user=hydrated)


def login(db: Session, login_value: str, password: str) -> TokenResponse:
    user = get_user_by_login(db, login_value)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return TokenResponse(access_token=create_access_token(str(user.id)), user=user)
