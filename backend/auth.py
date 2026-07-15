from datetime import datetime, timedelta
import os

from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from dotenv import load_dotenv

from backend.deps import get_db
from backend.models import User

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
except (TypeError, ValueError):
    ACCESS_TOKEN_EXPIRE_MINUTES = 60

security = HTTPBearer()


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    return credentials.credentials


def get_current_user(token: str = Depends(get_token), db: Session = Depends(get_db)):
    exception = HTTPException(status_code=401, detail="Token invalide")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise exception
    except JWTError:
        raise exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise exception

    return user
