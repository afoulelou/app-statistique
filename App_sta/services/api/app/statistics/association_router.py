from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.auth.dependencies import CurrentUser, Database
from app.datasets.router import owned_dataset
from app.datasets.service import read_dataset
from app.history.service import persist_analysis
from app.statistics.association import (
    association_interpretation,
    chi_square_test,
    fisher_exact_test,
)
from app.statistics.association_schemas import AssociationRequest, AssociationResponse

router = APIRouter(prefix="/tests", tags=["tests"])


@router.post("/chi-square", response_model=AssociationResponse)
def chi_square(
    payload: AssociationRequest,
    current_user: CurrentUser,
    database: Database,
) -> AssociationResponse:
    if payload.test_type != "chi_square":
        raise HTTPException(status_code=422, detail="Ce endpoint attend test_type=chi_square.")
    return _run_association(payload, current_user, database)


@router.post("/fisher", response_model=AssociationResponse)
def fisher(
    payload: AssociationRequest,
    current_user: CurrentUser,
    database: Database,
) -> AssociationResponse:
    if payload.test_type != "fisher":
        raise HTTPException(status_code=422, detail="Ce endpoint attend test_type=fisher.")
    return _run_association(payload, current_user, database)


def _run_association(
    payload: AssociationRequest,
    current_user: CurrentUser,
    database: Database,
) -> AssociationResponse:
    dataset = owned_dataset(payload.dataset_id, current_user, database)
    try:
        dataframe = read_dataset(Path(dataset.storage_path), dataset.encoding, dataset.delimiter)
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=f"Lecture du dataset impossible : {error}") from error

    if payload.first_column not in dataframe.columns or payload.second_column not in dataframe.columns:
        raise HTTPException(status_code=422, detail="Une variable selectionnee est introuvable dans le dataset.")
    if payload.first_column == payload.second_column:
        raise HTTPException(status_code=422, detail="Les variables doivent etre differentes.")

    try:
        result = (
            chi_square_test(dataframe[payload.first_column], dataframe[payload.second_column], payload.alpha)
            if payload.test_type == "chi_square"
            else fisher_exact_test(dataframe[payload.first_column], dataframe[payload.second_column], payload.alpha)
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    response = AssociationResponse(
        dataset_id=dataset.id,
        test_type=result.test_type,
        variables=[payload.first_column, payload.second_column],
        table=result.table,
        row_labels=result.row_labels,
        column_labels=result.column_labels,
        statistic=result.statistic,
        p_value=result.p_value,
        degrees_of_freedom=result.degrees_of_freedom,
        expected_frequencies=result.expected_frequencies,
        alpha=result.alpha,
        reject_null=result.reject_null,
        warnings=result.warnings,
        interpretation=association_interpretation(result),
    )
    persist_analysis(
        database,
        current_user,
        dataset,
        result.test_type,
        payload.model_dump(mode="json"),
        response.model_dump(mode="json"),
    )
    return response
