from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.auth.dependencies import CurrentUser, Database
from app.datasets.router import owned_dataset
from app.datasets.service import read_dataset
from app.history.service import persist_analysis
from app.statistics.ttest import (
    independent_ttest,
    one_sample_ttest,
    paired_ttest,
    ttest_interpretation,
)
from app.statistics.ttest_schemas import TTestRequest, TTestResponse

router = APIRouter(prefix="/tests", tags=["tests"])


@router.post("/ttest", response_model=TTestResponse)
def student_ttest(
    payload: TTestRequest,
    current_user: CurrentUser,
    database: Database,
) -> TTestResponse:
    dataset = owned_dataset(payload.dataset_id, current_user, database)
    try:
        dataframe = read_dataset(Path(dataset.storage_path), dataset.encoding, dataset.delimiter)
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=f"Lecture du dataset impossible : {error}") from error

    columns = [payload.column, payload.second_column]
    missing_columns = [column for column in columns if column is not None and column not in dataframe.columns]
    if missing_columns:
        raise HTTPException(status_code=422, detail="Une variable selectionnee est introuvable dans le dataset.")

    try:
        if payload.test_type == "one_sample":
            assert payload.column is not None
            assert payload.population_mean is not None
            result = one_sample_ttest(dataframe[payload.column], payload.population_mean, payload.alpha)
            variables = [payload.column]
        elif payload.test_type == "independent":
            assert payload.column is not None and payload.second_column is not None
            result = independent_ttest(dataframe[payload.column], dataframe[payload.second_column], payload.alpha)
            variables = [payload.column, payload.second_column]
        else:
            assert payload.column is not None and payload.second_column is not None
            result = paired_ttest(dataframe[payload.column], dataframe[payload.second_column], payload.alpha)
            variables = [payload.column, payload.second_column]
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    response = TTestResponse(
        dataset_id=dataset.id,
        test_type=result.test_type,
        variables=variables,
        sample_sizes=result.sample_sizes,
        statistic=result.statistic,
        p_value=result.p_value,
        degrees_of_freedom=result.degrees_of_freedom,
        alpha=result.alpha,
        reject_null=result.reject_null,
        warnings=result.warnings,
        interpretation=ttest_interpretation(result),
    )
    persist_analysis(
        database, current_user, dataset, "ttest", payload.model_dump(mode="json"), response.model_dump(mode="json")
    )
    return response
