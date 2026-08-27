from collections.abc import Generator
from datetime import UTC, datetime
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth.security import create_access_token
from app.db.base import Base
from app.db.models import AnalysisHistory, User
from app.db.session import get_db
from app.main import app


engine = create_engine(
    "sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
Base.metadata.create_all(engine)


def override_get_db() -> Generator[Session, None, None]:
    with TestingSessionLocal() as database:
        yield database


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


def test_history_is_scoped_to_the_authenticated_user() -> None:
    app.dependency_overrides[get_db] = override_get_db
    database = TestingSessionLocal()
    owner = User(
        first_name="History", last_name="Owner", email="history-owner@example.com", password_hash="hash"
    )
    other = User(
        first_name="Other", last_name="User", email="history-other@example.com", password_hash="hash"
    )
    database.add_all([owner, other])
    database.flush()
    analysis = AnalysisHistory(
        user_id=owner.id,
        dataset_id=uuid4(),
        analysis_type="descriptive",
        dataset_name="notes.csv",
        parameters={"column": "note"},
        results={"mean": 12.0},
        engine_version="0.1.0",
        created_at=datetime.now(UTC),
    )
    database.add(analysis)
    database.commit()
    analysis_id = analysis.id
    database.close()

    owner_headers = {"Authorization": f"Bearer {create_access_token(owner.id)}"}
    other_headers = {"Authorization": f"Bearer {create_access_token(other.id)}"}

    owner_response = client.get("/analysis/history", headers=owner_headers)
    assert owner_response.status_code == 200
    assert len(owner_response.json()) == 1

    hidden_response = client.get(f"/analysis/history/{analysis_id}", headers=other_headers)
    assert hidden_response.status_code == 404
