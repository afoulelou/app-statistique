from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.auth.dependencies import CurrentUser, Database
from app.datasets.router import owned_dataset
from app.datasets.service import read_dataset
from app.history.service import persist_analysis
from app.statistics.binary_models import binary_model_interpretation, estimate_binary_model
from app.statistics.binary_schemas import BinaryCoefficientResponse, BinaryModelRequest, BinaryModelResponse

router = APIRouter(prefix="/models", tags=["models"])


def run_binary_model(
    payload: BinaryModelRequest, current_user: CurrentUser, database: Database
) -> BinaryModelResponse:
    dataset = owned_dataset(payload.dataset_id, current_user, database)
    try:
        dataframe = read_dataset(Path(dataset.storage_path), dataset.encoding, dataset.delimiter)
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=f"Lecture du dataset impossible : {error}") from error

    required_columns = [payload.dependent_column, *payload.explanatory_columns]
    if any(column not in dataframe.columns for column in required_columns):
        raise HTTPException(status_code=422, detail="Une variable selectionnee est introuvable dans le dataset.")
    try:
        result = estimate_binary_model(
            dataframe,
            payload.dependent_column,
            payload.explanatory_columns,
            payload.model_type,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    response = BinaryModelResponse(
        dataset_id=dataset.id,
        model_type=result.model_type,
        dependent_variable=result.dependent_variable,
        explanatory_variables=result.explanatory_variables,
        observations=result.observations,
        coefficients=[BinaryCoefficientResponse(**coefficient.__dict__) for coefficient in result.coefficients],
        log_likelihood=result.log_likelihood,
        null_log_likelihood=result.null_log_likelihood,
        lr_statistic=result.lr_statistic,
        lr_p_value=result.lr_p_value,
        aic=result.aic,
        bic=result.bic,
        pseudo_r_squared=result.pseudo_r_squared,
        accuracy=result.accuracy,
        sensitivity=result.sensitivity,
        specificity=result.specificity,
        auc=result.auc,
        warnings=result.warnings,
        interpretation=binary_model_interpretation(result),
    )
    persist_analysis(
        database,
        current_user,
        dataset,
        result.model_type,
        payload.model_dump(mode="json"),
        response.model_dump(mode="json"),
    )
    return response


@router.post("/logit", response_model=BinaryModelResponse)
def logit_model(
    payload: BinaryModelRequest, current_user: CurrentUser, database: Database
) -> BinaryModelResponse:
    if payload.model_type != "logit":
        raise HTTPException(status_code=422, detail="Ce endpoint attend model_type=logit.")
    return run_binary_model(payload, current_user, database)


@router.post("/probit", response_model=BinaryModelResponse)
def probit_model(
    payload: BinaryModelRequest, current_user: CurrentUser, database: Database
) -> BinaryModelResponse:
    if payload.model_type != "probit":
        raise HTTPException(status_code=422, detail="Ce endpoint attend model_type=probit.")
    return run_binary_model(payload, current_user, database)
