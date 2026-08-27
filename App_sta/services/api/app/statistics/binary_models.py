from dataclasses import dataclass
from typing import Literal, cast

import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.metrics import confusion_matrix, roc_auc_score


@dataclass(frozen=True)
class BinaryCoefficient:
    name: str
    coefficient: float
    odds_ratio: float | None
    standard_error: float
    statistic: float
    p_value: float
    confidence_interval_low: float
    confidence_interval_high: float


@dataclass(frozen=True)
class BinaryModelResult:
    model_type: str
    dependent_variable: str
    explanatory_variables: list[str]
    observations: int
    coefficients: list[BinaryCoefficient]
    log_likelihood: float
    null_log_likelihood: float
    lr_statistic: float
    lr_p_value: float
    aic: float
    bic: float
    pseudo_r_squared: float
    accuracy: float
    sensitivity: float
    specificity: float
    auc: float
    warnings: list[str]


def _binary_data(
    dataframe: pd.DataFrame, dependent_column: str, explanatory_columns: list[str]
) -> pd.DataFrame:
    if dependent_column in explanatory_columns:
        raise ValueError("La variable dependante doit etre differente des variables explicatives.")
    if not explanatory_columns or len(set(explanatory_columns)) != len(explanatory_columns):
        raise ValueError("Les variables explicatives doivent etre presentes et distinctes.")
    required = [dependent_column, *explanatory_columns]
    if any(not pd.api.types.is_numeric_dtype(dataframe[column]) for column in required):
        raise ValueError("La variable dependante et les variables explicatives doivent etre quantitatives.")
    complete = dataframe[required].apply(pd.to_numeric, errors="coerce").dropna()
    values = set(complete[dependent_column].unique().tolist())
    if values != {0, 1}:
        raise ValueError("La variable dependante du modele doit etre binaire et coder 0 et 1.")
    if len(complete.index) <= len(explanatory_columns) + 1:
        raise ValueError("Le nombre d'observations valides est insuffisant pour estimer le modele.")
    if complete[explanatory_columns].nunique().lt(2).any():
        raise ValueError("Une variable explicative est constante.")
    return cast(pd.DataFrame, complete)


def estimate_binary_model(
    dataframe: pd.DataFrame,
    dependent_column: str,
    explanatory_columns: list[str],
    model_type: Literal["logit", "probit"],
) -> BinaryModelResult:
    complete = _binary_data(dataframe, dependent_column, explanatory_columns)
    design = sm.add_constant(complete[explanatory_columns], has_constant="add")
    model_class = sm.Logit if model_type == "logit" else sm.Probit
    try:
        model = model_class(complete[dependent_column], design).fit(disp=False, maxiter=200)
    except (np.linalg.LinAlgError, ValueError, TypeError) as error:
        raise ValueError(f"Estimation {model_type} impossible : separation ou matrice singuliere.") from error

    confidence_intervals = model.conf_int()
    coefficients = [
        BinaryCoefficient(
            name=str(name),
            coefficient=float(model.params[name]),
            odds_ratio=float(np.exp(model.params[name])) if model_type == "logit" else None,
            standard_error=float(model.bse[name]),
            statistic=float(model.tvalues[name]),
            p_value=float(model.pvalues[name]),
            confidence_interval_low=float(confidence_intervals.loc[name, 0]),
            confidence_interval_high=float(confidence_intervals.loc[name, 1]),
        )
        for name in model.params.index
    ]
    actual = complete[dependent_column].astype(int)
    probabilities = model.predict(design)
    predicted = (probabilities >= 0.5).astype(int)
    matrix = confusion_matrix(actual, predicted, labels=[0, 1])
    true_negative, false_positive, false_negative, true_positive = matrix.ravel()
    sensitivity = float(true_positive / (true_positive + false_negative)) if true_positive + false_negative else 0.0
    specificity = float(true_negative / (true_negative + false_positive)) if true_negative + false_positive else 0.0
    warnings: list[str] = []
    if model_type == "logit":
        warnings.append("Les coefficients Logit s'interpretent directement avec les odds ratios.")
    return BinaryModelResult(
        model_type=model_type,
        dependent_variable=dependent_column,
        explanatory_variables=explanatory_columns,
        observations=int(model.nobs),
        coefficients=coefficients,
        log_likelihood=float(model.llf),
        null_log_likelihood=float(model.llnull),
        lr_statistic=float(model.llr),
        lr_p_value=float(model.llr_pvalue),
        aic=float(model.aic),
        bic=float(-2 * model.llf + len(model.params) * np.log(model.nobs)),
        pseudo_r_squared=float(model.prsquared),
        accuracy=float((predicted == actual).mean()),
        sensitivity=sensitivity,
        specificity=specificity,
        auc=float(roc_auc_score(actual, probabilities)),
        warnings=warnings,
    )


def binary_model_interpretation(result: BinaryModelResult) -> dict[str, str]:
    return {
        "result": (
            f"Log-vraisemblance = {result.log_likelihood:.3f}, LR = {result.lr_statistic:.3f}, "
            f"p-value LR = {result.lr_p_value:.3f}, AIC = {result.aic:.3f}, BIC = {result.bic:.3f}."
        ),
        "interpretation": (
            f"La precision de classification est de {result.accuracy:.3%}, avec une sensibilite de "
            f"{result.sensitivity:.3%}, une specificite de {result.specificity:.3%} et une AUC de {result.auc:.3f}."
        ),
        "pedagogical": (
            "Le pseudo-R2 ne s'interprete pas comme le R2 d'une regression lineaire. "
            "Les coefficients des modeles binaires doivent etre interpretes avec prudence et ne prouvent pas une causalite."
        ),
    }
