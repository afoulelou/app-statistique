import pandas as pd
import pytest

from app.statistics.association import chi_square_test, fisher_exact_test


def test_chi_square_returns_contingency_table_and_expected_frequencies() -> None:
    result = chi_square_test(
        pd.Series(["oui"] * 8 + ["oui"] + ["non"] * 2 + ["non"] * 9),
        pd.Series(["A"] * 8 + ["B"] + ["A"] * 2 + ["B"] * 9),
    )

    assert result.test_type == "chi_square"
    assert result.table == [[2, 9], [8, 1]]
    assert result.degrees_of_freedom == 1
    assert result.statistic == pytest.approx(9.89898989)
    assert result.p_value < 0.01
    assert result.expected_frequencies == [[5.5, 5.5], [4.5, 4.5]]
    assert result.reject_null is True


def test_chi_square_warns_when_expected_counts_are_low() -> None:
    result = chi_square_test(
        pd.Series(["oui", "oui", "non", "non"]),
        pd.Series(["A", "B", "A", "B"]),
    )

    assert result.warnings
    assert "Fisher" in result.warnings[0]


def test_fisher_exact_is_limited_to_two_by_two_tables() -> None:
    result = fisher_exact_test(
        pd.Series(["oui"] * 8 + ["oui"] + ["non"] * 2 + ["non"] * 9),
        pd.Series(["A"] * 8 + ["B"] + ["A"] * 2 + ["B"] * 9),
    )

    assert result.test_type == "fisher"
    assert result.statistic == pytest.approx(1 / 36)
    assert result.p_value == pytest.approx(0.005477, rel=1e-3)

    with pytest.raises(ValueError, match="table 2x2"):
        fisher_exact_test(
            pd.Series(["A", "B", "C", "A", "B", "C"]),
            pd.Series(["X", "X", "X", "Y", "Y", "Y"]),
        )
