from dataclasses import dataclass

import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class TTestResult:
    test_type: str
    sample_sizes: list[int]
    statistic: float
    p_value: float
    degrees_of_freedom: float
    alpha: float
    reject_null: bool
    warnings: list[str]


def _numeric_series(series: pd.Series, label: str) -> pd.Series:
    if not pd.api.types.is_numeric_dtype(series):
        raise ValueError(f"La variable {label} doit etre quantitative pour un test t.")
    result = pd.to_numeric(series, errors="coerce").dropna()
    if len(result) < 2:
        raise ValueError(f"La variable {label} doit contenir au moins deux observations valides.")
    return result


def _decision(statistic: float, p_value: float, degrees_of_freedom: float, test_type: str,
              sample_sizes: list[int], alpha: float) -> TTestResult:
    return TTestResult(
        test_type=test_type,
        sample_sizes=sample_sizes,
        statistic=float(statistic),
        p_value=float(p_value),
        degrees_of_freedom=float(degrees_of_freedom),
        alpha=alpha,
        reject_null=float(p_value) < alpha,
        warnings=[],
    )


def one_sample_ttest(series: pd.Series, population_mean: float, alpha: float = 0.05) -> TTestResult:
    values = _numeric_series(series, "selectionnee")
    result = stats.ttest_1samp(values, popmean=population_mean)
    return _decision(result.statistic, result.pvalue, len(values) - 1, "one_sample", [len(values)], alpha)


def independent_ttest(
    first: pd.Series, second: pd.Series, alpha: float = 0.05
) -> TTestResult:
    first_values = _numeric_series(first, "du groupe 1")
    second_values = _numeric_series(second, "du groupe 2")
    result = stats.ttest_ind(first_values, second_values, equal_var=False)
    return _decision(
        result.statistic,
        result.pvalue,
        result.df,
        "independent",
        [len(first_values), len(second_values)],
        alpha,
    )


def paired_ttest(first: pd.Series, second: pd.Series, alpha: float = 0.05) -> TTestResult:
    if not pd.api.types.is_numeric_dtype(first) or not pd.api.types.is_numeric_dtype(second):
        raise ValueError("Les deux variables appariees doivent etre quantitatives.")
    pairs = pd.concat([first, second], axis=1).apply(pd.to_numeric, errors="coerce").dropna()
    if len(pairs.index) < 2:
        raise ValueError("Au moins deux paires d'observations valides sont necessaires.")
    result = stats.ttest_rel(pairs.iloc[:, 0], pairs.iloc[:, 1])
    return _decision(result.statistic, result.pvalue, len(pairs.index) - 1, "paired", [len(pairs.index)] * 2, alpha)


def ttest_interpretation(result: TTestResult) -> dict[str, str]:
    decision = "rejetee" if result.reject_null else "non rejetee"
    return {
        "result": (
            f"Statistique t = {result.statistic:.3f}, p-value = {result.p_value:.3f}, "
            f"ddl = {result.degrees_of_freedom:.3f}."
        ),
        "interpretation": (
            f"Au seuil de {result.alpha:.0%}, l'hypothese nulle est {decision}."
        ),
        "pedagogical": (
            "Une p-value inferieure au seuil indique une difference statistiquement significative, "
            "sans mesurer a elle seule l'importance pratique de cette difference."
        ),
    }
