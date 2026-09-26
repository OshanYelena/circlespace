from pydantic import BaseModel, EmailStr, Field

from app.modules.users.schemas import UserRead


class RegisterRequest(BaseModel):
    email: EmailStr
    username: str = Field(pattern=r"^[a-zA-Z0-9_]+$", min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=128)
    display_name: str = Field(min_length=1, max_length=100)


class LoginRequest(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
