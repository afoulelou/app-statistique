import pandas as pd
import pytest

from app.statistics.ttest import independent_ttest, one_sample_ttest, paired_ttest


def test_one_sample_ttest_returns_expected_statistics() -> None:
    result = one_sample_ttest(pd.Series([4, 5, 6, 7, 8]), population_mean=5)

    assert result.test_type == "one_sample"
    assert result.sample_sizes == [5]
    assert result.degrees_of_freedom == 4
    assert result.statistic == pytest.approx(1.41421356)
    assert result.p_value == pytest.approx(0.2302, rel=1e-3)
    assert result.reject_null is False


def test_independent_ttest_uses_welch_convention() -> None:
    result = independent_ttest(pd.Series([10, 11, 12, 13]), pd.Series([1, 2, 3, 4]))

    assert result.test_type == "independent"
    assert result.sample_sizes == [4, 4]
    assert result.statistic == pytest.approx(9.859006035)
    assert result.p_value < 0.001
    assert result.reject_null is True


def test_paired_ttest_removes_incomplete_pairs() -> None:
    result = paired_ttest(
        pd.Series([10, 12, None, 14]),
        pd.Series([9, 10, 100, 13]),
    )

    assert result.test_type == "paired"
    assert result.sample_sizes == [3, 3]
    assert result.degrees_of_freedom == 2
    assert result.statistic == pytest.approx(4.0)
    assert result.p_value == pytest.approx(0.0571909584, rel=1e-6)


def test_ttest_rejects_non_numeric_variables() -> None:
    with pytest.raises(ValueError, match="quantitative"):
        one_sample_ttest(pd.Series(["A", "B"]), population_mean=0)
