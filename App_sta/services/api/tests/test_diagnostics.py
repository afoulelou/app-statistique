import numpy as np
import pandas as pd
import pytest

from app.statistics.diagnostics import breusch_pagan_test, calculate_vif


def test_vif_returns_one_value_per_explanatory_variable() -> None:
    dataframe = pd.DataFrame(
        {
            "x1": np.arange(1, 21, dtype=float),
            "x2": np.arange(20, 0, -1, dtype=float) + np.tile([0.2, -0.2], 10),
            "x3": np.sin(np.arange(1, 21, dtype=float)),
        }
    )

    result = calculate_vif(dataframe, ["x1", "x2", "x3"])

    assert set(result.values) == {"x1", "x2", "x3"}
    assert all(np.isfinite(value) and value >= 1 for value in result.values.values())


def test_breusch_pagan_returns_both_test_variants() -> None:
    dataframe = pd.DataFrame(
        {
            "y": [2.1, 3.8, 5.2, 6.9, 8.1, 10.2, 12.0, 13.9, 16.2, 18.1],
            "x1": np.arange(1, 11, dtype=float),
            "x2": [0, 1, 0, 1, 0, 1, 0, 1, 0, 1],
        }
    )

    result = breusch_pagan_test(dataframe, "y", ["x1", "x2"])

    assert np.isfinite(result.lagrange_multiplier)
    assert 0 <= result.lm_p_value <= 1
    assert np.isfinite(result.f_statistic)
    assert 0 <= result.f_p_value <= 1
    assert result.alpha == 0.05


def test_diagnostics_reject_invalid_designs() -> None:
    dataframe = pd.DataFrame({"y": [1, 2, 3], "x": [1, 1, 1], "group": ["A", "B", "A"]})

    with pytest.raises(ValueError, match="Au moins deux variables"):
        calculate_vif(dataframe, ["x"])
    with pytest.raises(ValueError, match="quantitatives"):
        calculate_vif(dataframe, ["x", "group"])
    with pytest.raises(ValueError, match="constante"):
        calculate_vif(pd.DataFrame({"x1": [1, 1, 1, 1], "x2": [1, 2, 3, 4]}), ["x1", "x2"])
