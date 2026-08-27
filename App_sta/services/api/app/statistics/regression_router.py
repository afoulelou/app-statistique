from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.auth.dependencies import CurrentUser, Database
from app.datasets.router import owned_dataset
from app.datasets.service import read_dataset
from app.history.service import persist_analysis
from app.statistics.regression import estimate_ols, ols_interpretation
from app.statistics.regression_schemas import CoefficientResponse, OLSRequest, OLSResponse

router = APIRouter(prefix="/models", tags=["models"])


@router.post("/ols", response_model=OLSResponse)
def ols_model(
    payload: OLSRequest,
    current_user: CurrentUser,
    database: Database,
) -> OLSResponse:
    dataset = owned_dataset(payload.dataset_id, current_user, database)
    try:
        dataframe = read_dataset(Path(dataset.storage_path), dataset.encoding, dataset.delimiter)
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=f"Lecture du dataset impossible : {error}") from error

    required_columns = [payload.dependent_column, *payload.explanatory_columns]
    if any(column not in dataframe.columns for column in required_columns):
        raise HTTPException(status_code=422, detail="Une variable selectionnee est introuvable dans le dataset.")
    try:
        result = estimate_ols(dataframe, payload.dependent_column, payload.explanatory_columns)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    response = OLSResponse(
        dataset_id=dataset.id,
        dependent_variable=result.dependent_variable,
        explanatory_variables=result.explanatory_variables,
        observations=result.observations,
        coefficients=[CoefficientResponse(**coefficient.__dict__) for coefficient in result.coefficients],
        r_squared=result.r_squared,
        adjusted_r_squared=result.adjusted_r_squared,
        f_statistic=result.f_statistic,
        f_p_value=result.f_p_value,
        warnings=result.warnings,
        interpretation=ols_interpretation(result),
    )
    persist_analysis(
        database,
        current_user,
        dataset,
        "ols",
        payload.model_dump(mode="json"),
        response.model_dump(mode="json"),
    )
    return response
