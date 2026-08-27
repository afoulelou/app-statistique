from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class BinaryModelRequest(BaseModel):
    dataset_id: UUID
    dependent_column: str = Field(min_length=1, max_length=255)
    explanatory_columns: list[str] = Field(min_length=1, max_length=50)
    model_type: Literal["logit", "probit"]


class BinaryCoefficientResponse(BaseModel):
    name: str
    coefficient: float
    odds_ratio: float | None
    standard_error: float
    statistic: float
    p_value: float
    confidence_interval_low: float
    confidence_interval_high: float


class BinaryModelResponse(BaseModel):
    dataset_id: UUID
    model_type: str
    dependent_variable: str
    explanatory_variables: list[str]
    observations: int
    coefficients: list[BinaryCoefficientResponse]
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
    interpretation: dict[str, str]
