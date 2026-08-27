from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AnalysisHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    dataset_id: UUID
    analysis_type: str
    dataset_name: str
    parameters: dict[str, object]
    results: dict[str, object]
    engine_version: str
    created_at: datetime
