from fastapi import APIRouter, Depends, HTTPException

from backend.schemas import UserCreate, UserLogin
from backend.models import User
from backend.security import hash_password, verify_password
from backend.auth import create_access_token
from backend.deps import get_db

from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Cet email est déjà utilisé")

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Utilisateur créé avec succès"}


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user is None:
        raise HTTPException(status_code=400, detail="Utilisateur inconnu")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Mot de passe incorrect")

    token = create_access_token({"sub": db_user.email})
    return {
        "access_token": token,
        "token_type": "bearer"
    }
