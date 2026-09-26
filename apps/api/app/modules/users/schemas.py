from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=100)
    bio: str | None = Field(default=None, max_length=500)
    avatar_url: HttpUrl | None = None
    location: str | None = Field(default=None, max_length=100)


class ProfileRead(BaseModel):
    display_name: str
    bio: str | None
    avatar_url: str | None
    location: str | None

    model_config = ConfigDict(from_attributes=True)


class UserRead(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime
    profile: ProfileRead

    model_config = ConfigDict(from_attributes=True)


class PublicUserRead(BaseModel):
    id: int
    username: str
    created_at: datetime
    profile: ProfileRead

    model_config = ConfigDict(from_attributes=True)
