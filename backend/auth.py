from datetime import datetime, timedelta, timezone
import hmac

from fastapi import Cookie, Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from backend.config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY
from backend.deps import get_db
from backend.models import User

security = HTTPBearer(auto_error=False)


def _create_token(data: dict, token_type: str, expires_in: timedelta) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + expires_in
    payload["type"] = token_type
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict) -> str:
    return _create_token(data, "access", timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(data: dict) -> str:
    return _create_token(data, "refresh", timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as error:
        raise HTTPException(401, "Session invalide") from error

    if payload.get("type") != expected_type or not payload.get("sub"):
        raise HTTPException(401, "Session invalide")
    return payload


def get_token(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(security)) -> str:
    if credentials:
        return credentials.credentials
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "Session invalide")
    return token


def validate_csrf(
    request: Request,
    csrf_token: str | None = Cookie(default=None),
    x_csrf_token: str | None = Header(default=None),
) -> None:
    if request.headers.get("authorization"):
        return
    if not csrf_token or not x_csrf_token or not hmac.compare_digest(csrf_token, x_csrf_token):
        raise HTTPException(403, "Jeton CSRF invalide")


def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)):
    payload = decode_token(token, "access")
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if user is None:
        raise HTTPException(401, "Session invalide")
    return user
