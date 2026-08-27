from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DatasetColumnResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    position: int
    data_type: str
    missing_count: int
    unique_count: int


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    file_size_bytes: int
    row_count: int
    column_count: int
    delimiter: str
    encoding: str
    created_at: datetime
    columns: list[DatasetColumnResponse] = Field(default_factory=list)


class DatasetListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    row_count: int
    column_count: int
    created_at: datetime


class DatasetPreviewResponse(BaseModel):
    dataset_id: UUID
    columns: list[str]
    rows: list[dict[str, object]]
    page: int
    page_size: int
    total_rows: int
