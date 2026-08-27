from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.security import hash_password
from app.db.base import Base
from app.db.models import User
from app.db.session import get_db
from app.main import app


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base.metadata.create_all(engine)


def override_get_db() -> Generator[Session, None, None]:
    with TestingSessionLocal() as database:
        yield database


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_register_login_and_read_profile() -> None:
    register_response = client.post(
        "/auth/register",
        json={
            "first_name": "Awa",
            "last_name": "Diallo",
            "email": "awa@example.com",
            "password": "MotDePasse!123",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/auth/login",
        json={"email": "AWA@example.com", "password": "MotDePasse!123"},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    profile_response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == "awa@example.com"

    refresh_response = client.post(
        "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh_response.status_code == 200
    rotated_tokens = refresh_response.json()
    assert rotated_tokens["refresh_token"] != tokens["refresh_token"]

    revoked_response = client.post(
        "/auth/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert revoked_response.status_code == 401

    logout_response = client.post(
        "/auth/logout", json={"refresh_token": rotated_tokens["refresh_token"]}
    )
    assert logout_response.status_code == 204


def test_invalid_credentials_are_rejected() -> None:
    database = TestingSessionLocal()
    database.execute(
        insert(User).values(
            first_name="Moussa",
            last_name="Ba",
            email="moussa@example.com",
            password_hash=hash_password("Correct!123"),
        )
    )
    database.commit()
    database.close()

    response = client.post(
        "/auth/login",
        json={"email": "moussa@example.com", "password": "Incorrect!123"},
    )
    assert response.status_code == 401

    invalid_refresh_response = client.post(
        "/auth/refresh", json={"refresh_token": "unknown-refresh-token"}
    )
    assert invalid_refresh_response.status_code == 401
