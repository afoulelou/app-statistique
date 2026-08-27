from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProgressUpdate(BaseModel):
    completion: int = Field(ge=0, le=100)
    score: float | None = Field(default=None, ge=0, le=100)


class ProgressResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    method_id: str
    completion: int
    score: float | None
    updated_at: datetime


class ProgressSummary(BaseModel):
    methods_started: int
    methods_completed: int
    average_completion: float
    global_completion: float
    items: list[ProgressResponse]
    modules: dict[str, float]
