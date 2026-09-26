from fastapi import APIRouter, Response, status

from app.modules.auth.dependencies import CurrentUser, DatabaseSession
from app.modules.friendships.schemas import (
    FriendRequestCreate,
    FriendRequestDecision,
    FriendRequestRead,
)
from app.modules.friendships.service import (
    decide_request,
    list_friends,
    list_requests,
    remove_friend,
    send_request,
)
from app.modules.users.schemas import PublicUserRead

router = APIRouter(prefix="/friendships", tags=["friendships"])


@router.post("/requests", response_model=FriendRequestRead, status_code=201)
def create_request(data: FriendRequestCreate, db: DatabaseSession, current_user: CurrentUser):
    return send_request(db, current_user, data.username)


@router.get("/requests/{direction}", response_model=list[FriendRequestRead])
def read_requests(direction: str, db: DatabaseSession, current_user: CurrentUser):
    if direction not in {"sent", "received"}:
        return []
    return list_requests(db, current_user, direction)


@router.patch("/requests/{request_id}", response_model=FriendRequestRead)
def respond_to_request(
    request_id: int,
    data: FriendRequestDecision,
    db: DatabaseSession,
    current_user: CurrentUser,
):
    return decide_request(db, current_user, request_id, data.action)


@router.get("", response_model=list[PublicUserRead])
def read_friends(db: DatabaseSession, current_user: CurrentUser):
    return list_friends(db, current_user)


@router.delete("/{friend_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_friend(friend_id: int, db: DatabaseSession, current_user: CurrentUser) -> Response:
    remove_friend(db, current_user, friend_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
