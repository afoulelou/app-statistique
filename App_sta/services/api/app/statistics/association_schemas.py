from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class AssociationRequest(BaseModel):
    dataset_id: UUID
    first_column: str = Field(min_length=1, max_length=255)
    second_column: str = Field(min_length=1, max_length=255)
    alpha: float = Field(default=0.05, gt=0, lt=1)
    test_type: Literal["chi_square", "fisher"]


class AssociationResponse(BaseModel):
    dataset_id: UUID
    test_type: str
    variables: list[str]
    table: list[list[int]]
    row_labels: list[str]
    column_labels: list[str]
    statistic: float
    p_value: float
    degrees_of_freedom: int | None
    expected_frequencies: list[list[float]]
    alpha: float
    reject_null: bool
    warnings: list[str]
    interpretation: dict[str, str]
