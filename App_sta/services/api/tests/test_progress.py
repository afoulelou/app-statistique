from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.security import create_access_token
from app.db.base import Base
from app.db.models import User
from app.db.session import get_db
from app.main import app

engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base.metadata.create_all(engine)


def override_get_db() -> Generator[Session, None, None]:
    with SessionLocal() as database:
        yield database

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_progress_updates_idempotently_and_is_user_scoped() -> None:
    app.dependency_overrides[get_db] = override_get_db
    database = SessionLocal()
    owner = User(first_name="Progress", last_name="Owner", email="progress-owner@example.com", password_hash="hash")
    other = User(first_name="Other", last_name="User", email="progress-other@example.com", password_hash="hash")
    database.add_all([owner, other])
    database.commit()
    database.close()
    owner_headers = {"Authorization": f"Bearer {create_access_token(owner.id)}"}
    other_headers = {"Authorization": f"Bearer {create_access_token(other.id)}"}

    first = client.put("/progress/ttest", headers=owner_headers, json={"completion": 40, "score": 80})
    assert first.status_code == 200
    second = client.put("/progress/ttest", headers=owner_headers, json={"completion": 100, "score": 90})
    assert second.status_code == 200
    assert second.json()["completion"] == 100

    summary = client.get("/progress", headers=owner_headers)
    assert summary.status_code == 200
    assert summary.json()["methods_started"] == 1
    assert summary.json()["methods_completed"] == 1
    assert len(summary.json()["items"]) == 1

    other_summary = client.get("/progress", headers=other_headers)
    assert other_summary.status_code == 200
    assert other_summary.json()["items"] == []
