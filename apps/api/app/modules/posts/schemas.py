from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

from app.modules.users.schemas import PublicUserRead


class PostCreate(BaseModel):
    content: str = Field(min_length=1, max_length=2_000)
    image_url: HttpUrl | None = None


class PostUpdate(BaseModel):
    content: str | None = Field(default=None, min_length=1, max_length=2_000)
    image_url: HttpUrl | None = None


class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=500)


class CommentUpdate(BaseModel):
    content: str = Field(min_length=1, max_length=500)


class CommentRead(BaseModel):
    id: int
    author: PublicUserRead
    content: str
    created_at: datetime
    updated_at: datetime


class PostRead(BaseModel):
    id: int
    author: PublicUserRead
    content: str
    image_url: str | None
    created_at: datetime
    updated_at: datetime
    comments: list[CommentRead]
    like_count: int
    share_count: int
    viewer_liked: bool
    viewer_shared: bool


class EngagementRead(BaseModel):
    active: bool
    count: int
