from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.deps import get_db
from backend.app import db
from backend.app.schemas.schemas import UserCreate, UserOut, Token
from backend.app.core.security import verify_password, get_password_hash, create_access_token
from backend.app.db import models
from backend.app.core.config import settings
import hashlib

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    user = models.User(email=user_in.email, hashed_password=get_password_hash(user_in.password), full_name=user_in.full_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    # create default settings
    settings_obj = models.UserSettings(user_id=user.id)
    db.add(settings_obj)
    db.commit()
    return user

@router.post("/login", response_model=Token)
def login(form_data: UserCreate, db: Session = Depends(get_db)):
    # We accept email & password in JSON (not OAuth2 form) for clarity
    user = db.query(models.User).filter(models.User.email == form_data.email).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")
    access_token = create_access_token(str(user.id))
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    # create refresh token (random)
    refresh_plain = hashlib.sha256((str(user.id) + str(datetime.utcnow())).encode()).hexdigest()
    refresh_hash = get_password_hash(refresh_plain)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    session = models.AuthSession(user_id=user.id, refresh_token_hash=refresh_hash, expires_at=expires_at)
    db.add(session)
    db.commit()
    return {"access_token": access_token, "token_type": "bearer", "expires_in": expires_in, "refresh_token": refresh_plain}

@router.post("/refresh", response_model=Token)
def refresh(token: dict, db: Session = Depends(get_db)):
    # token = {"refresh_token": "..."}
    from passlib.context import CryptContext
    pwd = CryptContext(schemes=["argon2"], deprecated="auto")
    refresh_plain = token.get("refresh_token")
    if not refresh_plain:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing refresh token")
    # find session by matching hash
    sessions = db.query(models.AuthSession).all()
    matched = None
    for s in sessions:
        try:
            if pwd.verify(refresh_plain, s.refresh_token_hash):
                matched = s
                break
        except Exception:
            continue
    if not matched:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if matched.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    # create new access token
    access_token = create_access_token(str(matched.user_id))
    expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    return {"access_token": access_token, "token_type": "bearer", "expires_in": expires_in}

@router.post("/logout")
def logout(token: dict, db: Session = Depends(get_db)):
    refresh_plain = token.get("refresh_token")
    if not refresh_plain:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing refresh token")
    from passlib.context import CryptContext
    pwd = CryptContext(schemes=["argon2"], deprecated="auto")
    sessions = db.query(models.AuthSession).all()
    for s in sessions:
        try:
            if pwd.verify(refresh_plain, s.refresh_token_hash):
                db.delete(s)
                db.commit()
                return {"detail": "logged out"}
        except Exception:
            continue
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")
