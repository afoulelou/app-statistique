from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class DescriptiveResult:
    count: int
    mean: float
    median: float
    modes: list[float]
    variance: float
    standard_deviation: float
    coefficient_of_variation: float | None
    warnings: list[str]


def calculate_descriptive(series: pd.Series) -> DescriptiveResult:
    if not pd.api.types.is_numeric_dtype(series):
        raise ValueError("La variable selectionnee doit etre quantitative.")

    numeric_series = pd.to_numeric(series, errors="coerce").dropna()
    count = len(numeric_series)
    if count == 0:
        raise ValueError("La variable ne contient aucune observation numerique exploitable.")
    if count < 2:
        raise ValueError("Au moins deux observations numeriques sont necessaires.")

    mean = float(numeric_series.mean())
    median = float(numeric_series.median())
    variance = float(numeric_series.var(ddof=1))
    standard_deviation = float(numeric_series.std(ddof=1))
    mode_values = numeric_series.mode().tolist()
    modes = [float(value) for value in mode_values]
    warnings: list[str] = []

    coefficient_of_variation: float | None
    if mean == 0:
        coefficient_of_variation = None
        warnings.append(
            "La moyenne est egale a zero. Le coefficient de variation ne peut pas etre interprete."
        )
    else:
        coefficient_of_variation = float(standard_deviation / mean * 100)

    return DescriptiveResult(
        count=count,
        mean=mean,
        median=median,
        modes=modes,
        variance=variance,
        standard_deviation=standard_deviation,
        coefficient_of_variation=coefficient_of_variation,
        warnings=warnings,
    )


def result_interpretation(result: DescriptiveResult, variable: str) -> dict[str, str]:
    cv_text = (
        f"Le coefficient de variation est de {result.coefficient_of_variation:.2f} %."
        if result.coefficient_of_variation is not None
        else "Le coefficient de variation n'est pas calculable lorsque la moyenne est nulle."
    )
    return {
        "result": (
            f"{variable} : moyenne = {result.mean:.2f}, mediane = {result.median:.2f}, "
            f"ecart-type = {result.standard_deviation:.2f}, N = {result.count}."
        ),
        "interpretation": (
            f"Les observations de {variable} se situent en moyenne autour de {result.mean:.2f}. "
            f"L'ecart-type est de {result.standard_deviation:.2f}."
        ),
        "pedagogical": (
            f"La variance mesure la dispersion au carre autour de la moyenne. {cv_text}"
        ),
    }
