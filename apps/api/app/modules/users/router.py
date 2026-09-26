from fastapi import APIRouter

from app.modules.auth.dependencies import CurrentUser, DatabaseSession
from app.modules.users.models import User
from app.modules.users.schemas import ProfileUpdate, PublicUserRead, UserRead
from app.modules.users.service import get_user_by_username, update_profile

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserRead)
def read_me(current_user: CurrentUser) -> User:
    return current_user


@router.patch("/me/profile", response_model=UserRead)
def edit_my_profile(
    data: ProfileUpdate,
    db: DatabaseSession,
    current_user: CurrentUser,
) -> User:
    return update_profile(db, current_user, data)


@router.get("/{username}", response_model=PublicUserRead)
def read_profile(username: str, db: DatabaseSession) -> User:
    return get_user_by_username(db, username)
