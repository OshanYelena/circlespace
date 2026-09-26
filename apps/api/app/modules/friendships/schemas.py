from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict

from app.modules.users.schemas import PublicUserRead


class FriendRequestAction(str, Enum):
    ACCEPT = "accept"
    REJECT = "reject"


class FriendRequestCreate(BaseModel):
    username: str


class FriendRequestDecision(BaseModel):
    action: FriendRequestAction


class FriendRequestRead(BaseModel):
    id: int
    requester: PublicUserRead
    recipient: PublicUserRead
    status: str
    created_at: datetime
    responded_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
