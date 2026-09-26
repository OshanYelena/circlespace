from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.modules.users.models import User
from app.modules.users.service import get_user_by_id

bearer = HTTPBearer(auto_error=False)


DatabaseSession = Annotated[Session, Depends(get_db)]
BearerCredentials = Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]


def get_current_user(credentials: BearerCredentials, db: DatabaseSession) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not credentials:
        raise unauthorized
    try:
        user_id = int(decode_access_token(credentials.credentials))
    except (jwt.InvalidTokenError, ValueError) as exc:
        raise unauthorized from exc
    user = get_user_by_id(db, user_id)
    if not user:
        raise unauthorized
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
