from collections.abc import Generator
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.db.base import Base
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


def auth_headers(email: str, password: str) -> dict[str, str]:
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_upload_preview_and_user_isolation(tmp_path: Path) -> None:
    original_storage_path = settings.dataset_storage_path
    settings.dataset_storage_path = str(tmp_path)
    try:
        register = client.post(
            "/auth/register",
            json={
                "first_name": "Data",
                "last_name": "Owner",
                "email": "owner@example.com",
                "password": "MotDePasse!123",
            },
        )
        assert register.status_code == 201
        owner_headers = auth_headers("owner@example.com", "MotDePasse!123")

        upload = client.post(
            "/datasets",
            headers=owner_headers,
            files={"file": ("enquete.csv", "age;revenu\n25;1200\n;1800\n30;1200\n", "text/csv")},
        )
        assert upload.status_code == 201
        dataset = upload.json()
        assert dataset["row_count"] == 3
        assert dataset["column_count"] == 2
        assert dataset["delimiter"] == ";"
        assert dataset["columns"][0]["name"] == "age"
        assert dataset["columns"][0]["missing_count"] == 1

        preview = client.get(f"/datasets/{dataset['id']}/preview?page_size=2", headers=owner_headers)
        assert preview.status_code == 200
        assert preview.json()["rows"] == [{"age": 25.0, "revenu": 1200}, {"age": None, "revenu": 1800}]

        other_register = client.post(
            "/auth/register",
            json={
                "first_name": "Other",
                "last_name": "User",
                "email": "other@example.com",
                "password": "MotDePasse!123",
            },
        )
        assert other_register.status_code == 201
        other_headers = auth_headers("other@example.com", "MotDePasse!123")
        hidden = client.get(f"/datasets/{dataset['id']}", headers=other_headers)
        assert hidden.status_code == 404
    finally:
        settings.dataset_storage_path = original_storage_path
