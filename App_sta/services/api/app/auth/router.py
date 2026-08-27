from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.auth.dependencies import CurrentUser, Database
from app.auth.schemas import LoginRequest, RefreshRequest, RegisterRequest, TokenResponse, UserResponse
from app.auth.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.db.models import RefreshToken, User

router = APIRouter(prefix="/auth", tags=["auth"])
users_router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, database: Database) -> User:
    email = str(payload.email).lower()
    existing_user = database.scalar(select(User).where(User.email == email))
    if existing_user is not None:
        raise HTTPException(status_code=409, detail="Cette adresse e-mail est deja utilisee.")

    user = User(
        first_name=payload.first_name.strip(),
        last_name=payload.last_name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
    )
    database.add(user)
    database.commit()
    database.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, database: Database) -> TokenResponse:
    email = str(payload.email).lower()
    user = database.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raw_refresh_token, token_hash, expires_at = create_refresh_token()
    database.add(RefreshToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at))
    database.commit()
    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=raw_refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, database: Database) -> TokenResponse:
    stored_token = database.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(payload.refresh_token))
    )
    now = datetime.now(UTC)
    if stored_token is None or stored_token.revoked_at is not None:
        raise HTTPException(status_code=401, detail="Refresh token invalide ou expire.")
    expires_at = stored_token.expires_at
    normalized_expires_at = expires_at.replace(tzinfo=UTC) if expires_at.tzinfo is None else expires_at
    if normalized_expires_at <= now:
        raise HTTPException(status_code=401, detail="Refresh token invalide ou expire.")

    user = database.get(User, stored_token.user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable.")

    stored_token.revoked_at = now
    raw_refresh_token, token_hash, new_expires_at = create_refresh_token()
    database.add(RefreshToken(user_id=user.id, token_hash=token_hash, expires_at=new_expires_at))
    database.commit()
    return TokenResponse(access_token=create_access_token(user.id), refresh_token=raw_refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(payload: RefreshRequest, database: Database) -> None:
    stored_token = database.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == hash_refresh_token(payload.refresh_token))
    )
    if stored_token is not None and stored_token.revoked_at is None:
        stored_token.revoked_at = datetime.now(UTC)
        database.commit()


@users_router.get("/me", response_model=UserResponse)
def read_current_user(current_user: CurrentUser) -> User:
    return current_user
