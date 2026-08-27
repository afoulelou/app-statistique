from uuid import UUID

from pydantic import BaseModel, Field


class VIFRequest(BaseModel):
    dataset_id: UUID
    columns: list[str] = Field(min_length=2, max_length=50)


class VIFResponse(BaseModel):
    dataset_id: UUID
    values: dict[str, float]
    warnings: list[str]


class BreuschPaganRequest(BaseModel):
    dataset_id: UUID
    dependent_column: str = Field(min_length=1, max_length=255)
    columns: list[str] = Field(min_length=1, max_length=50)
    alpha: float = Field(default=0.05, gt=0, lt=1)


class BreuschPaganResponse(BaseModel):
    dataset_id: UUID
    dependent_column: str
    columns: list[str]
    lagrange_multiplier: float
    lm_p_value: float
    f_statistic: float
    f_p_value: float
    alpha: float
    reject_null: bool
    warnings: list[str]
    interpretation: dict[str, str]
