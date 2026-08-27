from uuid import UUID

from pydantic import BaseModel, Field


class OLSRequest(BaseModel):
    dataset_id: UUID
    dependent_column: str = Field(min_length=1, max_length=255)
    explanatory_columns: list[str] = Field(min_length=1, max_length=50)


class CoefficientResponse(BaseModel):
    name: str
    coefficient: float
    standard_error: float
    statistic: float
    p_value: float
    confidence_interval_low: float
    confidence_interval_high: float


class OLSResponse(BaseModel):
    dataset_id: UUID
    dependent_variable: str
    explanatory_variables: list[str]
    observations: int
    coefficients: list[CoefficientResponse]
    r_squared: float
    adjusted_r_squared: float
    f_statistic: float
    f_p_value: float
    warnings: list[str]
    interpretation: dict[str, str]
