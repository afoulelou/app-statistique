from uuid import UUID

from pydantic import BaseModel, Field


class DescriptiveRequest(BaseModel):
    dataset_id: UUID
    column: str = Field(min_length=1, max_length=255)


class InterpretationResponse(BaseModel):
    result: str
    interpretation: str
    pedagogical: str


class DescriptiveResponse(BaseModel):
    dataset_id: UUID
    variable: str
    count: int
    mean: float
    median: float
    modes: list[float]
    variance: float
    standard_deviation: float
    coefficient_of_variation: float | None
    warnings: list[str]
    interpretation: InterpretationResponse
