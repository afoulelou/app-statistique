from dataclasses import dataclass
from typing import cast

import pandas as pd
import statsmodels.api as sm


@dataclass(frozen=True)
class CoefficientResult:
    name: str
    coefficient: float
    standard_error: float
    statistic: float
    p_value: float
    confidence_interval_low: float
    confidence_interval_high: float


@dataclass(frozen=True)
class OLSResult:
    dependent_variable: str
    explanatory_variables: list[str]
    observations: int
    coefficients: list[CoefficientResult]
    r_squared: float
    adjusted_r_squared: float
    f_statistic: float
    f_p_value: float
    warnings: list[str]


def _complete_numeric_data(
    dataframe: pd.DataFrame, dependent_column: str, explanatory_columns: list[str]
) -> pd.DataFrame:
    if dependent_column in explanatory_columns:
        raise ValueError("La variable dependante doit etre differente des variables explicatives.")
    if len(explanatory_columns) < 1:
        raise ValueError("Au moins une variable explicative est necessaire.")
    if len(set(explanatory_columns)) != len(explanatory_columns):
        raise ValueError("Les variables explicatives doivent etre distinctes.")
    required_columns = [dependent_column, *explanatory_columns]
    if any(not pd.api.types.is_numeric_dtype(dataframe[column]) for column in required_columns):
        raise ValueError("La variable dependante et les variables explicatives doivent etre quantitatives.")
    complete = dataframe[required_columns].apply(pd.to_numeric, errors="coerce").dropna()
    if len(complete.index) <= len(explanatory_columns) + 1:
        raise ValueError("Le nombre d'observations valides est insuffisant pour estimer le modele.")
    if complete[explanatory_columns].nunique().lt(2).any():
        raise ValueError("Une variable explicative est constante.")
    return cast(pd.DataFrame, complete)


def estimate_ols(
    dataframe: pd.DataFrame, dependent_column: str, explanatory_columns: list[str]
) -> OLSResult:
    complete = _complete_numeric_data(dataframe, dependent_column, explanatory_columns)
    design = sm.add_constant(complete[explanatory_columns], has_constant="add")
    model = sm.OLS(complete[dependent_column], design).fit()
    confidence_intervals = model.conf_int()
    coefficients = [
        CoefficientResult(
            name=str(name),
            coefficient=float(model.params[name]),
            standard_error=float(model.bse[name]),
            statistic=float(model.tvalues[name]),
            p_value=float(model.pvalues[name]),
            confidence_interval_low=float(confidence_intervals.loc[name, 0]),
            confidence_interval_high=float(confidence_intervals.loc[name, 1]),
        )
        for name in model.params.index
    ]
    warnings: list[str] = []
    if float(model.condition_number) > 30:
        warnings.append("Le nombre de condition est eleve ; une multicolinearite peut affecter les coefficients.")
    return OLSResult(
        dependent_variable=dependent_column,
        explanatory_variables=explanatory_columns,
        observations=int(model.nobs),
        coefficients=coefficients,
        r_squared=float(model.rsquared),
        adjusted_r_squared=float(model.rsquared_adj),
        f_statistic=float(model.fvalue),
        f_p_value=float(model.f_pvalue),
        warnings=warnings,
    )


def ols_interpretation(result: OLSResult) -> dict[str, str]:
    return {
        "result": (
            f"R2 = {result.r_squared:.3f}, R2 ajuste = {result.adjusted_r_squared:.3f}, "
            f"F = {result.f_statistic:.3f}, p-value du F-test = {result.f_p_value:.3f}, N = {result.observations}."
        ),
        "interpretation": (
            "Le R2 indique la part de la variabilite de la variable dependante expliquee par les variables du modele. "
            "La p-value du F-test evalue la significativite globale du modele."
        ),
        "pedagogical": (
            "Un coefficient mesure la variation moyenne attendue de la variable dependante lorsque l'explicative augmente d'une unite, "
            "toutes les autres variables restant constantes. Une association estimee ne prouve pas une causalite."
        ),
    }
