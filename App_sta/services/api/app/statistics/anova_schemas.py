from uuid import UUID

from pydantic import BaseModel, Field


class AnovaRequest(BaseModel):
    dataset_id: UUID
    value_column: str = Field(min_length=1, max_length=255)
    group_column: str = Field(min_length=1, max_length=255)
    alpha: float = Field(default=0.05, gt=0, lt=1)


class AnovaResponse(BaseModel):
    dataset_id: UUID
    value_variable: str
    group_variable: str
    group_sizes: dict[str, int]
    statistic: float
    p_value: float
    degrees_of_freedom_between: int
    degrees_of_freedom_within: int
    alpha: float
    reject_null: bool
    warnings: list[str]
    interpretation: dict[str, str]
