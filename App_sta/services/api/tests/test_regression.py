import pandas as pd
import pytest

from app.statistics.regression import estimate_ols, ols_interpretation


def test_ols_interpretation_uses_three_decimals() -> None:
    dataframe = pd.DataFrame(
        {
            "y": [3, 5, 7, 9, 11, 13],
            "x": [1, 2, 3, 4, 5, 6],
        }
    )

    result = estimate_ols(dataframe, "y", ["x"])
    interpretation = ols_interpretation(result)

    assert "R2 = 1.000" in interpretation["result"]
    assert "R2 ajuste = 1.000" in interpretation["result"]
    assert "F = 0.000" in interpretation["result"] or "F = 0" not in interpretation["result"]


def test_simple_ols_returns_known_coefficient_and_fit_metrics() -> None:
    dataframe = pd.DataFrame(
        {
            "y": [3, 5, 7, 9, 11, 13],
            "x": [1, 2, 3, 4, 5, 6],
        }
    )

    result = estimate_ols(dataframe, "y", ["x"])

    assert result.observations == 6
    assert [coefficient.name for coefficient in result.coefficients] == ["const", "x"]
    assert result.coefficients[0].coefficient == pytest.approx(1)
    assert result.coefficients[1].coefficient == pytest.approx(2)
    assert result.r_squared == pytest.approx(1)
    assert result.adjusted_r_squared == pytest.approx(1)
    assert result.f_p_value < 0.001


def test_multiple_ols_removes_incomplete_rows() -> None:
    dataframe = pd.DataFrame(
        {
            "y": [10, 14, 18, None, 26, 30],
            "x1": [1, 2, 3, 4, 5, 6],
            "x2": [0, 1, 0, 1, 0, 1],
        }
    )

    result = estimate_ols(dataframe, "y", ["x1", "x2"])

    assert result.observations == 5
    assert len(result.coefficients) == 3
    assert 0 <= result.r_squared <= 1


def test_ols_rejects_invalid_models() -> None:
    dataframe = pd.DataFrame({"y": [1, 2, 3, 4], "x": [1, 1, 1, 1], "group": ["A", "B", "A", "B"]})

    with pytest.raises(ValueError, match="quantitatives"):
        estimate_ols(dataframe, "y", ["group"])
    with pytest.raises(ValueError, match="constante"):
        estimate_ols(dataframe, "y", ["x"])
    with pytest.raises(ValueError, match="differente"):
        estimate_ols(dataframe, "y", ["y"])
