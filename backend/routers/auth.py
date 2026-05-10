from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth_utils import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    get_password_hash,
    verify_password,
)
from ..config import ADMIN_EMAILS_SET, RATE_LIMIT_AUTH
from ..database import get_db
from ..rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserRead)
@limiter.limit(RATE_LIMIT_AUTH)
def register(request: Request, user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with a hashed password.
    Users whose email appears in ADMIN_EMAILS receive role 'admin'.
    """
    existing_user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    role = "admin" if user_in.email.lower() in ADMIN_EMAILS_SET else "user"

    user = models.User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
@limiter.limit(RATE_LIMIT_AUTH)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Verify user credentials and return JWT access + refresh tokens.
    """
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(user.id)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=schemas.Token)
@limiter.limit(RATE_LIMIT_AUTH)
def refresh_tokens(
    request: Request,
    body: schemas.RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """
    Exchange a valid refresh token for a new access token and rotated refresh token.
    """
    user_id = decode_refresh_token(body.refresh_token)
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh = create_refresh_token(user.id)
    return {
        "access_token": access_token,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }
