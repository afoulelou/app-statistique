from collections.abc import Generator
from pathlib import Path

import pandas as pd
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.statistics.descriptive import calculate_descriptive


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


def test_descriptive_uses_sample_conventions_and_supports_multiple_modes() -> None:
    result = calculate_descriptive(pd.Series([1, 2, 2, 3, 3, None]))

    assert result.count == 5
    assert result.mean == pytest.approx(2.2)
    assert result.median == pytest.approx(2.0)
    assert result.modes == [2.0, 3.0]
    assert result.variance == pytest.approx(0.7)
    assert result.standard_deviation == pytest.approx(0.8366600265)
    assert result.coefficient_of_variation == pytest.approx(38.0296, rel=1e-4)


def test_descriptive_warns_when_mean_is_zero() -> None:
    result = calculate_descriptive(pd.Series([-1, 0, 1]))

    assert result.coefficient_of_variation is None
    assert len(result.warnings) == 1


def test_descriptive_rejects_categorical_series() -> None:
    with pytest.raises(ValueError, match="quantitative"):
        calculate_descriptive(pd.Series(["faible", "eleve"]))


def test_descriptive_endpoint_returns_three_interpretation_levels(tmp_path: Path) -> None:
    original_storage_path = settings.dataset_storage_path
    settings.dataset_storage_path = str(tmp_path)
    try:
        register = client.post(
            "/auth/register",
            json={
                "first_name": "Stats",
                "last_name": "Learner",
                "email": "stats-learner@example.com",
                "password": "MotDePasse!123",
            },
        )
        assert register.status_code == 201
        login = client.post(
            "/auth/login",
            json={"email": "stats-learner@example.com", "password": "MotDePasse!123"},
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
        upload = client.post(
            "/datasets",
            headers=headers,
            files={"file": ("notes.csv", "note;groupe\n10;A\n12;A\n14;B\n", "text/csv")},
        )
        assert upload.status_code == 201
        dataset_id = upload.json()["id"]

        response = client.post(
            "/statistics/descriptive",
            headers=headers,
            json={"dataset_id": dataset_id, "column": "note"},
        )
        assert response.status_code == 200
        body = response.json()
        assert body["mean"] == pytest.approx(12)
        assert body["variance"] == pytest.approx(4)
        assert set(body["interpretation"]) == {"result", "interpretation", "pedagogical"}

        history = client.get("/analysis/history", headers=headers)
        assert history.status_code == 200
        assert len(history.json()) == 1
        assert history.json()[0]["analysis_type"] == "descriptive"
        assert history.json()[0]["results"]["mean"] == pytest.approx(12)
        assert history.json()[0]["id"]

        progress = client.get("/progress", headers=headers)
        assert progress.status_code == 200
        assert progress.json()["modules"]["descriptive"] > 0

        invalid = client.post(
            "/statistics/descriptive",
            headers=headers,
            json={"dataset_id": dataset_id, "column": "groupe"},
        )
        assert invalid.status_code == 422
    finally:
        settings.dataset_storage_path = original_storage_path
