from typing import Any

from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import AnalysisHistory, Dataset, User
from app.progress.service import mark_method_progress

ANALYSIS_METHOD_IDS = {
    "descriptive": "mean",
}


def persist_analysis(
    database: Session,
    user: User,
    dataset: Dataset,
    analysis_type: str,
    parameters: dict[str, Any],
    results: dict[str, Any],
) -> AnalysisHistory:
    history = AnalysisHistory(
        user_id=user.id,
        dataset_id=dataset.id,
        analysis_type=analysis_type,
        dataset_name=dataset.name,
        parameters=parameters,
        results=results,
        engine_version=settings.api_version,
    )
    database.add(history)
    mark_method_progress(database, user, ANALYSIS_METHOD_IDS.get(analysis_type, analysis_type), 100)
    database.commit()
    database.refresh(history)
    return history
