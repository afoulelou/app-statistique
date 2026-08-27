import numpy as np
import pandas as pd
import pytest

from app.statistics.binary_models import estimate_binary_model


def binary_dataframe() -> pd.DataFrame:
    x1 = np.linspace(-2, 2, 40)
    x2 = np.tile([-1.0, 1.0], 20)
    probability = 1 / (1 + np.exp(-(1.2 * x1 + 0.8 * x2)))
    y = (probability > 0.5).astype(int)
    return pd.DataFrame({"y": y, "x1": x1, "x2": x2})


def test_logit_returns_binary_model_diagnostics() -> None:
    result = estimate_binary_model(binary_dataframe(), "y", ["x1", "x2"], "logit")

    assert result.model_type == "logit"
    assert result.observations == 40
    assert len(result.coefficients) == 3
    assert result.coefficients[1].odds_ratio is not None
    assert np.isfinite(result.log_likelihood)
    assert 0 <= result.accuracy <= 1
    assert 0 <= result.sensitivity <= 1
    assert 0 <= result.specificity <= 1
    assert 0 <= result.auc <= 1


def test_probit_returns_binary_model_diagnostics() -> None:
    result = estimate_binary_model(binary_dataframe(), "y", ["x1", "x2"], "probit")

    assert result.model_type == "probit"
    assert result.observations == 40
    assert all(coefficient.odds_ratio is None for coefficient in result.coefficients)
    assert 0 <= result.pseudo_r_squared <= 1


def test_binary_models_reject_invalid_targets_and_designs() -> None:
    dataframe = binary_dataframe()
    dataframe["invalid_y"] = 2
    with pytest.raises(ValueError, match="binaire"):
        estimate_binary_model(dataframe, "invalid_y", ["x1"], "logit")
    with pytest.raises(ValueError, match="differente"):
        estimate_binary_model(dataframe, "y", ["y"], "probit")
    with pytest.raises(ValueError, match="quantitatives"):
        dataframe["category"] = ["A", "B"] * 20
        estimate_binary_model(dataframe, "y", ["category"], "logit")
