from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.auth.dependencies import CurrentUser, Database
from app.datasets.router import owned_dataset
from app.datasets.service import read_dataset
from app.history.service import persist_analysis
from app.statistics.descriptive import calculate_descriptive, result_interpretation
from app.statistics.schemas import DescriptiveRequest, DescriptiveResponse, InterpretationResponse

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.post("/descriptive", response_model=DescriptiveResponse)
def descriptive_statistics(
    payload: DescriptiveRequest,
    current_user: CurrentUser,
    database: Database,
) -> DescriptiveResponse:
    dataset = owned_dataset(payload.dataset_id, current_user, database)
    try:
        dataframe = read_dataset(Path(dataset.storage_path), dataset.encoding, dataset.delimiter)
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=f"Lecture du dataset impossible : {error}") from error

    if payload.column not in dataframe.columns:
        raise HTTPException(status_code=422, detail="La variable selectionnee est introuvable dans le dataset.")

    try:
        result = calculate_descriptive(dataframe[payload.column])
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    response = DescriptiveResponse(
        dataset_id=dataset.id,
        variable=payload.column,
        count=result.count,
        mean=result.mean,
        median=result.median,
        modes=result.modes,
        variance=result.variance,
        standard_deviation=result.standard_deviation,
        coefficient_of_variation=result.coefficient_of_variation,
        warnings=result.warnings,
        interpretation=InterpretationResponse(**result_interpretation(result, payload.column)),
    )
    persist_analysis(
        database,
        current_user,
        dataset,
        "descriptive",
        payload.model_dump(mode="json"),
        response.model_dump(mode="json"),
    )
    return response
