from dataclasses import dataclass

import pandas as pd
from scipy import stats


@dataclass(frozen=True)
class AnovaResult:
    group_sizes: dict[str, int]
    statistic: float
    p_value: float
    degrees_of_freedom_between: int
    degrees_of_freedom_within: int
    alpha: float
    reject_null: bool
    warnings: list[str]


def calculate_anova(
    values: pd.Series, groups: pd.Series, alpha: float = 0.05
) -> AnovaResult:
    if not pd.api.types.is_numeric_dtype(values):
        raise ValueError("La variable dependante doit etre quantitative.")
    if pd.api.types.is_numeric_dtype(groups):
        raise ValueError("La variable de groupes doit etre qualitative.")

    data = pd.DataFrame({"value": pd.to_numeric(values, errors="coerce"), "group": groups})
    data = data.dropna()
    grouped = [group["value"] for _, group in data.groupby("group", observed=True)]
    if len(grouped) < 2:
        raise ValueError("L'ANOVA necessite au moins deux groupes exploitables.")
    if any(len(group) < 2 for group in grouped):
        raise ValueError("Chaque groupe doit contenir au moins deux observations valides.")

    result = stats.f_oneway(*grouped)
    group_sizes = {str(name): int(len(group)) for name, group in data.groupby("group", observed=True)["value"]}
    group_count = len(grouped)
    observation_count = len(data.index)
    return AnovaResult(
        group_sizes=group_sizes,
        statistic=float(result.statistic),
        p_value=float(result.pvalue),
        degrees_of_freedom_between=group_count - 1,
        degrees_of_freedom_within=observation_count - group_count,
        alpha=alpha,
        reject_null=float(result.pvalue) < alpha,
        warnings=[],
    )


def anova_interpretation(result: AnovaResult) -> dict[str, str]:
    decision = "rejetee" if result.reject_null else "non rejetee"
    return {
        "result": (
            f"Statistique F = {result.statistic:.3f}, p-value = {result.p_value:.3f}, "
            f"ddl = ({result.degrees_of_freedom_between}, {result.degrees_of_freedom_within})."
        ),
        "interpretation": f"Au seuil de {result.alpha:.0%}, l'hypothese d'egalite des moyennes est {decision}.",
        "pedagogical": (
            "Une ANOVA significative indique qu'au moins une moyenne differe des autres. "
            "Elle ne precise pas seule quelles paires de groupes sont differentes ; un test post-hoc sera necessaire."
        ),
    }
