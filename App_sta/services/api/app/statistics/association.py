from dataclasses import dataclass

import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class AssociationResult:
    test_type: str
    table: list[list[int]]
    row_labels: list[str]
    column_labels: list[str]
    statistic: float
    p_value: float
    degrees_of_freedom: int | None
    expected_frequencies: list[list[float]]
    alpha: float
    reject_null: bool
    warnings: list[str]


def _contingency_table(first: pd.Series, second: pd.Series) -> pd.DataFrame:
    if pd.api.types.is_numeric_dtype(first) or pd.api.types.is_numeric_dtype(second):
        raise ValueError("Les deux variables doivent etre qualitatives pour un test d'association.")
    table = pd.crosstab(first, second, dropna=True)
    if table.shape[0] < 2 or table.shape[1] < 2:
        raise ValueError("Les deux variables doivent contenir au moins deux categories.")
    return table


def chi_square_test(first: pd.Series, second: pd.Series, alpha: float = 0.05) -> AssociationResult:
    table = _contingency_table(first, second)
    statistic, p_value, degrees_of_freedom, expected = stats.chi2_contingency(table, correction=False)
    expected_list = expected.tolist()
    warnings: list[str] = []
    small_cells = sum(value < 5 for row in expected_list for value in row)
    if small_cells > 0:
        warnings.append(
            "Les effectifs attendus sont faibles dans certaines cellules. Le test exact de Fisher peut etre recommande pour une table 2x2."
        )
    return AssociationResult(
        test_type="chi_square",
        table=table.astype(int).values.tolist(),
        row_labels=[str(label) for label in table.index],
        column_labels=[str(label) for label in table.columns],
        statistic=float(statistic),
        p_value=float(p_value),
        degrees_of_freedom=int(degrees_of_freedom),
        expected_frequencies=expected_list,
        alpha=alpha,
        reject_null=float(p_value) < alpha,
        warnings=warnings,
    )


def fisher_exact_test(first: pd.Series, second: pd.Series, alpha: float = 0.05) -> AssociationResult:
    table = _contingency_table(first, second)
    if table.shape != (2, 2):
        raise ValueError("Le test exact de Fisher est implemente uniquement pour une table 2x2.")
    odds_ratio, p_value = stats.fisher_exact(table)
    expected = stats.contingency.expected_freq(table).tolist()
    return AssociationResult(
        test_type="fisher",
        table=table.astype(int).values.tolist(),
        row_labels=[str(label) for label in table.index],
        column_labels=[str(label) for label in table.columns],
        statistic=float(odds_ratio),
        p_value=float(p_value),
        degrees_of_freedom=None,
        expected_frequencies=expected,
        alpha=alpha,
        reject_null=float(p_value) < alpha,
        warnings=[],
    )


def association_interpretation(result: AssociationResult) -> dict[str, str]:
    decision = "rejetee" if result.reject_null else "non rejetee"
    test_name = "du Chi-deux" if result.test_type == "chi_square" else "exact de Fisher"
    return {
        "result": f"Test {test_name} : statistique = {result.statistic:.3f}, p-value = {result.p_value:.3f}.",
        "interpretation": f"Au seuil de {result.alpha:.0%}, l'hypothese d'independance est {decision}.",
        "pedagogical": (
            "Une p-value faible suggere une association entre les variables, mais ne prouve pas une relation causale. "
            "Les effectifs attendus doivent etre examines avant d'interpreter le Chi-deux."
        ),
    }
