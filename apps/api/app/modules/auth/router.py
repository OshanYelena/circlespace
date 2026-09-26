from fastapi import APIRouter

from app.modules.auth.dependencies import DatabaseSession
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.modules.auth.service import login, register

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
def register_user(data: RegisterRequest, db: DatabaseSession) -> TokenResponse:
    return register(db, data)


@router.post("/login", response_model=TokenResponse)
def login_user(data: LoginRequest, db: DatabaseSession) -> TokenResponse:
    return login(db, data.login, data.password)
