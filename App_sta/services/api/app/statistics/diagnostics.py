from dataclasses import dataclass
from typing import cast

import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor


@dataclass(frozen=True)
class VIFResult:
    values: dict[str, float]
    warnings: list[str]


@dataclass(frozen=True)
class BreuschPaganResult:
    lagrange_multiplier: float
    lm_p_value: float
    f_statistic: float
    f_p_value: float
    alpha: float
    reject_null: bool
    warnings: list[str]


def _numeric_design(dataframe: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    if len(columns) < 2:
        raise ValueError("Au moins deux variables explicatives sont necessaires.")
    if len(set(columns)) != len(columns):
        raise ValueError("Les variables explicatives doivent etre distinctes.")
    selected = dataframe[columns]
    if any(not pd.api.types.is_numeric_dtype(selected[column]) for column in columns):
        raise ValueError("Toutes les variables explicatives doivent etre quantitatives.")
    design = selected.apply(pd.to_numeric, errors="coerce").dropna()
    if len(design.index) <= len(columns) + 1:
        raise ValueError("Le nombre d'observations valides doit depasser le nombre de parametres.")
    if design.nunique().lt(2).any():
        raise ValueError("Une variable explicative est constante et ne permet pas le diagnostic.")
    return cast(pd.DataFrame, design)


def calculate_vif(dataframe: pd.DataFrame, columns: list[str]) -> VIFResult:
    design = _numeric_design(dataframe, columns)
    matrix = sm.add_constant(design, has_constant="add")
    values = {
        column: float(variance_inflation_factor(matrix.values, index + 1))
        for index, column in enumerate(columns)
    }
    warnings = [
        f"La variable {column} presente un VIF superieur a 5, ce qui peut indiquer une multicolinearite." 
        for column, value in values.items()
        if value > 5
    ]
    return VIFResult(values=values, warnings=warnings)


def breusch_pagan_test(
    dataframe: pd.DataFrame, dependent_column: str, columns: list[str], alpha: float = 0.05
) -> BreuschPaganResult:
    if dependent_column in columns:
        raise ValueError("La variable dependante doit etre differente des variables explicatives.")
    if not pd.api.types.is_numeric_dtype(dataframe[dependent_column]):
        raise ValueError("La variable dependante doit etre quantitative.")
    design = _numeric_design(dataframe, columns)
    dependent = pd.to_numeric(dataframe[dependent_column], errors="coerce")
    complete = pd.concat([dependent.rename("dependent"), design], axis=1).dropna()
    if len(complete.index) <= len(columns) + 1:
        raise ValueError("Le nombre d'observations completes est insuffisant pour le diagnostic.")
    model = sm.OLS(complete["dependent"], sm.add_constant(complete[columns])).fit()
    lm_stat, lm_p_value, f_statistic, f_p_value = het_breuschpagan(model.resid, model.model.exog)
    return BreuschPaganResult(
        lagrange_multiplier=float(lm_stat),
        lm_p_value=float(lm_p_value),
        f_statistic=float(f_statistic),
        f_p_value=float(f_p_value),
        alpha=alpha,
        reject_null=float(lm_p_value) < alpha,
        warnings=[],
    )


def breusch_pagan_interpretation(result: BreuschPaganResult) -> dict[str, str]:
    decision = "rejetee" if result.reject_null else "non rejetee"
    return {
        "result": (
            f"LM = {result.lagrange_multiplier:.3f}, p-value LM = {result.lm_p_value:.3f}, "
            f"F = {result.f_statistic:.3f}, p-value F = {result.f_p_value:.3f}."
        ),
        "interpretation": (
            f"Au seuil de {result.alpha:.0%}, l'hypothese d'homoscedasticite est {decision}."
        ),
        "pedagogical": (
            "Une p-value faible suggere que la variance des erreurs n'est pas constante. "
            "Des erreurs standards robustes peuvent alors etre envisagees."
        ),
    }
