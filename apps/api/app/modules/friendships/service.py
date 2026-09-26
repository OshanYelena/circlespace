from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session, selectinload

from app.modules.friendships.models import FriendRequest, FriendRequestStatus, Friendship
from app.modules.friendships.schemas import FriendRequestAction
from app.modules.users.models import User
from app.modules.users.service import get_user_by_id, get_user_by_username


def _friendship_condition(first_id: int, second_id: int):
    low, high = sorted((first_id, second_id))
    return and_(Friendship.user_low_id == low, Friendship.user_high_id == high)


def _request_query():
    return select(FriendRequest).options(
        selectinload(FriendRequest.requester).selectinload(User.profile),
        selectinload(FriendRequest.recipient).selectinload(User.profile),
    )


def send_request(db: Session, requester: User, username: str) -> FriendRequest:
    recipient = get_user_by_username(db, username)
    if recipient.id == requester.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot friend yourself"
        )
    if db.scalar(select(Friendship).where(_friendship_condition(requester.id, recipient.id))):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already friends")

    pending = db.scalar(
        select(FriendRequest).where(
            FriendRequest.status == FriendRequestStatus.PENDING,
            or_(
                and_(
                    FriendRequest.requester_id == requester.id,
                    FriendRequest.recipient_id == recipient.id,
                ),
                and_(
                    FriendRequest.requester_id == recipient.id,
                    FriendRequest.recipient_id == requester.id,
                ),
            ),
        )
    )
    if pending:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Request already pending")

    friend_request = FriendRequest(requester_id=requester.id, recipient_id=recipient.id)
    db.add(friend_request)
    db.commit()
    return (
        db.scalar(_request_query().where(FriendRequest.id == friend_request.id)) or friend_request
    )


def list_requests(db: Session, user: User, direction: str) -> list[FriendRequest]:
    owner_column = (
        FriendRequest.recipient_id if direction == "received" else FriendRequest.requester_id
    )
    return list(
        db.scalars(
            _request_query()
            .where(owner_column == user.id, FriendRequest.status == FriendRequestStatus.PENDING)
            .order_by(FriendRequest.created_at.desc())
        )
    )


def decide_request(
    db: Session, user: User, request_id: int, action: FriendRequestAction
) -> FriendRequest:
    friend_request = db.scalar(_request_query().where(FriendRequest.id == request_id))
    if not friend_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    if friend_request.recipient_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your request")
    if friend_request.status != FriendRequestStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Request already handled")

    friend_request.responded_at = datetime.now(timezone.utc)
    if action == FriendRequestAction.ACCEPT:
        friend_request.status = FriendRequestStatus.ACCEPTED
        low, high = sorted((friend_request.requester_id, friend_request.recipient_id))
        db.add(Friendship(user_low_id=low, user_high_id=high))
    else:
        friend_request.status = FriendRequestStatus.REJECTED
    db.commit()
    return db.scalar(_request_query().where(FriendRequest.id == request_id)) or friend_request


def list_friends(db: Session, user: User) -> list[User]:
    friendships = db.scalars(
        select(Friendship).where(
            or_(Friendship.user_low_id == user.id, Friendship.user_high_id == user.id)
        )
    )
    friend_ids = [
        item.user_high_id if item.user_low_id == user.id else item.user_low_id
        for item in friendships
    ]
    return [found for friend_id in friend_ids if (found := get_user_by_id(db, friend_id))]


def remove_friend(db: Session, user: User, friend_id: int) -> None:
    friendship = db.scalar(select(Friendship).where(_friendship_condition(user.id, friend_id)))
    if not friendship:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Friendship not found")
    db.delete(friendship)
    db.commit()
