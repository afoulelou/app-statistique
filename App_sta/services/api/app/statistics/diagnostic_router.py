from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import APIRouter, HTTPException

from app.auth.dependencies import CurrentUser, Database
from app.datasets.router import owned_dataset
from app.datasets.service import read_dataset
from app.db.models import Dataset
from app.history.service import persist_analysis
from app.statistics.diagnostic_schemas import (
    BreuschPaganRequest,
    BreuschPaganResponse,
    VIFRequest,
    VIFResponse,
)
from app.statistics.diagnostics import (
    breusch_pagan_interpretation,
    breusch_pagan_test,
    calculate_vif,
)

router = APIRouter(prefix="/tests", tags=["tests"])


def dataset_dataframe(dataset_id: Any, current_user: Any, database: Any) -> tuple[Dataset, pd.DataFrame]:
    dataset = owned_dataset(dataset_id, current_user, database)
    try:
        dataframe = read_dataset(Path(dataset.storage_path), dataset.encoding, dataset.delimiter)
    except (OSError, ValueError) as error:
        raise HTTPException(status_code=400, detail=f"Lecture du dataset impossible : {error}") from error
    return dataset, dataframe


@router.post("/vif", response_model=VIFResponse)
def vif_test(payload: VIFRequest, current_user: CurrentUser, database: Database) -> VIFResponse:
    dataset, dataframe = dataset_dataframe(payload.dataset_id, current_user, database)
    missing_columns = [column for column in payload.columns if column not in dataframe.columns]
    if missing_columns:
        raise HTTPException(status_code=422, detail="Une variable selectionnee est introuvable dans le dataset.")
    try:
        result = calculate_vif(dataframe, payload.columns)
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    response = VIFResponse(dataset_id=dataset.id, values=result.values, warnings=result.warnings)
    persist_analysis(
        database, current_user, dataset, "vif", payload.model_dump(mode="json"), response.model_dump(mode="json")
    )
    return response


@router.post("/breusch-pagan", response_model=BreuschPaganResponse)
def breusch_pagan(
    payload: BreuschPaganRequest, current_user: CurrentUser, database: Database
) -> BreuschPaganResponse:
    dataset, dataframe = dataset_dataframe(payload.dataset_id, current_user, database)
    required_columns = [payload.dependent_column, *payload.columns]
    if any(column not in dataframe.columns for column in required_columns):
        raise HTTPException(status_code=422, detail="Une variable selectionnee est introuvable dans le dataset.")
    try:
        result = breusch_pagan_test(
            dataframe, payload.dependent_column, payload.columns, payload.alpha
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    response = BreuschPaganResponse(
        dataset_id=dataset.id,
        dependent_column=payload.dependent_column,
        columns=payload.columns,
        lagrange_multiplier=result.lagrange_multiplier,
        lm_p_value=result.lm_p_value,
        f_statistic=result.f_statistic,
        f_p_value=result.f_p_value,
        alpha=result.alpha,
        reject_null=result.reject_null,
        warnings=result.warnings,
        interpretation=breusch_pagan_interpretation(result),
    )
    persist_analysis(
        database,
        current_user,
        dataset,
        "breusch_pagan",
        payload.model_dump(mode="json"),
        response.model_dump(mode="json"),
    )
    return response
