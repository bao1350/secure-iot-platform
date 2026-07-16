import secrets

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from backend.auth import create_access_token, create_refresh_token, decode_token, validate_csrf
from backend.config import ACCESS_TOKEN_EXPIRE_MINUTES, COOKIE_SECURE, REFRESH_TOKEN_EXPIRE_DAYS
from backend.deps import get_db
from backend.models import User
from backend.rate_limit import login_rate_limit, register_rate_limit
from backend.schemas import UserCreate, UserLogin
from backend.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


def set_session_cookies(response: Response, email: str) -> None:
    response.set_cookie(key="access_token", value=create_access_token({"sub": email}), max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60, path="/", httponly=True, secure=COOKIE_SECURE, samesite="none")
    response.set_cookie(key="refresh_token", value=create_refresh_token({"sub": email}), max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400, path="/auth", httponly=True, secure=COOKIE_SECURE, samesite="none")
    response.set_cookie(key="csrf_token", value=secrets.token_urlsafe(32), max_age=REFRESH_TOKEN_EXPIRE_DAYS * 86400, path="/", httponly=False, secure=COOKIE_SECURE, samesite="none")


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db), _: None = Depends(register_rate_limit)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(400, "Cet email est déjà utilisé")
    db.add(User(email=user.email, hashed_password=hash_password(user.password)))
    db.commit()
    return {"message": "Utilisateur créé avec succès"}


@router.post("/login")
def login(
    user: UserLogin,
    response: Response,
    db: Session = Depends(get_db),
    _: None = Depends(login_rate_limit),
):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user is None or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(401, "Identifiants invalides")
    set_session_cookies(response, db_user.email)
    return {"message": "Connexion réussie"}


@router.post("/refresh")
def refresh_session(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    _: None = Depends(validate_csrf),
):
    if not refresh_token:
        raise HTTPException(401, "Session invalide")
    set_session_cookies(response, decode_token(refresh_token, "refresh")["sub"])
    return {"message": "Session renouvelée"}


@router.post("/logout")
def logout(response: Response, _: None = Depends(validate_csrf)):
    response.delete_cookie("access_token", path="/")
    response.delete_cookie("refresh_token", path="/auth")
    response.delete_cookie("csrf_token", path="/")
    return {"message": "Déconnexion réussie"}
