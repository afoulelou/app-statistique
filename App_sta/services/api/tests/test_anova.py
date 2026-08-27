import pandas as pd
import pytest

from app.statistics.anova import calculate_anova


def test_anova_returns_f_statistic_and_degrees_of_freedom() -> None:
    result = calculate_anova(
        pd.Series([1, 2, 3, 10, 11, 12, 20, 21, 22]),
        pd.Series(["A", "A", "A", "B", "B", "B", "C", "C", "C"]),
    )

    assert result.group_sizes == {"A": 3, "B": 3, "C": 3}
    assert result.degrees_of_freedom_between == 2
    assert result.degrees_of_freedom_within == 6
    assert result.statistic == pytest.approx(271.0)
    assert result.p_value < 0.001
    assert result.reject_null is True


def test_anova_removes_incomplete_observations() -> None:
    result = calculate_anova(
        pd.Series([1, 2, None, 4, 5, 6]),
        pd.Series(["A", "A", "A", "B", "B", "B"]),
    )

    assert result.group_sizes == {"A": 2, "B": 3}
    assert result.degrees_of_freedom_between == 1
    assert result.degrees_of_freedom_within == 3


def test_anova_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError, match="quantitative"):
        calculate_anova(pd.Series(["A", "B"]), pd.Series(["X", "Y"]))
    with pytest.raises(ValueError, match="qualitative"):
        calculate_anova(pd.Series([1, 2, 3, 4]), pd.Series([1, 1, 2, 2]))
    with pytest.raises(ValueError, match="au moins deux groupes"):
        calculate_anova(pd.Series([1, 2, 3]), pd.Series(["A", "A", "A"]))
