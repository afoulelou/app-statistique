from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.auth.dependencies import CurrentUser, Database
from app.datasets.router import owned_dataset
from app.datasets.service import read_dataset
from app.history.service import persist_analysis
from app.statistics.anova import anova_interpretation, calculate_anova
from app.statistics.anova_schemas import AnovaRequest, AnovaResponse

router = APIRouter(prefix="/tests", tags=["tests"])


@router.post("/anova", response_model=AnovaResponse)
def anova_test(
    payload: AnovaRequest,
    current_user: CurrentUser,
    database: Database,
) -> AnovaResponse:
    dataset = owned_dataset(payload.dataset_id, current_user, database)
    try:
        dataframe = read_dataset(Path(dataset.storage_path), dataset.encoding, dataset.delimiter)
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=f"Lecture du dataset impossible : {error}") from error

    if payload.value_column not in dataframe.columns or payload.group_column not in dataframe.columns:
        raise HTTPException(status_code=422, detail="Une variable selectionnee est introuvable dans le dataset.")
    if payload.value_column == payload.group_column:
        raise HTTPException(status_code=422, detail="Les variables dependante et de groupes doivent etre differentes.")

    try:
        result = calculate_anova(
            dataframe[payload.value_column], dataframe[payload.group_column], payload.alpha
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    response = AnovaResponse(
        dataset_id=dataset.id,
        value_variable=payload.value_column,
        group_variable=payload.group_column,
        group_sizes=result.group_sizes,
        statistic=result.statistic,
        p_value=result.p_value,
        degrees_of_freedom_between=result.degrees_of_freedom_between,
        degrees_of_freedom_within=result.degrees_of_freedom_within,
        alpha=result.alpha,
        reject_null=result.reject_null,
        warnings=result.warnings,
        interpretation=anova_interpretation(result),
    )
    persist_analysis(
        database, current_user, dataset, "anova", payload.model_dump(mode="json"), response.model_dump(mode="json")
    )
    return response
