from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class TTestRequest(BaseModel):
    dataset_id: UUID
    test_type: Literal["one_sample", "independent", "paired"]
    column: str | None = Field(default=None, min_length=1, max_length=255)
    second_column: str | None = Field(default=None, min_length=1, max_length=255)
    population_mean: float | None = None
    alpha: float = Field(default=0.05, gt=0, lt=1)

    @model_validator(mode="after")
    def validate_parameters(self) -> "TTestRequest":
        if self.test_type == "one_sample" and (self.column is None or self.population_mean is None):
            raise ValueError("Un test a un echantillon necessite une variable et une moyenne de reference.")
        if self.test_type in {"independent", "paired"} and (
            self.column is None or self.second_column is None
        ):
            raise ValueError("Ce test necessite deux variables quantitatives.")
        return self


class TTestResponse(BaseModel):
    dataset_id: UUID
    test_type: str
    variables: list[str]
    sample_sizes: list[int]
    statistic: float
    p_value: float
    degrees_of_freedom: float
    alpha: float
    reject_null: bool
    warnings: list[str]
    interpretation: dict[str, str]
