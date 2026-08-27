from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_content_catalog_exposes_modules_and_method_detail() -> None:
    modules = client.get("/modules")
    assert modules.status_code == 200
    assert {module["id"] for module in modules.json()} == {"descriptive", "inference", "econometrics"}

    method = client.get("/methods/ols")
    assert method.status_code == 200
    assert method.json()["name"] == "Regression lineaire OLS"
    assert len(method.json()["commands"]) == 3


def test_content_returns_404_for_unknown_method() -> None:
    response = client.get("/methods/unknown")
    assert response.status_code == 404
