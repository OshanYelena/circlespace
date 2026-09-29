from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.modules.users.schemas import PublicUserRead


class ArticleCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=20_000)


class ArticleCommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=500)


class ArticleRead(BaseModel):
    id: int
    author: PublicUserRead
    title: str
    content: str
    view_count: int
    like_count: int
    comment_count: int
    created_at: datetime
    updated_at: datetime


class ArticleInteractionRead(BaseModel):
    article_id: int
    count: int
    created: bool = True


class NotificationRead(BaseModel):
    id: int
    type: str
    reference_id: int
    created_at: datetime
    read_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
